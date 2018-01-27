# Part of the Tidal-Chrome MPRIS bridge
# Author: SERVCUBED 2018-
# License: AGPL

import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Driver:

    def __init__(self):
        """
        Creates a new instance of the TIDAL-Chrome driver, opens a browser
        window and navigates to TIDAL.

        The browser's data directory is set to:
            ~/.config/tidal-google-chrome/
        """
        chrome_options = Options()
        chrome_options.add_argument("--disable-sync")
        chrome_options.add_argument("user-data-dir=" +
                                    os.path.
                                    expanduser(
                                        "~/.config/tidal-google-chrome/"))
        chrome_options.add_argument("--app=https://listen.tidal.com/")

        print("Starting webdriver")
        self._driver = webdriver.Chrome('chromedriver',
                                        chrome_options=chrome_options)

        print("Waiting for load")
        self._driver.implicitly_wait(10)

        print("Started")

    def can_play(self) -> bool:
        """
        Get whether the player can play, pause, seek.
        :return: True if the player can play, pause, seek
        """
        return "has-media" in \
               self._driver.find_element_by_class_name("grid"). \
               get_property("classList")

    def play(self) -> None:
        """
        Play the current track.
        :return: Nothing
        """
        self._driver.execute_script("arguments[0].click();",
                                    self._driver.
                                    find_elements_by_class_name("js-play")
                                    [-1])

    def pause(self) -> None:
        """
        Pause the current track.
        :return: Nothing
        """
        self._driver.execute_script("arguments[0].click();",
                                    self._driver.
                                    find_elements_by_class_name("js-pause")
                                    [-1])

    def next(self) -> None:
        """
        Play the next track, if available.
        :return: Nothing
        """
        self._driver.execute_script("arguments[0].click();",
                                    self._driver.
                                    find_elements_by_class_name("js-next")
                                    [-1])

    def previous(self) -> None:
        """
        Play the previous track, if available.
        :return: Nothing
        """
        self._driver.execute_script("arguments[0].click();",
                                    self._driver.
                                    find_elements_by_class_name("js-previous")
                                    [-1])

    def is_playing(self) -> bool:
        """
        Gets whether the player is currently playing.
        :return: True if the player is currently playing.
        """
        return "play-controls__main-button--playing" in \
            self._driver.find_element_by_class_name("js-main-button"). \
            get_property("classList")

    def is_shuffle(self) -> bool:
        """
        Gets whether shuffle is currently enabled.
        :return: True if shuffle is currently enabled.
        """
        return "active" in \
            self._driver.find_element_by_class_name("js-shuffle"). \
            get_property("classList")

    def toggle_shuffle(self) -> None:
        """
        Toggle the shuffle status.
        :return: Nothing
        """
        self._driver.execute_script("arguments[0].click();",
                                    self._driver.
                                    find_elements_by_class_name("js-shuffle")
                                    [-1])

    def current_track_title(self) -> str:
        """
        Gets the current track title.
        :return: String of the current track title.
        """
        return self._driver. \
            find_element_by_class_name("now-playing__metadata__title"). \
            get_property("title")

    def current_track_artists(self) -> str:
        """
        Gets a list of the current track artists, separated by ", ".
        :return: A string of the current track artists.
        """
        return ", ".join([x.get_property("title") for x in
                          self._driver.
                         find_element_by_class_name(
                              "now-playing__metadata__artist").
                         find_elements_by_tag_name('a')])

    def current_track_image(self) -> str:
        """
        Gets the URL of the album art for the current track.
        :return: A string containing the album art URL.
        """
        return self._driver. \
            find_element_by_class_name("js-footer-player-image"). \
            get_property("src")

    def current_track_progress(self) -> int:
        """
        Gets the progress of the current track in microseconds.
        :return: The current track progress in microseconds.
        """
        t = self._driver.find_element_by_class_name("js-progress"). \
            get_property("innerHTML").split(":")
        return int(t[0]) * 60 + int(t[1]) * 10000000  # Microseconds

    def current_track_duration(self) -> int:
        """
        Gets the duration of the current track in microseconds.
        :return: The current track duration in microseconds.
        """
        t = self._driver.find_element_by_class_name("js-duration"). \
            get_property("innerHTML").split(":")
        return int(t[0]) * 60 + int(t[1]) * 10000000  # Microseconds

    def current_location(self) -> str:
        """
        Gets the currently selected sidebar item.
        :return: The currently selected sidebar item.
        """
        link = self._driver.find_elements_by_class_name("menu__link--active")
        if len(link) == 0:
            return ""
        return link[0].find_element_by_tag_name("span"). \
            get_property("innerHTML")

    def set_position(self, position) -> None:
        """
        Set the current playback position.
        :param position: Position to skip to in microseconds. Must be less than
        current_track_duration().
        :return: Nothing
        """
        el = self._driver. \
            find_element_by_class_name("progressbar__interaction-layer")
        clickxpos = position * el.size["width"] / self.current_track_duration()

        action = webdriver.ActionChains(self._driver)
        action.move_to_element_with_offset(el, clickxpos, 5)
        action.click()
        action.perform()

    def raise_window(self) -> None:
        """
        Sets focus to the browser window.
        :return: Nothing
        """
        self._driver.switch_to.window(self._driver.current_window_handle)

    def set_fullscreen(self, value) -> None:
        """
        Set the window to fullscreen and maximise the player.
        :param value: True if fullscreen. False is currently not implemented.
        :return: Nothing
        """
        if value:
            self._driver.fullscreen_window()
            self._driver.execute_script("arguments[0].click();",
                                        self._driver.
                                        find_elements_by_class_name(
                                             "js-maximize")[0])

    def open_uri(self, uri) -> None:
        """
        Open a tidal:// protocol URI in the browser window without reloading
        the entire page.
        :param uri: The tidal:// URI to open.
        :return: Nothing
        """
        if not uri.startswith("tidal://"):
            return

        el = self._driver.find_elements_by_xpath("//*[@id=\"main\"]//a[1]")[-1]
        self._driver.execute_script(
            "arguments[0].href=arguments[1];arguments[0].click();", el,
            uri.replace("tidal://", "/"))

    def quit(self) -> None:
        """
        Quit the browser.
        :return: Nothing
        """
        self._driver.quit()
