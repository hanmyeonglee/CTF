const express = require('express');
const cookieParser = require('cookie-parser')
const path = require('path');
const crypto = require('crypto');
const app = express();
const port = 3000

const mainRoute = require('./routes/main');
const authRoute = require('./routes/auth');
const userRoute = require('./routes/user');
const postRoute = require('./routes/post');
const adminRoute = require('./routes/admin');
const errorRoute = require('./routes/error');
const reportRoute = require('./routes/report');

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

app.use(express.text());
app.use(express.json());
app.use(cookieParser());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

app.use((req, res, next) => {
    const nonce = crypto.randomBytes(16).toString('hex');

    res.setHeader("X-Frame-Options", "deny");

    if (req.path.startsWith('/admin')) {
        res.setHeader("Content-Security-Policy", `default-src 'self'; script-src 'self' 'unsafe-inline'`);
    } else {
        res.setHeader("Content-Security-Policy", `default-src 'self'; script-src 'nonce-${nonce}'`);
    }

    res.locals.nonce = nonce;

    next();
});

app.use('/', mainRoute);
app.use('/auth', authRoute);
app.use('/user', userRoute);
app.use('/post', postRoute);
app.use('/admin', adminRoute);
app.use('/error', errorRoute);
app.use('/report', reportRoute);


app.listen(port, () => {
    console.log(`Server listening on port ${port}`);
})