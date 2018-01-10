# Part of the Tidal-Chrome MPRIS bridge
# Author: SERVCUBED 2018-
# License: GPL

import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Driver:

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-sync")
        chrome_options.add_argument("user-data-dir=" + os.path.expanduser("~/.config/tidal-google-chrome/"))
        chrome_options.add_argument("--app=https://listen.tidal.com/")

        print("Starting webdriver")
        self.driver = webdriver.Chrome('chromedriver', chrome_options=chrome_options)

        print("Waiting for load")
        self.driver.implicitly_wait(10)

        print("Started")

    def CanPlay(self):
        return "has-media" in \
               self.driver.find_element_by_class_name("grid").get_property("classList")

    def play(self):
        self.driver.execute_script("arguments[0].click();", self.driver.find_elements_by_class_name("js-play")[-1])

    def pause(self):
        self.driver.execute_script("arguments[0].click();", self.driver.find_elements_by_class_name("js-pause")[-1])

    def next(self):
        self.driver.execute_script("arguments[0].click();", self.driver.find_elements_by_class_name("js-next")[-1])

    def previous(self):
        self.driver.execute_script("arguments[0].click();", self.driver.find_elements_by_class_name("js-previous")[-1])

    def isPlaying(self):
        return "play-controls__main-button--playing" in \
               self.driver.find_element_by_class_name("js-main-button").get_property("classList")

    def isShuffle(self):
        return "active" in \
               self.driver.find_element_by_class_name("js-shuffle").get_property("classList")

    def toggleShuffle(self):
        self.driver.execute_script("arguments[0].click();", self.driver.find_elements_by_class_name("js-shuffle")[-1])

    def currentTrackTitle(self):
        return self.driver.find_element_by_class_name("now-playing__metadata__title").get_property("title")

    def currentTrackArtists(self):
        return ", ".join([x.get_property("title") for x in
                          self.driver.find_element_by_class_name("now-playing__metadata__artist").
                         find_elements_by_tag_name('a')])

    def currentTrackImage(self):
        return self.driver.find_element_by_class_name("js-footer-player-image").get_property("src")

    def currentTrackProgress(self):
        t = self.driver.find_element_by_class_name("js-progress").get_property("innerHTML").split(":")
        return int(t[0]) * 60 + int(t[1]) * 10000000  # Microseconds

    def currentTrackDuration(self):
        t = self.driver.find_element_by_class_name("js-duration").get_property("innerHTML").split(":")
        return int(t[0]) * 60 + int(t[1]) * 10000000  # Microseconds

    def currentLocation(self):
        link = self.driver.find_elements_by_class_name("menu__link--active")
        if len(link) == 0:
            return ""
        return link[0].find_element_by_tag_name("span").get_property("innerHTML")

    def setPosition(self, position):
        el = self.driver.find_element_by_class_name("progressbar__interaction-layer")
        clickxpos = position * el.size["width"] / self.currentTrackDuration()

        action = webdriver.ActionChains(self.driver)
        action.move_to_element_with_offset(el, clickxpos, 5)
        action.click()
        action.perform()

    def raiseWindow(self):
        return self.driver.switch_to.window(self.driver.current_window_handle)

    def setFullscreen(self):
        return self.driver.fullscreen_window()

    def quit(self):
        self.driver.quit()
