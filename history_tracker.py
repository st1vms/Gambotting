import asyncio
from selgym import *
import threading

HEADLESS = True

HISTORY: list[int] = list()

MAX_RESULTS = 500

MIN_HASH_LENGTH = 20

ELEMENTS_TABLE_XPATH = "/html/body/div[1]/div/div[3]/div/div/div/div[1]/div[2]/div[2]/div/div/div[2]/div/div/div[2]/div[2]/div[3]/div[2]/div[2]"

LAST_NUMS_TABLE_XPATH = "/html/body/div[1]/div/div[3]/div/div/div/div[1]/div[2]/div[2]/div/div/div[2]/div/div/div[1]/div[2]"

GAME_HISTORY_BUTTON_XPATH = "/html/body/div[1]/div/div[3]/div/div/div/div[1]/div[2]/div[2]/div/div/div[2]/div/div/div[2]/div"

EXIT_HISTORY_BUTTON_XPATH = "/html/body/div[1]/div/div[3]/div/div/div/div[1]/div[2]/div[2]/div/div/div[2]/div/div/div[2]/div[2]/div[3]/div[1]/button"

NUMBER_ELEMENT_TAG_NAME = "a"

LAST_HASH_XPATH = "/html/body/div[1]/div/div[3]/div/div/div/div[1]/div[2]/div[2]/div/div/div[2]/div/div/div[2]/div[2]/div[3]/div[2]/div[2]/div[2]/div[4]/div"

START_URL = "https://gamdom.com/roulette"

LAST_HASH = ""

_LOCK = threading.Lock()


def get_history() -> list[int]:
    global HISTORY
    with _LOCK:
        return HISTORY.copy()


def get_last_number(driver) -> int | None:
    elements = wait_element_by(driver, By.XPATH, ELEMENTS_TABLE_XPATH)
    nums = wait_elements_by(elements, By.TAG_NAME, NUMBER_ELEMENT_TAG_NAME)

    if nums != None and len(nums) > 0:
        return int(nums[0].text)
    return -1


def get_last_hash(driver) -> str:
    return wait_element_by(driver, By.XPATH, LAST_HASH_XPATH).text


def get_visible_history(driver) -> list[int]:
    res = []
    elements = wait_element_by(driver, By.XPATH, ELEMENTS_TABLE_XPATH)
    nums = wait_elements_by(elements, By.TAG_NAME, NUMBER_ELEMENT_TAG_NAME)

    if nums != None and len(nums) > 0:
        for n in nums:
            res.append(int(n.text))

    global LAST_HASH
    LAST_HASH = get_last_hash(driver)

    return res[::-1]


async def crawl_history(driver, max_results: int) -> list[int]:
    histButton = wait_element_by(driver, By.XPATH, GAME_HISTORY_BUTTON_XPATH)
    click_element(driver, histButton)

    timed_out = False
    hist = get_visible_history(driver)
    table = wait_element_by(driver, By.XPATH, ELEMENTS_TABLE_XPATH)
    while len(hist) < max_results:
        try:
            scroll_btn = wait_elements_by(table, By.TAG_NAME, "button")
            driver.execute_script("arguments[0].scrollIntoView();", scroll_btn[-1])
            click_element(driver, scroll_btn[-1])
            hist = get_visible_history(driver)
            print(f"{len(hist)}/{max_results}", end="\r" * 24)
        except KeyboardInterrupt:
            break
        except Exception as e:
            if timed_out:
                break
            timed_out = True
            await asyncio.sleep(1)
            continue

    btn = wait_element_by(driver, By.XPATH, EXIT_HISTORY_BUTTON_XPATH)
    click_element(driver, btn)

    global HISTORY
    with threading.Lock():
        HISTORY = hist
    return hist


async def num_watcher(driver):
    global HISTORY
    global LAST_HASH

    histButton = wait_element_by(driver, By.XPATH, GAME_HISTORY_BUTTON_XPATH)
    click_element(driver, histButton)

    h = ""
    while True:
        try:
            await asyncio.sleep(1)
            n = get_last_number(driver)
            h = get_last_hash(driver)
            if n != -1 and h != LAST_HASH:
                LAST_HASH = h
                with _LOCK:
                    HISTORY.append(n)
        except KeyboardInterrupt:
            break


async def history_task(max_results: int = MAX_RESULTS):
    global HISTORY

    opts = get_firefox_options(headless=HEADLESS)
    driver = get_firefox_webdriver(
        firefox_profile=linux_default_firefox_profile_path(), options=opts
    )

    try:
        driver.get(START_URL)
        print(f"\nCrawling first {max_results} numbers from history...")
        hist = await crawl_history(driver, max_results)
        with _LOCK:
            HISTORY = hist

        print("\nNumber watcher started...")
        await num_watcher(driver)
    finally:
        driver.quit()

if __name__ == "__main__":
    asyncio.run(history_task())
