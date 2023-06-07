import asyncio
import traceback
from history_tracker import get_history, history_task
from selenium.webdriver.common.keys import Keys
from selgym import *
from stats import *

HEADLESS = False

START_URL = "https://gamdom.com/roulette"

GREEN_BUTTON_XPATH = "/html/body/div[1]/div/div[3]/div/div/div/div[2]/div[3]/div/div[2]/div/div[2]/button"
RED_BUTTON_XPATH = "/html/body/div[1]/div/div[3]/div/div/div/div[2]/div[3]/div/div[1]/div/div[2]/button"
BLACK_BUTTON_XPATH = "/html/body/div[1]/div/div[3]/div/div/div/div[2]/div[3]/div/div[3]/div/div[2]/button"

CLEAR_BET_BUTTON_XPATH = "/html/body/div[1]/div/div[3]/div/div/div/div[2]/div[1]/div/div/div[1]/div/div/div[2]/button"

BET_VALUE_INPUT_XPATH = "/html/body/div[1]/div/div[3]/div/div/div/div[2]/div[1]/div/div/div[1]/div/div/input"

BALANCE_VIEW_XPATH = "/html/body/div[1]/div/div[2]/header/div/div/div[3]/div[2]/div/div[6]/div[2]/div[1]/div/div/div/div"

GREEN_BUTTON_ID = 0
RED_BUTTON_ID = 1
BLACK_BUTTON_ID = 2

BALANCE = None

def green_hunt() -> int:
    print(f"{get_green_distance_count()} >= {max(get_green_distances())} - {get_avg_green_distance()}")
    if get_green_distance_count() >= max(get_green_distances()) - get_avg_green_distance():
        return GREEN_BUTTON_ID
    return -1

def colds_hunt() -> int:
    r,b = 0,0
    s = get_stats_prob()
    k = s.keys()[:4]
    for n in k:
        if n >= 1 and n <= 7:
            r += 1
        elif n >= 8 and n <= 14:
            b += 1
    if b >= r:
        return BLACK_BUTTON_ID
    return RED_BUTTON_ID

def hots_hunt() -> int:
    r,b = 0,0
    s = get_stats_prob()
    k = s.keys()[-4:]
    for n in k:
        if n >= 1 and n <= 7:
            r += 1
        elif n >= 8 and n <= 14:
            b += 1
    if b >= r:
        return BLACK_BUTTON_ID
    return RED_BUTTON_ID

def calculate_bet(history: list[int], mode: int, min_bet: int) -> tuple[int, int]:
    update_stats(history)
    pretty_print_stats()

    bet_amount = min_bet
    button_id = -1

    if mode == 1:
        # Green hunting
        button_id = green_hunt()
    elif mode == 2:
        # Colds Hunt
        button_id = colds_hunt()
    elif mode == 3:
        # Hots Hunt
        button_id = hots_hunt()

    return (bet_amount, button_id)


def is_win(last_bet: int, last_number: int) -> bool:
    _, n = last_bet
    if n == GREEN_BUTTON_ID:
        return last_number == 0
    elif n == RED_BUTTON_ID:
        return last_number >= 1 and last_number <= 7
    elif n == BLACK_BUTTON_ID:
        return last_number >= 8 and last_number <= 14


def bet_click(driver, bet_amount: int, button: int):
    if button not in {GREEN_BUTTON_ID, RED_BUTTON_ID, BLACK_BUTTON_ID}:
        return 0

    clear_btn = wait_element_by(driver, By.XPATH, CLEAR_BET_BUTTON_XPATH)
    click_element(driver, clear_btn)
    inp = wait_element_by(driver, By.XPATH, BET_VALUE_INPUT_XPATH)
    click_element(driver, inp)
    inp.send_keys(Keys.CONTROL, "a")
    inp.send_keys(Keys.BACKSPACE)
    if len(str(bet_amount).split(".")) == 1:
        inp.send_keys(f"{bet_amount}.")
    else:
        inp.send_keys(f"{str(bet_amount)}")

    if button == GREEN_BUTTON_ID:
        btn = wait_element_by(driver, By.XPATH, GREEN_BUTTON_XPATH)
        print(f"\nBetting {bet_amount} on Green")
        click_element(driver, btn)
    elif button == RED_BUTTON_ID:
        btn = wait_element_by(driver, By.XPATH, RED_BUTTON_XPATH)
        print(f"\nBetting {bet_amount} on Red")
        click_element(driver, btn)
    elif button == BLACK_BUTTON_ID:
        btn = wait_element_by(driver, By.XPATH, BLACK_BUTTON_XPATH)
        print(f"\nBetting {bet_amount} on Black")
        click_element(driver, btn)

    return bet_amount


async def bot_task(mode: int, min_bet: float):
    global BALANCE

    if os.name == "posix":
        FIREFOX_PROFILE = linux_default_firefox_profile_path()
    elif os.name == "nt":
        FIREFOX_PROFILE = win_default_firefox_profile_path()
    else:
        print("\nUnrecognized OS")
        return
    opts = get_firefox_options(headless=HEADLESS)
    driver = get_firefox_webdriver(firefox_profile=FIREFOX_PROFILE, options=opts)

    last_bet = (0, -1)
    try:
        driver.get(START_URL)

        history = get_history()
        c = len(history)
        while True:
            try:
                await asyncio.sleep(1)
                history = get_history()
                tmp = len(history)
                if tmp != c:
                    c = tmp
                    BALANCE = wait_element_by(driver, By.XPATH, BALANCE_VIEW_XPATH).text

                    print(f"\n-> {history[-1]}")
                    if last_bet[0] != 0.0:
                        if is_win(last_bet, history[-1]):
                            print("\nRound Won!")
                        else:
                            print("\nRound lost...")
                    bet, btn = calculate_bet(history, mode, min_bet)
                    last_bet = (bet_click(driver, bet, btn), btn)

            except Exception as e:
                traceback.print_exc()
                break
    finally:
        driver.quit()


if __name__ == "__main__":

    MENU = """
    1) Green Hunt
    2) Colds Hunt
    3) Hots Hunt
    >>"""


    async def main():
        c = int(input(MENU))
        if c not in {1, 2}:
            return
        m = int(input("History starting length (max. 500)\n>>").rstrip().lstrip())
        b = input("Minimum Bet amount (min 0.01)\n>>")
        if not b:
            b = 0.01
        b = round(float(b))
        await asyncio.gather(history_task(m), bot_task(c, b))

    asyncio.run(main())
