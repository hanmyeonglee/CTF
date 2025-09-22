const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const { router, protectRoute } = require('./routes/auth');
const notesRouter = require('./routes/notes');
const path = require('path'); 
const User = require('./models/user');

const HOSTNAME = process.env.HOSTNAME ?? 'http://localhost:8000'

const app = express();

// Middleware
app.use(bodyParser.urlencoded({ extended: false }))
app.use(cookieParser());  
app.use((req, res, next) => {
    // Prevent any attack
    res.setHeader('X-Frame-Options', 'DENY');
    res.setHeader('Content-Security-Policy', `script-src ${HOSTNAME}/static/dashboard.js https://js.hcaptcha.com/1/api.js; style-src ${HOSTNAME}/static/; img-src 'none'; connect-src 'self'; media-src 'none'; object-src 'none'; prefetch-src 'none'; frame-ancestors 'none'; form-action 'self'; frame-src 'none';`);
    res.setHeader('Referrer-Policy', 'no-referrer');
    res.setHeader('Cache-Control', 'no-store');
    next();
});


app.use('/api/auth', router);   
app.use('/api/notes', protectRoute, notesRouter);  

app.use(express.static(path.join(__dirname, 'public')));
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));  // Serve the landing page
});

app.get('/login', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'login.html'));  // Serve the login page
});

app.get('/signup', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'signup.html'));  // Serve the signup page
});

app.get('/dashboard', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'dashboard.html'));  // Serve the dashboard page
});

// Serve static files from the 'static' folder
app.get('/static/*splat', (req, res) => {
  const requestedPath = req.path; 

  if (!requestedPath.endsWith('.js') && !requestedPath.endsWith('.css')) {
    return res.redirect(requestedPath.replaceAll('/static',''));
  }

  let file = req.path.slice(req.path.lastIndexOf('/')+1)
  const filePath = path.join(__dirname, 'static', file);
  res.sendFile(filePath);
});

const { spawn } = require('child_process');
app.post('/report', async (req, res) => {
    const noteId = req.body.noteId;

    if(typeof noteId !== 'string'){
        res.status(400).send('Missing noteId');
        return;
    }

    try{
        const admin = await User.findOne().sort({ _id: 1 }).exec();
        const subprocess = spawn('node', ['bot.js', admin.email, admin.password, noteId], {
          detached: true,
          stdio: 'ignore'
        });
        subprocess.unref();
        res.send('Thank you for your report.');
    }catch(e){
        console.log(e);
        res.status(500).send('Error');
    }
});


mongoose.connect(process.env.DB_URI, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log('MongoDB connected'))
  .catch(err => console.log(err));

// Start server
const PORT = process.env.PORT || 8000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});

