from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from replutil import in_repl
from json import loads, dumps
from urllib.parse import urlparse
from multiprocessing import Process
from functools import partial
from time import sleep
from getkey import getkey
from replit import db


# Cookies
def assemble_url(cookie: dict) -> str:
    url: str = ""

    url += "https://" if cookie["secure"] else "http://"

    url += cookie["domain"].lstrip(".")
    url += cookie["path"]

    return url


def save_cookies(driver) -> None:
    print("Saving cookies...", end="")
    for key in [key for key in db.keys() if key.isnumeric()]:
        del db[key]
    for index, value in enumerate(driver.get_cookies()):
        db[str(index)] = dumps(value)
    print("done")


def save_cookies_task(driver) -> None:
    while True:
        sleep(60)
        save_cookies(driver)


# Handle downloads



# Running
if __name__ == "__main__":
    if in_repl():
        # Do keepalive if we have a token
        chrome_options: ChromeOptions = ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')


        driver: Chrome = Chrome(options=chrome_options)

        run_partial: partial = partial(save_cookies_task, driver)
        scp: Process = Process(target=run_partial)
        # handle_downloads_partial: partial = partial()
        # dlp: Process = Process(target=handle_downloads_partial)

        if db.keys():
            print("Loading cookies...", end="")
            for key in sorted([key for key in db.keys() if key.isnumeric()],
                              key=int):
                cookie: dict = loads(db[key])
                url: str = assemble_url(cookie)
                if urlparse(
                        driver.current_url).hostname != urlparse(url).hostname:
                    driver.get(url)
                driver.add_cookie(cookie)
            print("done")

        driver.get("https://google.com")
        driver.find_element(By.NAME, "q").send_keys("ready")

        scp.start()

        print(
            "\033[4m"
            "Done loading! Press Shift+S in this window to save cookies and exit the browser."
            "\033[0m")

        while getkey() != "S":
            continue

        scp.terminate()

        save_cookies(driver)


        driver.close()
    else:
        raise RuntimeError(
            "This script should only be executed in a repl.it container.")
