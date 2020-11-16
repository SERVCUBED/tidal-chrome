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
        return "hasPlayer" in ''.join(self._driver.find_elements_by_xpath(
            '//div[contains(@class,"mainLayout")]/div[2]')[0].get_property("classList"))

    def play(self) -> None:
        """
        Play the current track.
        :return: Nothing
        """
        self._driver.execute_script("arguments[0].click();",
                                    self._driver.find_elements_by_xpath(
                                        '//button[contains(@class,"playback-controls")][@title="Play"]')
                                    [0])

    def pause(self) -> None:
        """
        Pause the current track.
        :return: Nothing
        """
        self._driver.execute_script("arguments[0].click();",
                                    self._driver.find_elements_by_xpath(
                                        '//button[contains(@class,"playback-controls")][@title="Pause"]')
                                    [0])

    def play_pause(self) -> bool:
        """
        Toggle the playing state for the current track.
        :return: True if track is now playing, false otherwise
        """
        el = self._driver.find_elements_by_xpath('//button[contains(@class,"playbackToggle")]')[0]
        self._driver.execute_script("arguments[0].click();", el)
        return el.get_property("title") == "Pause"

    def next(self) -> None:
        """
        Play the next track, if available.
        :return: Nothing
        """
        self._driver.execute_script("arguments[0].click();",
                                    self._driver.find_elements_by_xpath(
                                        '//button[contains(@class,"playback-controls")][@title="Next"]')
                                    [0])

    def previous(self) -> None:
        """
        Play the previous track, if available.
        :return: Nothing
        """
        self._driver.execute_script("arguments[0].click();",
                                    self._driver.find_elements_by_xpath(
                                        '//button[contains(@class,"playback-controls")][@title="Previous"]')
                                    [0])

    def is_playing(self) -> bool:
        """
        Gets whether the player is currently playing.
        :return: True if the player is currently playing.
        """
        return self._driver.find_elements_by_xpath(
            '//button[contains(@class,"playbackToggle")]')[0].get_property("title") == "Pause"

    def is_shuffle(self) -> bool:
        """
        Gets whether shuffle is currently enabled.
        :return: True if shuffle is currently enabled.
        """
        return "active" in \
            ''.join(self._driver.find_elements_by_xpath('//button[@title="Shuffle"]')[0].get_property("classList"))


    def toggle_shuffle(self) -> None:
        """
        Toggle the shuffle status.
        :return: Nothing
        """
        self._driver.execute_script("arguments[0].click();",
                                    self._driver.find_elements_by_xpath(
                                        '//button[@title="Shuffle"]')
                                    [0])

    def current_track_title(self) -> str:
        """
        Gets the current track title.
        :return: String of the current track title.
        """
        return self._driver. \
            find_elements_by_xpath('//div[contains(@class,"mediaInformation")]/span[1]/a')[0]. \
            get_property("innerHTML")

    def current_track_artists(self) -> list:
        """
        Gets a list of the current track artists, separated by ", ".
        :return: A string of the current track artists.
        """
        return [x.get_property("title") for x in
                          self._driver.
                         find_elements_by_xpath(
                              '//div[contains(@class,"leftColumn")]/div/div[contains(@class,"mediaInformation")]/span[2]/a')
                          ]

    def current_track_image(self) -> str:
        """
        Gets the URL of the album art for the current track.
        :return: A string containing the album art URL.
        """
        return self._driver. \
            find_elements_by_xpath('//figure[contains(@class,"mediaImagery")]/div/div/div/img[contains(@class,"image")]')[0]. \
            get_property("src")

    def current_track_progress(self) -> int:
        """
        Gets the progress of the current track in microseconds.
        :return: The current track progress in microseconds.
        """
        t = self._driver.find_elements_by_xpath('//time[contains(@class,"currentTime")]')[0]. \
            get_property("innerHTML").split(":")
        return int(t[0]) * 60 + int(t[1]) * 10000000  # Microseconds

    def current_track_duration(self) -> int:
        """
        Gets the duration of the current track in microseconds.
        :return: The current track duration in microseconds.
        """
        t = self._driver.find_elements_by_xpath('//time[contains(@class,"duration")]')[0]. \
            get_property("innerHTML").split(":")
        return int(t[0]) * 60 + int(t[1]) * 10000000  # Microseconds

    def set_position(self, position) -> None:
        """
        Set the current playback position.
        :param position: Position to skip to in microseconds. Must be less than
        current_track_duration().
        :return: Nothing
        """
        el = self._driver.find_elements_by_xpath(
            '//div[contains(@class,"progressBarWrapper")]/div/div[contains(@class,"interactionLayer")]')[0]
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
                                        find_elements_by_xpath(
                                            '//div[contains(@class,"overlayClickable")]')[0])

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
