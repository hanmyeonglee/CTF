const puppeteer = require('puppeteer-core');

const TIMEOUT = 10000;
const HOSTNAME = process.env.HOSTNAME ?? 'http://localhost:8000';
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

async function browse(email, password, noteId){
    let browser;
    try{
        browser = await puppeteer.launch({
            headless: "new",
            // pipe: true,
            executablePath: '/usr/bin/chromium',
            ignoreHTTPSErrors: true, 
            acceptInsecureCerts: true,
            args: [
                '--ignore-certificate-errors',
                '--no-sandbox',
                '--disable-gpu',
                "--disable-wasm",
		"--disable-dev-shm-usage",
                '--jitless'
            ]
        });
        await Promise.race([
            sleep(TIMEOUT),
            visit(browser, email, password, noteId),
        ]);
    }catch(e){
        console.error('Failed to browse:', e);
    }finally{
        if(browser){
            try{
                await browser.close();
            }catch(e){
                console.error('Failed to close browser:', e);
            }
        }
    }
}

async function visit(ctx, email, password, noteId){
    page = await ctx.newPage();

    // login
    await page.goto(HOSTNAME + '/login');
    await page.waitForSelector('input[name=email]');
    await page.type('input[name=email]', email);
    await page.waitForSelector('input[name=password]');
    await page.type('input[name=password]', password); 
    await page.waitForSelector('button[type=submit]');
    await page.click('button[type=submit]')

    // Review note
    await sleep(2000);
    try{
        await page.goto(HOSTNAME + '/dashboard?reviewNote='+noteId);
    } catch(error) {
        console.log(error);
    }
    await sleep(2000);
    try{page.close()} catch{};

}

// Get args and navigate 
if (require.main === module) {
  const [email, password, noteId] = process.argv.slice(2);
  if (!email || !password || !noteId) {
    console.error('Usage: node bot.js <email> <password> <noteId>');
    process.exit(1);
  }
  browse(email, password, noteId);
}
