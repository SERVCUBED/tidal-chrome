# Part of the Tidal-Chrome MPRIS bridge
# Author: SERVCUBED 2018-
# License: AGPL

import os
from typing import Optional

from selenium.webdriver import Chrome, ChromeOptions, ActionChains
from selenium.webdriver.common.keys import Keys


class Driver:

    def __init__(self, prefs=None, errorhandler: Optional[callable] = None):
        """
        Creates a new instance of the TIDAL-Chrome driver, opens a browser
        window and navigates to TIDAL.

        The browser's data directory is (by default) set to:
            ~/.config/tidal-google-chrome/
        """

        self.__errorhandler = errorhandler

        if not prefs:
            from . import preferences
            prefs = preferences.Preferences(True)

        chrome_options = ChromeOptions()
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
        self._driver = Chrome(prefs.values["chromedriver_binary_path"], options=chrome_options)

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
        t = self._driver.find_elements_by_xpath('//div[@id="wimp"]/div/div/div/div[2]')
        if not t:
            self.__errorhandler('can_play')
            return False
        return "hasPlayer" in ''.join(t[0].get_property("classList"))

    def play(self) -> None:
        """
        Play the current track.
        :return: Nothing
        """
        t = self._driver.find_elements_by_xpath('//div[@data-test="play-controls"]/div/button[@title="Play"]')
        if not t:
            self.__errorhandler('play')
            return
        self._driver.execute_script("arguments[0].click();", t[0])

    def pause(self) -> None:
        """
        Pause the current track.
        :return: Nothing
        """
        t = self._driver.find_elements_by_xpath('//div[@data-test="play-controls"]/div/button[@title="Pause"]')
        if not t:
            self.__errorhandler('pause')
            return
        self._driver.execute_script("arguments[0].click();", t[0])

    def play_pause(self) -> Optional[bool]:
        """
        Toggle the playing state for the current track.
        :return: True if track is now playing, false otherwise
        """
        el = self._driver.find_elements_by_xpath('//div[@data-test="play-controls"]/div/button')
        if not el:
            self.__errorhandler('play_pause')
            return None
        el = el[0]
        self._driver.execute_script("arguments[0].click();", el)
        return el.get_property("title") == "Pause"

    def next(self) -> None:
        """
        Play the next track, if available.
        :return: Nothing
        """
        t = self._driver.find_elements_by_xpath('//div[@data-test="play-controls"]/button[@title="Next"]')
        if not t:
            self.__errorhandler(__name__)
            return
        self._driver.execute_script("arguments[0].click();", t[0])

    def previous(self) -> None:
        """
        Play the previous track, if available.
        :return: Nothing
        """
        t = self._driver.find_elements_by_xpath('//div[@data-test="play-controls"]/button[@title="Previous"]')
        if not t:
            self.__errorhandler('previous')
            return
        self._driver.execute_script("arguments[0].click();", t[0])

    def is_playing(self) -> bool:
        """
        Gets whether the player is currently playing.
        :return: True if the player is currently playing.
        """
        t = self._driver.find_elements_by_xpath('//div[@data-test="play-controls"]/div/button')
        return t[0].get_property("title") == "Pause" if t else False

    def is_shuffle(self) -> bool:
        """
        Gets whether shuffle is currently enabled.
        :return: True if shuffle is currently enabled.
        """
        t = self._driver.find_elements_by_xpath('//div[@data-test="play-controls"]/button[@title="Shuffle"]')
        return t[0].get_attribute('aria-checked') == 'true' if t else False

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

        t = self._driver.find_elements_by_xpath('//div[@data-test="play-controls"]/button[@title="Shuffle"]')
        if not t:
            self.__errorhandler('toggle_shuffle')
            return
        self._driver.execute_script("arguments[0].click();", t[0])

    def current_track_title(self) -> str:
        """
        Gets the current track title.
        :return: String of the current track title.
        """
        t = self._driver.find_elements_by_xpath('//div[@data-test="footer-track-title"]/a/span')
        if not t:
            self.__errorhandler('current_track_title')
            return ''
        return t[0].get_property("innerHTML")

    def current_track_artists(self) -> list:
        """
        Gets a list of the current track artists, separated by ", ".
        :return: A string of the current track artists.
        """
        return [x.get_property("title") for x in
                self._driver.find_elements_by_xpath('//span[contains(@class,"artist-link")]/a')
                ]

    def current_track_image(self) -> str:
        """
        Gets the URL of the album art for the current track.
        :return: A string containing the album art URL.
        """
        t = self._driver.find_elements_by_xpath('//figure[@data-test="current-media-imagery"]/div/div/div/img')
        if not t:
            self.__errorhandler('current_track_image')
            return ''
        t = t[0].get_property("srcset")
        if not t:
            self.__errorhandler('current_track_image_srcset')
            return ''
        return t.split(',')[-1].split()[0]

    def current_track_progress(self) -> int:
        """
        Gets the progress of the current track in microseconds.
        :return: The current track progress in microseconds.
        """
        t = self._driver.find_elements_by_xpath('//time[@data-test="current-time"]')
        if not t:
            self.__errorhandler('current_track_progress')
            return 0
        t = t[0].get_property("innerHTML").split(":")
        return (int(t[0]) * 60 + int(t[1])) * 1000000  # Microseconds

    def current_track_duration(self) -> int:
        """
        Gets the duration of the current track in microseconds.
        :return: The current track duration in microseconds.
        """
        t = self._driver.find_elements_by_xpath('//time[@data-test="duration-time"]')
        if not t:
            self.__errorhandler('current_track_duration')
            return 0
        t = t[0].get_property("innerHTML").split(":")
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
            pfx + '//div[contains(@class,"progressBarWrapper")]/div/div[contains(@class,"interactionLayer")]')
        if not el:
            self.__errorhandler('set_position')
            return
        clickxpos = position * el[0].size["width"] / self.current_track_duration()

        action = ActionChains(self._driver)
        action.move_to_element_with_offset(el[0], clickxpos, 5)
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
        :param value: True if fullscreen. False if non-fullscreen maximised window; does not close the
        large now-playing.
        :return: Nothing
        """
        if value:
            # self._driver.fullscreen_window()
            self.set_now_playing_maximised(True)
            t = self._driver.find_elements_by_xpath('//button[@data-test="fullscreen"]')
            if not t:
                self.__errorhandler('set_fullscreen')
                return
            self._driver.execute_script("arguments[0].click();", t[0])
        else:
            # self._driver.maximize_window()
            ActionChains(self._driver).send_keys(Keys.ESCAPE).perform()

    def set_now_playing_maximised(self, value) -> None:
        """
        Set the window to fullscreen and maximise the player.
        :param value: True if to set. False to close the large now-playing window.
        :return: Nothing
        """
        if value is not self.is_now_playing_maximised():
            t = self._driver.find_elements_by_xpath('//button[@data-test="toggle-now-playing"]')
            if not t:
                self.__errorhandler('set_now_playing_maximised')
                return
            self._driver.execute_script("arguments[0].click();", t[0])

    def open_uri(self, uri) -> None:
        """
        Open a tidal:/ protocol URI in the browser window without reloading
        the entire page.
        :param uri: The tidal:/ URI to open.
        :return: Nothing
        """
        if not uri.startswith("tidal:/"):
            self.__errorhandler("open_uri: Incorrect URI format")
            return

        el = self._driver.find_elements_by_xpath("//*[@id=\"main\"]//a[1]")
        if not el:
            self.__errorhandler('open_uri')
            return
        el = el[-1]
        self._driver.execute_script(
            "arguments[0].href=arguments[1];arguments[0].click();", el,
            uri.replace("tidal:/", ""))

    def quit(self) -> None:
        """
        Quit the browser.
        :return: Nothing
        """
        self._driver.quit()
