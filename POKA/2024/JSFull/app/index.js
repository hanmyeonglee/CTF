const puppeteer = require('puppeteer-core');
const crypto = require('crypto');
const cookieParser = require('cookie-parser');
const express = require('express');
const app = express();

let secret = Array.from(crypto.randomBytes(40), byte => byte % 2);
let bot_token = crypto.randomBytes(32).toString('hex');

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

const visit = async (url) => {
    secret = Array.from(crypto.randomBytes(40), byte => byte % 2);
	bot_token = crypto.randomBytes(32).toString('hex');
    let browser;
    try {
        browser = await puppeteer.launch({
            headless: 'new',
			executablePath: '/usr/bin/google-chrome',
			args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--incognito', '--js-flags=--noexpose_wasm,--jitless']
		});
		
        const page = await browser.newPage();
		await page.setCookie({
			name: 'bot_token',
			value: bot_token,
			domain: 'localhost',
			path: '/',
			httpOnly: true,
		});

		await page.goto(url, { timeout: 1000, waitUntil: 'domcontentloaded' });
		await sleep(35000);
		await page.close();
        await browser.close();
        browser = null;
    } catch (err) {
        console.log('bot error', err);
    } finally {
        if (browser) await browser.close();
        secret = Array.from(crypto.randomBytes(40), byte => byte % 2);
		bot_token = crypto.randomBytes(32).toString('hex');
    }
};

app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use((req, res, next) => {
    res.setHeader("Content-Security-Policy", "default-src 'self'; frame-ancestors 'none';");
	res.setHeader("Cross-Origin-Embedder-Policy", "require-corp");
    res.setHeader("Cross-Origin-Opener-Policy", "same-origin");
    res.setHeader("Cross-Origin-Resource-Policy", "same-origin");
    res.setHeader("X-Frame-Options", "deny");
    res.setHeader("X-Content-Type-Options", "nosniff");
    res.setHeader("Cache-Control", "no-store");
    res.setHeader("Document-Policy", "force-load-at-top");
    res.setHeader("Referrer-Policy", "no-referrer");
	
	next();
});

app.get('/', (req, res) => {
	res.send('expresss');
});

app.get('/secret/:index', (req, res) => {
	if (!(/^[0123456789]+$/.test(req.params.index ?? '')))
		return res.send('Invalid index');
	const index = parseInt(req.params.index ?? '');
	if (index < 0 || index >= secret.length)
		return res.send('Invalid index');
	
	if (req.cookies?.bot_token !== bot_token)
		return res.send(index % 2 ? `<img src='/gosu.webp'>` : 'i wanna gosu');
	
	secret[index] = crypto.randomInt(2);
	res.send(secret[index] ? `<img src='/gosu.webp'>` : 'i wanna gosu');
});

app.get('/gosu.webp', (req, res) => {
	res.sendFile(__dirname + '/gosu.webp', (err) => {
		if (err) {
			console.error('file error', err);
			res.send('something wrong');
		}
	});
});

app.get('/flag', (req, res) => {
	if (req.query?.secret !== secret.join(""))
		return res.send('Invalid secret');
	
	res.send(process.env.FLAG ?? 'pokactf2024{test}');
});

app.get('/bot', (req, res) => {
	res.send(`
	<form action="/bot" method="POST">
		report to bot<br>
		<input id="url" name="url" required>
        <button type="submit">Submit</button>
    </form>`);
});

app.post('/bot', (req, res) => {
	const url = req.body.url ?? '';
	if (!url.startsWith('http://') && !url.startsWith('https://'))
		return res.send("use http or https");
	
	visit(url);
	res.send("done");
});

app.listen(30000, () => {
	console.log(`Express server listening on port 30000`);
});