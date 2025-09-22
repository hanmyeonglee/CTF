const puppeteer = require('puppeteer-core');

function sleep(ms) {
	return new Promise(resolve => setTimeout(resolve, ms));
}

const setupDialogHandler = page => {
	page.on('dialog', async dialog => {
		await dialog.accept();
	});
};

const loginAsAdmin = async page => {
	await page.goto('http://127.0.0.1:3000/login', {
		waitUntil: 'networkidle2'
	});

	await page.type('input[name="email"]', "admin@admin.com");
	await page.type('input[name="password"]', 'fake_password');

	await Promise.all([
		page.click('button[type="submit"]'),
		page.waitForNavigation({ waitUntil: 'networkidle2' })
	]);
};

const visit = async url => {
	let browser;
	try {
		browser = await puppeteer.launch({
			headless: 'new',
			executablePath: '/usr/bin/google-chrome',
			args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
		});

		const page = await browser.newPage();

		setupDialogHandler(page);

		await loginAsAdmin(page);
		await sleep(400);

		await page.evaluate(async () => {
			await fetch('http://127.0.0.1:3000/refresh', {
				method: 'POST',
				credentials: 'include'
			});
		});
		await sleep(400);


		await page.goto(url, {
			timeout: 10000
		});

		await sleep(5000);

		await page.goto('http://127.0.0.1:3000/list', {
			waitUntil: 'networkidle2',
			timeout: 10000
		});
		
		await Promise.all([
			page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 10000 }),
			page.evaluate(() => {
				const f = document.createElement('form');
				f.method = 'POST';
				f.action = 'http://127.0.0.1:3000/memo/delete';
				document.body.appendChild(f);
				setTimeout(() => f.submit(), 0);
				return null;
			})
		]);

		await page.close();
		await browser.close();
		browser = null;
	} catch (err) {
		console.log('error', err);
	} finally {
		if (browser) await browser.close();
	}
};

module.exports = { visit };