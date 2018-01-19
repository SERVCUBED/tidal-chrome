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
        chrome_options.add_argument("user-data-dir=" +
                                    os.path.
                                    expanduser(
                                        "~/.config/tidal-google-chrome/"))
        chrome_options.add_argument("--app=https://listen.tidal.com/")

        print("Starting webdriver")
        self.driver = webdriver.Chrome('chromedriver',
                                       chrome_options=chrome_options)

        print("Waiting for load")
        self.driver.implicitly_wait(10)

        print("Started")

    def can_play(self):
        return "has-media" in \
               self.driver.find_element_by_class_name("grid"). \
                   get_property("classList")

    def play(self):
        self.driver.execute_script("arguments[0].click();",
                                   self.driver.
                                   find_elements_by_class_name("js-play")
                                   [-1])

    def pause(self):
        self.driver.execute_script("arguments[0].click();",
                                   self.driver.
                                   find_elements_by_class_name("js-pause")
                                   [-1])

    def next(self):
        self.driver.execute_script("arguments[0].click();",
                                   self.driver.
                                   find_elements_by_class_name("js-next")
                                   [-1])

    def previous(self):
        self.driver.execute_script("arguments[0].click();",
                                   self.driver.
                                   find_elements_by_class_name("js-previous")
                                   [-1])

    def is_playing(self):
        return "play-controls__main-button--playing" in \
               self.driver.find_element_by_class_name("js-main-button"). \
                   get_property("classList")

    def is_shuffle(self):
        return "active" in \
               self.driver.find_element_by_class_name("js-shuffle"). \
                   get_property("classList")

    def toggle_shuffle(self):
        self.driver.execute_script("arguments[0].click();",
                                   self.driver.
                                   find_elements_by_class_name("js-shuffle")
                                   [-1])

    def current_track_title(self):
        return self.driver. \
            find_element_by_class_name("now-playing__metadata__title"). \
            get_property("title")

    def current_track_artists(self):
        return ", ".join([x.get_property("title") for x in
                          self.driver.
                         find_element_by_class_name(
                              "now-playing__metadata__artist").
                         find_elements_by_tag_name('a')])

    def current_track_image(self):
        return self.driver. \
            find_element_by_class_name("js-footer-player-image"). \
            get_property("src")

    def current_track_progress(self):
        t = self.driver.find_element_by_class_name("js-progress"). \
            get_property("innerHTML").split(":")
        return int(t[0]) * 60 + int(t[1]) * 10000000  # Microseconds

    def current_track_duration(self):
        t = self.driver.find_element_by_class_name("js-duration"). \
            get_property("innerHTML").split(":")
        return int(t[0]) * 60 + int(t[1]) * 10000000  # Microseconds

    def current_location(self):
        link = self.driver.find_elements_by_class_name("menu__link--active")
        if len(link) == 0:
            return ""
        return link[0].find_element_by_tag_name("span"). \
            get_property("innerHTML")

    def set_position(self, position):
        el = self.driver. \
            find_element_by_class_name("progressbar__interaction-layer")
        clickxpos = position * el.size["width"] / self.current_track_duration()

        action = webdriver.ActionChains(self.driver)
        action.move_to_element_with_offset(el, clickxpos, 5)
        action.click()
        action.perform()

    def raise_window(self):
        return self.driver.switch_to.window(self.driver.current_window_handle)

    def set_fullscreen(self, value):
        if value:
            self.driver.fullscreen_window()
            self.driver.execute_script("arguments[0].click();",
                                       self.driver.
                                       find_elements_by_class_name(
                                           "js-maximize")[0])

    def open_uri(self, uri):
        if not uri.startswith("tidal://"):
            return

        el = self.driver.find_elements_by_xpath("//*[@id=\"main\"]//a[1]")[-1]
        self.driver.execute_script(
            "arguments[0].href=arguments[1];arguments[0].click();", el,
            uri.replace("tidal://", "/"))

    def quit(self):
        self.driver.quit()
