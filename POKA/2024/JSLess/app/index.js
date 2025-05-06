const puppeteer = require('puppeteer-core');
const crypto = require('crypto');
const fs = require("fs");
const express = require('express');
const app = express();

if (!(/^pokactf2024\{[a-z]+\}$/.test(process.env.FLAG)))
	throw new Error('Wrong Flag Format');

const SECRET = crypto.randomBytes(16).toString('hex');
fs.writeFile('/secret', SECRET, (err) => { });

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

const visit = async (name) => {
    let browser;
    try {
        browser = await puppeteer.launch({
            headless: 'new',
			executablePath: '/usr/bin/google-chrome',
			args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--incognito', '--js-flags=--noexpose_wasm,--jitless']
		});
		
        const page = await browser.newPage();
		await page.setJavaScriptEnabled(false);
		await page.goto(`http://localhost/index.php?name=${name}`, { timeout: 300, waitUntil: 'domcontentloaded' });
		await sleep(700);
		await page.close();
        await browser.close();
        browser = null;
    } catch (err) {
        console.log('bot error', err);
    } finally {
        if (browser) await browser.close();
    }
};

app.use(express.urlencoded({ extended: false }));
app.use((req, res, next) => {
    res.setHeader("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline';");
	res.setHeader("Cross-Origin-Embedder-Policy", "require-corp");
    res.setHeader("Cross-Origin-Opener-Policy", "same-origin");
    res.setHeader("Cross-Origin-Resource-Policy", "same-origin");
    res.setHeader("X-Frame-Options", "DENY");
    res.setHeader("X-Content-Type-Options", "nosniff");
    res.setHeader("Cache-Control", "no-store");
	
	next();
});

app.get('/', (req, res) => {
	res.send('expresss');
});

app.get('/flag', (req, res) => {
	if (req.query?.secret !== SECRET)
		return res.send('Invalid secret');
	
	const flag = req.connection.remoteAddress === '::ffff:127.0.0.1' ? process.env.FLAG : 'pokactf2024{test}';
	const text = (req.query?.text?.length < 1000) ? (req.query?.text) : '';
	res.send(`<h1 flag="${flag}">${flag}</h1><br>${text ?? 'text'}<br>`);
});

app.get('/bot', (req, res) => {
	res.send(`
	<form action="/bot" method="POST">
		report to bot<br>
		http://localhost/index.php?name=<input id="name" name="name" required>
        <button type="submit">Submit</button>
    </form>`);
});

app.post('/bot', (req, res) => {
	visit(req.body.name);
	res.send("done");
});

app.listen(8080, () => {
	console.log(`Express server listening on port 8080`);
});