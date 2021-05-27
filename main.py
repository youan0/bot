from selenium.webdriver import Chrome
import pyttsx3
import os
import json
import time
import re

config = json.load(open("config.json"))
URL = config["URL"]
KEYWORD_USED = config.get("KEYWORD_USED", None)
ASSAY_TYEPS_AVAILABLE = config.get("ASSAY_TYPES_AVAILABLE", None)
ASSAY_TYPE = config.get("ASSAY_TYPE", "BOTH")
REPEAT_AFTER_N_SEC = config.get("REPEAT_AFTER_N_SEC", 6)


class Bot(Chrome):
    def __init__(self, webdriver_name="chromedriver"):
        self.webdriver_name = webdriver_name

    def start_chrome(self):
        """This Function Will Open The Google Chrome Driver"""
        super().__init__(self.webdriver_name)
        self.get(URL)
        self.implicitly_wait(1)
        self.engine = pyttsx3.init()

    def login(self):
        """This Function Will Login To The Website With Your Credentials"""
        if "/users/sign_in" in self.current_url:
            pass
        elif "/users/sign_in" not in self.current_url:
            return True
        else:
            self.get(os.path.join(URL, "users/sign_in"))
        self.implicitly_wait(1)
        # Fill login form
        email = self.find_element_by_name("user[email]")
        password = self.find_element_by_name("user[password]")
        commit = self.find_element_by_name("commit")

        if email and password and commit:
            email.send_keys(config.get("EMAIL", None))
            password.send_keys(config.get("PASSWORD", None))
            commit.submit()
            return True

    def notify_by_sound(self, message):
        """This Function Will Notify By Sound If There's Something New In 1337 Site"""
        try:
            for _ in range(200):
                self.engine.say(message)
                self.engine.runAndWait()
        except:
            self.engine.stop()
            exit(0)

    def exist_in_page_source(self):
        """This Function Will Check If Keywords Is In Page Source"""
        return list(
            filter(lambda KEYWORD: re.search(KEYWORD, self.page_source), KEYWORD_USED)
        )

    def check_for(self, phase):
        """This Function Will Check If any CheckIns/Pools are open"""
        if phase == "check-in" and "meetings" not in self.current_url:
            self.get(os.path.join(URL, "meetings"))
        elif phase == "pool" and "piscines" not in self.current_url:
            self.get(os.path.join(URL, "piscines"))
        self.implicitly_wait(1)
        is_found = len(self.exist_in_page_source()) > 0
        if is_found:
            return True
        return False

    def assay_type(self):
        """This Function Will Setup The Assay Type"""
        ONE_DAY = 1440
        if ASSAY_TYEPS_AVAILABLE.get(ASSAY_TYPE, None) == 0:
            if self.check_for("check-in"):
                self.notify_by_sound(ASSAY_TYPE + " is available")
                time.sleep(ONE_DAY)
        elif ASSAY_TYEPS_AVAILABLE.get(ASSAY_TYPE, None) == 1:
            if self.check_for("pool"):
                self.notify_by_sound(ASSAY_TYPE + " is available")
                time.sleep(ONE_DAY)
        elif ASSAY_TYEPS_AVAILABLE.get(ASSAY_TYPE, None) == 2:
            if self.check_for("check-in") or self.check_for("pool"):
                self.notify_by_sound(ASSAY_TYPE + " is available")
                time.sleep(ONE_DAY)
        else:
            raise KeyError("Assay Type Not Found")


bot = Bot()
bot.start_chrome()
bot.login()

while True:
    try:
        bot.refresh()
        if bot.login():
            bot.assay_type()
        else:
            bot.login()
        time.sleep(REPEAT_AFTER_N_SEC)
    except KeyboardInterrupt:
        print("\rGoodBye :)")
        bot.quit()
        quit()
    except Exception as e:
        print(e)
        bot.quit()
        break
