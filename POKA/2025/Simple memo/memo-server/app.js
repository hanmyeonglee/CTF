const express = require('express');
const bcrypt = require('bcrypt');
const session = require('express-session');
const bodyParser = require('body-parser');
const crypto = require('crypto');
const path = require('path');
const fs = require('fs/promises');
const Busboy = require('busboy');
const FormData = require('form-data')
const axios = require('axios');
const { getConnection } = require('./db');
const { visit } = require('./bot');

const app = express();
const SECRET = crypto.randomBytes(64).toString('hex');

app.use(session({
  secret: SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: { 
    secure: false,
    maxAge: 24 * 60 * 60 * 1000
  }
}));

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.static(path.join(__dirname, 'views')));

function auth(req, res, next) {
  if (!req.session.userId) {
    return res.status(401).json({ error: '로그인이 필요합니다.' });
  }
  req.user = { id: req.session.userId, email: req.session.userEmail };
  next();
}

app.get('/', (req, res) => {
  if (req.session.userId) {
    res.redirect('/list');
  } else {
    res.redirect('/login');
  }
});

app.get('/register', (req, res) => {
  res.sendFile(path.join(__dirname, 'views', 'register.html'));
});

app.post('/register', async (req, res) => {
  const { email, password } = req.body;
  const token = crypto.randomBytes(16).toString('hex');
  const hash = await bcrypt.hash(password, 10);
  try {
    const conn = await getConnection();
    await conn.execute('INSERT INTO users (email, token, password) VALUES (?, ?, ?)', [email, token, hash]);
    await conn.end();
    res.redirect('/login');
  } catch (err) {
    res.status(400).json({ error: '이미 존재하는 이메일입니다.'});
  }
});

app.get('/login', (req, res) => {
  res.sendFile(path.join(__dirname, 'views', 'login.html'));
});

app.post('/login', async (req, res) => {
  const { email, password } = req.body;

  const conn = await getConnection();
  const [rows] = await conn.execute('SELECT * FROM users WHERE email = ?', [email]);
  await conn.end();
  const user = rows[0];
  if (!user) return res.status(400).json({ error: '이메일 또는 비밀번호가 틀렸습니다.' });
  const match = await bcrypt.compare(password, user.password);
  if (!match) return res.status(400).json({ error: '이메일 또는 비밀번호가 틀렸습니다.' });

  req.session.userId = user.id;
  req.session.userEmail = user.email;
  
  res.redirect('/list');
});

app.get('/logout', (req, res) => {
  req.session.destroy((err) => {
    if (err) {
      return res.status(500).json({ error: '로그아웃 오류' });
    }
    res.redirect('/login');
  });
});

app.get('/memo', auth, (req, res) => {
  res.sendFile(path.join(__dirname, 'views', 'write.html'));
});

app.post('/memo', auth, async (req, res) => {
	const ct = req.headers['content-type'] || '';
	const isMultipart = ct.startsWith('multipart/form-data');

	if (!isMultipart) {
		const { title = '', content = '' } = req.body || {};
		if (typeof content !== 'string' || content.length > 20 || title.length > 300) {
			return res.status(400).send('Not Allowed');
		}

		const conn = await getConnection();
		try {
			await conn.beginTransaction();

			const [[{ nextId }]] = await conn.execute(
				'SELECT COALESCE(MAX(memo_id),0) + 1 AS nextId FROM memos WHERE user_id = ? FOR UPDATE',
				[req.user.id]
			);

			await conn.execute(
				'INSERT INTO memos (user_id, memo_id, title, content) VALUES (?, ?, ?, ?)',
				[req.user.id, nextId, title, content]
			);

			await conn.commit();
			return res.redirect(`/memo/${nextId}`);
		} catch (e) {
			await conn.rollback();
			return res.status(500).send('메모 저장 오류');
		} finally {
			await conn.end();
		}
	}

	const busboy = Busboy({ headers: req.headers });
	let title = '';
	let content = '';
	let hasFile = false;
	let fileUploadPromise = null;

	const conn = await getConnection();
	await conn.beginTransaction();

	busboy.on('field', (name, val) => {
		if (name === 'title') title = val;
		if (name === 'content') content = val;
	});

	busboy.on('file', (name, fileStream, fileInfo) => {
		const { filename = '', mimeType } = fileInfo || {};

		if (!filename) {
			fileStream.resume();
			return;
		}

		hasFile = true;

		const formData = new FormData();
		formData.append('file', fileStream, { filename, contentType: mimeType });

		fileUploadPromise = axios.post('http://127.0.0.1:8000/upload', formData, {
			headers: formData.getHeaders(),
			maxBodyLength: Infinity
		});
	});

	busboy.on('finish', async () => {
		try {
			if (typeof content !== 'string' || content.length > 20) {
				await conn.rollback();
				return res.status(400).send('Not Allowed');
			}

			if (hasFile && fileUploadPromise) {
				await fileUploadPromise;  
			}

			const [[{ nextId }]] = await conn.execute(
				'SELECT COALESCE(MAX(memo_id),0) + 1 AS nextId FROM memos WHERE user_id = ? FOR UPDATE',
				[req.user.id]
			);

			await conn.execute(
				'INSERT INTO memos (user_id, memo_id, title, content) VALUES (?, ?, ?, ?)',
				[req.user.id, nextId, title, content]
			);

			await conn.commit();
			return res.redirect(`/memo/${nextId}`);
		} catch (e) {
			await conn.rollback();
			return res.status(500).send('메모 저장 오류');
		} finally {
			await conn.end();
		}
	});

	req.pipe(busboy);
});

app.get('/title', auth, async (req, res) => {
  const conn = await getConnection();
  const [rows] = await conn.execute(
    'SELECT memo_id, title FROM memos WHERE user_id = ? ORDER BY created_at DESC',
    [req.user.id]
  );
  await conn.end();
  res.json(rows);
});

app.get('/list', auth, (req, res) => {
  res.sendFile(path.join(__dirname, 'views', 'list.html'));
});

app.get('/memo/:id', auth, async (req, res) => {
  const memoId = req.params.id;
  let content = ''
  const conn = await getConnection();
  const [rows] = await conn.execute(
    'SELECT content FROM memos WHERE memo_id = ? AND user_id = ?',
    [memoId, req.user.id]
  );
  
  if (rows.length > 0) {
    content = rows[0].content;
  } else {
    return res.send('메모 조회 오류');
  }

  const [rows2] = await conn.execute(
    'SELECT token FROM users WHERE id = ?',
    [req.user.id]
  );
  await conn.end();

  const nonce = rows2[0].token;

  let template = await fs.readFile(
		path.join(__dirname, 'views', 'memo.html'),
		'utf-8'
	);

  const html = template
		.replace(/{{nonce}}/g, nonce)
		.replace('{{memoId}}', memoId)
    .replace('{{content}}', content);
                       
  res.send(html);
});

app.post('/memo/delete', auth, async (req, res) => {
	const conn = await getConnection();
	try {
		await conn.beginTransaction();

		const [result] = await conn.execute('DELETE FROM memos WHERE user_id = ?', [
			req.user.id
		]);

		await conn.commit();

		res.redirect('/list');
	} catch (e) {
		await conn.rollback();
		console.error('메모 삭제 오류:', e);
		res.status(500).send('메모 삭제 오류');
	} finally {
		await conn.end();
	}
});


app.get('/flag', auth, async (req, res) =>{
  if (req.session.userEmail === 'admin@admin.com'){
    res.send('poka{fake_flag}');
  }
  else{
    res.status(403).send('Not Allowed');
  }
});

app.post('/refresh', auth, async(req, res) => {
  if (req.session.userEmail === 'admin@admin.com') {
    const newToken = crypto.randomBytes(16).toString('hex');
    const conn = await getConnection();
    await conn.execute(`UPDATE users SET token = ? WHERE email = ?`, [
			newToken,
			'admin@admin.com'
		]);
		await conn.commit();
    res.send('success!')
	} else {
		res.status(403).send('Not Allowed');
	}
})

app.get('/bot', (req, res) =>{
  res.sendFile(path.join(__dirname, 'views', 'bot.html'));
});

app.post('/bot', async (req, res) => {
	const { url } = req.body;
	if (!url) {
		return res.status(400).send('Enter URL');
	}
	if (!url.startsWith('http://') && !url.startsWith('https://')) {
		return res.status(400).send('Bad URL');
	}
	await visit(url);
	res.send('Complete!');
});

(async () => {
  try {
	await new Promise(resolve => setTimeout(resolve, 5000));
    const conn = await getConnection();
    await conn.ping();
    await conn.end();
    app.listen(3000, () => {
      console.log('Server on 3000 port');
    });
  } catch (err) {
    console.error('DB Error', err);
    process.exit(1);
  }
})(); 