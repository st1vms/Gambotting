"""Gamdom trivia bot"""

from re import compile as re_compile
from time import sleep
from random import uniform, choice
from selenium.webdriver import Keys
from selgym.gym import (
    get_firefox_options,
    get_firefox_webdriver,
    wait_element_by,
    wait_elements_by,
    FirefoxWebDriver,
    FirefoxOptions,
    ActionChains,
    WebElement,
    By,
)


def random_sleep(_min: float, _max: float) -> None:
    """Random sleep interval"""
    sleep(round(uniform(_min, _max), 3))


BASE_URL = "https://gamdom.com"

UNDER_ME_REGEX = re_compile(r'^["\']?\$?\s*0?\.\s*5\s*(under ?me)\W*["\']?$')
UNDER_ME_CHARS = "0à+ù36.295"

UNDER_ME_DELAY_MIN = 0.1
UNDER_ME_DELAY_MAX = 0.3

CHAT_UL_XPATH = '//*[@id="chat-messages"]'
CHAT_BOX_CSSS = 'div[role="textbox"]'


class TriviaBot:
    """Gamdom TriviaBot"""

    driver: FirefoxWebDriver = None

    def __init__(self, firefox_profile: str, headless=False):

        self.__gecko_options: FirefoxOptions = get_firefox_options(
            firefox_profile=firefox_profile, headless=headless
        )

    def __is_under_me(self, text: str) -> int:
        """Return underme message index, -1 if no underme"""
        if not bool(UNDER_ME_REGEX.search(text)):
            return -1
        if text.lower().find("2nd") != -1:
            return 1
        if text.lower().find("3rd") != -1:
            return 2
        return 0

    def __get_last_message(self) -> str | None:
        """Retrieves the last message out of chat"""
        messages = wait_element_by(self.driver, By.XPATH, CHAT_UL_XPATH)
        msg = wait_elements_by(messages, By.TAG_NAME, "li")
        if not msg:
            return None
        msg = wait_element_by(msg[-1], By.TAG_NAME, "span")
        if not msg:
            return None
        msg = msg.text.split("\n", maxsplit=3)
        if len(msg) > 1:
            return msg[2].strip()
        if msg:
            return msg[1].strip()
        return None

    def __send_newline(self, actions: ActionChains) -> None:

        actions.key_down(Keys.LEFT_SHIFT).key_down(Keys.ENTER).key_up(
            Keys.ENTER
        ).key_up(Keys.LEFT_SHIFT).perform()

    def __send_chat_message(self, textarea: WebElement, text: str) -> None:
        """Sends text message to chat"""
        actions = ActionChains(self.driver).move_to_element(textarea).click()
        for ch in text:
            if ch == "\n":
                self.__send_newline(actions)
            else:
                actions.send_keys(ch).perform()
        actions.key_down(Keys.ENTER).key_up(Keys.ENTER)

    def __bot_main(self) -> None:
        """Bot main routine"""

        textbox = wait_element_by(self.driver, By.CSS_SELECTOR, CHAT_BOX_CSSS)

        last_msg = None
        last_trivia = None
        ix = -1
        while True:
            msg = self.__get_last_message()
            if msg is None:
                continue

            if last_msg != msg:
                print(msg)
                last_msg = msg

            if last_trivia is None:
                ix = self.__is_under_me(msg)
                if ix == -1:
                    continue
                last_trivia = msg
            elif ix == 0:
                last_trivia = None
                answer = choice(UNDER_ME_CHARS)
                random_sleep(UNDER_ME_DELAY_MIN, UNDER_ME_DELAY_MAX)
                self.__send_chat_message(textbox, answer)
                input("\n\n!!!TRIVIA ANSWERED!!!\n\nPress Enter to continue...")
            ix -= 1

    def start(self) -> None:
        """Start trivia bot webdriver instance"""
        if self.driver:
            self.quit()

        self.driver = get_firefox_webdriver(options=self.__gecko_options)
        try:
            self.driver.get(BASE_URL)
            self.driver.implicitly_wait(10)
            input("\nPress Enter when chat is open...")
            self.__bot_main()
        finally:
            self.quit()

    def quit(self) -> None:
        """Gracefully quit webdriver"""
        if self.driver:
            self.driver.quit()
        self.driver = None


if __name__ == "__main__":
    TriviaBot(headless=True, firefox_profile="/home/st1v/.mozilla/firefox/j2lzzsg2.python").start()
