const puppeteer = require('puppeteer');
const { generateToken } = require('./jwt')

const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const viewUrl = async (post_id) => {
    const token = generateToken({ uuid: "codegate2025{test_flag}", role: "ADMIN", hasPerm: true })

    const cookies = [{ "name": "jwt", "value": token, "domain": "localhost" }];

    const browser = await puppeteer.launch({
        executablePath: '/usr/bin/chromium',
        args: ["--no-sandbox"]
    });

    let result = true;

    try {
        await browser.setCookie(...cookies);

        const page = await browser.newPage();

        await page.goto(`http://localhost:3000/post/${post_id}`, { timeout: 3000, waitUntil: "domcontentloaded" });

        await delay(1000);

        const button = await page.$('#delete');
        await button.click();

        await delay(1000);
    } catch (error) {
        console.error("An Error occurred:", error);
        result = false;
    } finally {
        await browser.close();
    }

    return result;
};

module.exports = { viewUrl };