# Part of the Tidal-Chrome MPRIS bridge
# Author: SERVCUBED 2018-
# License: AGPL

import os

from selenium import webdriver


class Driver:

    def __init__(self, prefs=None):
        """
        Creates a new instance of the TIDAL-Chrome driver, opens a browser
        window and navigates to TIDAL.

        The browser's data directory is (by default) set to:
            ~/.config/tidal-google-chrome/
        """

        if not prefs:
            from . import preferences
            prefs = preferences.Preferences(True)

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--disable-sync")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--user-data-dir=" +
                                    os.path.expanduser(
                                        prefs.values["profile_path"]))
        chrome_options.add_argument("--disable-features=MediaSessionService")
        chrome_options.add_argument("--app=https://listen.tidal.com/")
        if prefs.values["enable_kiosk_mode"]:
            chrome_options.add_argument("--kiosk")

        if prefs.values["chrome_binary_path"] is not None:
            chrome_options.binary_location = prefs.values["chrome_binary_path"]

        print("Starting webdriver")
        self._driver = webdriver.Chrome(prefs.values["chromedriver_binary_path"], options=chrome_options)

        print("Waiting for load")
        self._driver.implicitly_wait(10)

        print("Started")

    def __del__(self):
        self.quit()

    def can_play(self) -> bool:
        """
        Get whether the player can play, pause, seek.
        :return: True if the player can play, pause, seek
        """
        return "hasPlayer" in ''.join(self._driver.find_elements_by_xpath(
            '//div[@id="wimp"]/div/div/div/div[2]')[0].get_property("classList"))

    def play(self) -> None:
        """
        Play the current track.
        :return: Nothing
        """
        self._driver.execute_script("arguments[0].click();",
                                    self._driver.find_elements_by_xpath(
                                        '//div[@data-test="play-controls"]/div/button[@title="Play"]')
                                    [0])

    def pause(self) -> None:
        """
        Pause the current track.
        :return: Nothing
        """
        self._driver.execute_script("arguments[0].click();",
                                    self._driver.find_elements_by_xpath(
                                        '//div[@data-test="play-controls"]/div/button[@title="Pause"]')
                                    [0])

    def play_pause(self) -> bool:
        """
        Toggle the playing state for the current track.
        :return: True if track is now playing, false otherwise
        """
        el = self._driver.find_elements_by_xpath('//div[@data-test="play-controls"]/div/button')[0]
        self._driver.execute_script("arguments[0].click();", el)
        return el.get_property("title") == "Pause"

    def next(self) -> None:
        """
        Play the next track, if available.
        :return: Nothing
        """
        self._driver.execute_script("arguments[0].click();",
                                    self._driver.find_elements_by_xpath(
                                        '//div[@data-test="play-controls"]/button[@title="Next"]')
                                    [0])

    def previous(self) -> None:
        """
        Play the previous track, if available.
        :return: Nothing
        """
        self._driver.execute_script("arguments[0].click();",
                                    self._driver.find_elements_by_xpath(
                                        '//div[@data-test="play-controls"]/button[@title="Previous"]')
                                    [0])

    def is_playing(self) -> bool:
        """
        Gets whether the player is currently playing.
        :return: True if the player is currently playing.
        """
        return self._driver.find_elements_by_xpath(
            '//div[@data-test="play-controls"]/div/button')[0].get_property("title") == "Pause"

    def is_shuffle(self) -> bool:
        """
        Gets whether shuffle is currently enabled.
        :return: True if shuffle is currently enabled.
        """
        return self._driver.find_elements_by_xpath('//div[@data-test="play-controls"]/button[@title="Shuffle"]')[0].get_attribute('aria-checked') == 'true'

    def is_now_playing_maximised(self) -> bool:
        """
        Gets whether the "Now Playing" section is fullscreen
        :return True if the "Now Playing" section is fullscreen
        """
        return len(self._driver.find_elements_by_xpath('//section[@id="nowPlaying"]/div/div')) > 1

    def toggle_shuffle(self) -> None:
        """
        Toggle the shuffle status.
        :return: Nothing
        """
        self._driver.execute_script("arguments[0].click();",
                                    self._driver.find_elements_by_xpath(
                                        '//div[@data-test="play-controls"]/button[@title="Shuffle"]')
                                    [0])

    def current_track_title(self) -> str:
        """
        Gets the current track title.
        :return: String of the current track title.
        """
        return self._driver. \
            find_elements_by_xpath('//div[@data-test="footer-track-title"]/a/span')[0]. \
            get_property("innerHTML")

    def current_track_artists(self) -> list:
        """
        Gets a list of the current track artists, separated by ", ".
        :return: A string of the current track artists.
        """
        return [x.get_property("title") for x in
                self._driver.
                    find_elements_by_xpath(
                    '//span[contains(@class,"artist-link")]/a')
                ]

    def current_track_image(self) -> str:
        """
        Gets the URL of the album art for the current track.
        :return: A string containing the album art URL.
        """
        return self._driver. \
            find_elements_by_xpath(
            '//figure[@data-test="current-media-imagery"]/div/div/div/img')[0]. \
            get_property("srcset").split(',')[-1].split()[0]

    def current_track_progress(self) -> int:
        """
        Gets the progress of the current track in microseconds.
        :return: The current track progress in microseconds.
        """
        t = self._driver.find_elements_by_xpath('//time[@data-test="current-time"]')[0]. \
            get_property("innerHTML").split(":")
        return (int(t[0]) * 60 + int(t[1])) * 1000000  # Microseconds

    def current_track_duration(self) -> int:
        """
        Gets the duration of the current track in microseconds.
        :return: The current track duration in microseconds.
        """
        t = self._driver.find_elements_by_xpath('//time[@data-test="duration-time"]')[0]. \
            get_property("innerHTML").split(":")
        return (int(t[0]) * 60 + int(t[1])) * 1000000  # Microseconds

    def set_position(self, position) -> None:
        """
        Set the current playback position.
        :param position: Position to skip to in microseconds. Must be less than
        current_track_duration().
        :return: Nothing
        """
        pfx = '//section[@id="nowPlaying"]' if self.is_now_playing_maximised() else ''
        el = self._driver.find_elements_by_xpath(
            pfx + '//div[contains(@class,"progressBarWrapper")]/div/div[contains(@class,"interactionLayer")]')[0]
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
        Open a tidal:/ protocol URI in the browser window without reloading
        the entire page.
        :param uri: The tidal:/ URI to open.
        :return: Nothing
        """
        if not uri.startswith("tidal:/"):
            return

        el = self._driver.find_elements_by_xpath("//*[@id=\"main\"]//a[1]")[-1]
        self._driver.execute_script(
            "arguments[0].href=arguments[1];arguments[0].click();", el,
            uri.replace("tidal:/", ""))

    def quit(self) -> None:
        """
        Quit the browser.
        :return: Nothing
        """
        self._driver.quit()
