import os
import time
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def _origin_of(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


class Bot:
    def __init__(self, headless: bool = True):
        self.admin_username = os.getenv("ADMIN_USERNAME", "admin")
        self.admin_password = os.getenv("ADMIN_PASSWORD", "admin1234")

        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--window-size=1920x1080")

        chrome_bin = os.getenv("CHROME_BIN", "/usr/bin/chromium")
        if os.path.exists(chrome_bin):
            chrome_options.binary_location = chrome_bin

        driver_path = os.getenv("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")
        service = Service(executable_path=driver_path)

        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    def _login_admin(self, origin: str):
        self.driver.get(f"{origin}/login")

        self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
        self.wait.until(EC.presence_of_element_located((By.NAME, "password")))

        self.driver.find_element(By.NAME, "username").clear()
        self.driver.find_element(By.NAME, "username").send_keys(self.admin_username)
        self.driver.find_element(By.NAME, "password").clear()
        self.driver.find_element(By.NAME, "password").send_keys(self.admin_password)

        try:
            self.driver.find_element(By.CSS_SELECTOR, "form button[type=submit]").click()
        except Exception:
            self.driver.find_element(By.CSS_SELECTOR, "form input[type=submit]").click()

        self.wait.until(EC.url_contains(origin))

        try:
            self.driver.get(f"{origin}/api/user")
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "pre")))
        except Exception:
            pass

    def _drop_flag_cookie(self, origin: str):
        self.driver.get(origin + "/")

        self.driver.add_cookie({
            "name": "flag",
            "value": "poka{testflag}",
            "httponly": False,
            "path": "/",
        })

    def visit(self, url: str):
        origin = _origin_of(url)

        self._login_admin(origin)
        self._drop_flag_cookie(origin)

        self.driver.get(url)
        time.sleep(1)
        print(f"[BOT] Visited {url} as admin.")

    def close(self):
        self.driver.quit()

if __name__ == "__main__":
    test_url = os.getenv("TEST_URL", "http://127.0.0.1:7575/")
    b = Bot()
    try:
        b.visit(test_url)
    finally:
        b.close()
