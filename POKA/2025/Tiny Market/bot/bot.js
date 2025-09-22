const puppeteer = require("puppeteer-core");
const express = require("express");
const dotenv = require("dotenv");
const fs = require("fs");
const path = require("path");
const PROFILE_ID = process.env.CHROME_PROFILE_ID || `${Date.now()}`;
const PROFILE_BASE = process.env.CHROME_PROFILE_BASE || "/tmp/chrome-user-data";
const USER_DATA_DIR = path.join(PROFILE_BASE, PROFILE_ID);

fs.mkdirSync(USER_DATA_DIR, { recursive: true });

dotenv.config();

const app = express();
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

app.use(express.json());

let browser;

async function ensureBrowser() {
  if (browser && browser.isConnected()) return browser;

  browser = await puppeteer.launch({
    headless: "new",
    executablePath: "/usr/bin/google-chrome",
    userDataDir: USER_DATA_DIR,
    args: [
      "--no-sandbox",
      "--disable-dev-shm-usage",
      "--disable-gpu",
      "--no-first-run",
      "--no-default-browser-check",
      "--disable-web-security",
    ],
  });

  browser.on("disconnected", () => {
    browser = null;
  });

  let init_page = await browser.newPage();

  await init_page.goto("http://app.local:8080", {
    timeout: 5000,
    waitUntil: "domcontentloaded",
  });

  const pathname = (() => {
    try {
      return new URL(init_page.url()).pathname;
    } catch {
      return "";
    }
  })();

  if (pathname.startsWith("/login")) {
    await init_page.evaluate(
      (ADMIN_EMAIL, ADMIN_PASSWORD) => {
        document.querySelector("#email").value = ADMIN_EMAIL;
        document.querySelector("#password").value = ADMIN_PASSWORD;
        document.querySelector("#login-btn").click();
      },
      process.env.ADMIN_EMAIL,
      process.env.ADMIN_PASSWORD
    );

    await Promise.race([
      init_page
        .waitForNavigation({ waitUntil: "domcontentloaded", timeout: 5000 })
        .catch(() => {}),
      init_page
        .waitForFunction(() => !location.pathname.startsWith("/login"), {
          timeout: 5000,
        })
        .catch(() => {}),
    ]);

    console.log("Bot logged in and session established");
  } else {
    console.log("Session valid; login skipped");
  }

  return browser;
}

app.get("/", async (req, res) => {
  res.sendFile(__dirname + "/index.html");
});

app.post("/visit", async (req, res) => {
  let url = req.body.url;
  let closeAfterMs = Math.max(0, Number(req.body.closeAfterMs ?? 2000));

  if (!url) {
    return res.status(400).json({ error: "url is required" });
  }

  if (
    typeof url !== "string" ||
    url.includes("..") ||
    url.includes("@") ||
    url.includes(";") ||
    url.includes("\0")
  ) {
    return res.status(400).json({ error: "invalid url" });
  }

  if (url.startsWith("/") && !url.startsWith("//")) {
    url = `http://app.local:8080${url}`;
  } else if (!url.startsWith("http://app.local:8080/")) {
    return res.status(400).json({ error: "invalid url" });
  }

  // 60 seconds
  if (closeAfterMs > 60000) {
    return res.status(400).json({ error: "closeAfterMs is too large" });
  }

  const b = await ensureBrowser();

  // Wait for 2 seconds to ensure the browser is ready
  await sleep(2000);

  const new_page = await b.newPage();

  new_page.setDefaultTimeout(5000);

  try {
    await new_page.goto(url, { waitUntil: "domcontentloaded", timeout: 5000 });
    await new_page.waitForTimeout(2000);

    try {
      await new_page.evaluate(() => {
        document.querySelector(`#approve-btn`).click();
      });
    } catch {}

    await new_page.waitForTimeout(closeAfterMs);

    res.status(200).json({ message: "Bot visited the URL" });
  } catch (e) {
    try {
      await b.close();
    } catch {}

    res.status(500).json({ error: "Failed to visit the URL" });
  } finally {
    try {
      await new_page.close({ runBeforeUnload: false });
    } catch {}
  }
});

const server = app.listen(5000, async () => {
  console.log("Bot is running on port 5000");
  console.log("Waiting 3 seconds for services to be ready...");

  setTimeout(async () => {
    try {
      await ensureBrowser();
      console.log("Browser initialized successfully after delay");
    } catch (error) {
      console.log("Browser initialization failed:", error.message);
    }
  }, 3000);
});

process.on("SIGINT", async () => {
  try {
    await browser?.close();
  } finally {
    server.close(() => process.exit(0));
  }
});

process.on("SIGTERM", async () => {
  try {
    await browser?.close();
  } finally {
    server.close(() => process.exit(0));
  }
});
