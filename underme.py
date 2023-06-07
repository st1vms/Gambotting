from selgym import *
from selenium.webdriver.common.keys import Keys
import re
import time
import random
import os

XPATH_WAIT_TIMEOUT = 10

if os.name == "posix":
    FIREFOX_PROFILE = linux_default_firefox_profile_path()
elif os.name == "nt":
    FIREFOX_PROFILE = win_default_firefox_profile_path()
else:
    print("\nUnrecognized OS")
    quit()

CHAT_UL_XPATH = "/html/body/div[1]/div/div[4]/div/div/div/div/div[2]/ul"

CHAT_MSG_CONTENT_CLASS = "MessageSaystyled__ChatUserName"

CHAT_INPUT_XPATH = "/html/body/div[1]/div/div[4]/div/div/div/div/div[4]/div[1]/input"

UNDER_ME_DELAY = 0.35

UNDER_ME_CHARS = "0à+ù36.295"

START_URL = "https://gamdom.com"

UNDER_ME_REGEX = re.compile(r'^["\']?\$?\s*0?\.\s*5\s*(under ?me)\W*["\']?$')


def sendRandomText(driver):
    box = wait_element_by(driver, By.XPATH, CHAT_INPUT_XPATH)
    if box != None:
        box.send_keys(random.choice(list(UNDER_ME_CHARS)))
        box.send_keys(Keys.RETURN)


def process_word(driver, text: str):
    if None != UNDER_ME_REGEX.search(text):
        if text.lower().find("2nd") != -1:
            return 1
        elif text.lower().find("3rd") != -1 or text.lower().find("3d") != -1:
            return 2
        time.sleep(UNDER_ME_DELAY)
        sendRandomText(driver)
        input("\n***UNDER ME***\n")
    return 0


if __name__ == "__main__":
    driver = get_firefox_webdriver(
        firefox_profile=FIREFOX_PROFILE, options=get_firefox_options(headless=True)
    )
    try:
        driver.get(START_URL)
        time.sleep(3)
        chat = wait_element_by(driver, By.XPATH, CHAT_UL_XPATH)
        waitSecond = 0
        lastMessage = ""
        while True:
            try:
                msg = wait_elements_by(chat, By.TAG_NAME, "li")
                if not msg:
                    continue
                msg = wait_element_by(msg[-1], By.TAG_NAME, "span")
                if not msg:
                    continue
            except:
                try:
                    chat = wait_element_by(driver, By.XPATH, CHAT_UL_XPATH)
                except:
                    break
                else:
                    continue
            else:
                if lastMessage != msg.text.split("\n")[-1]:
                    lastMessage = msg.text.split("\n")[-1]
                    scroll_element_to_bottom(driver, chat)
                    print(lastMessage)

                    if waitSecond - 1 == 0:
                        sendRandomText(driver)
                        waitSecond = 0
                    elif waitSecond >= 1:
                        waitSecond -= 1
                        continue

                    waitSecond = process_word(driver, lastMessage)
    finally:
        driver.close()
