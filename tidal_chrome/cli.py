#!/usr/bin/python

# Tidal-Chrome MPRIS bridge

# Author: SERVCUBED
# License: GPL

# MPRIS Specification:
#   https://specifications.freedesktop.org/mpris-spec/latest/
# D-Bus Specification:
#   https://dbus.freedesktop.org/doc/dbus-specification.html

import sys
import threading
import time
import traceback

from gi.repository import GLib
from pydbus import SessionBus
from selenium.common.exceptions import WebDriverException

import tidal_chrome.tidal_chrome_driver

OPATH = "/org/mpris/MediaPlayer2"
BASE_IFACE = "org.mpris.MediaPlayer2"
PLAYER_IFACE = "org.mpris.MediaPlayer2.Player"
BUS_NAME = "org.mpris.MediaPlayer2.tidal-chrome"


class MPRIS(object):
    """
<node>
    <interface name="org.freedesktop.DBus.Properties">
        <method name="Get">
            <arg type="s" name="interface_name" direction="in"/>
            <arg type="s" name="property_name" direction="in"/>
            <arg type="v" name="value" direction="out"/>
        </method>
        <method name="GetAll">
            <arg type="s" name="interface_name" direction="in"/>
            <arg type="a{sv}" name="properties" direction="out"/>
        </method>
        <method name="Set">
            <arg type="s" name="interface_name" direction="in"/>
            <arg type="s" name="property_name" direction="in"/>
            <arg type="v" name="value" direction="in"/>
        </method>
        <signal name="PropertiesChanged">
            <arg type="s" name="interface_name"/>
            <arg type="a{sv}" name="changed_properties"/>
            <arg type="as" name="invalidated_properties"/>
        </signal>
    </interface>
    <interface name="org.mpris.MediaPlayer2">
        <method name="Raise"/>
        <method name="Quit"/>
        <property type="b" name="CanQuit" access="read"/>
        <property type="b" name="CanRaise" access="read"/>
        <property type="b" name="HasTrackList" access="read"/>
        <property type="s" name="Identity" access="read"/>
        <property type="s" name="DesktopEntry" access="read"/>
        <property type="as" name="SupportedUriSchemes" access="read"/>
        <property type="as" name="SupportedMimeTypes" access="read"/>
    </interface>
    <interface name="org.mpris.MediaPlayer2.Player">
        <method name="Next"/>
        <method name="Previous"/>
        <method name="Pause"/>
        <method name="PlayPause"/>
        <method name="Stop"/>
        <method name="Play"/>
        <method name="Seek">
            <arg type="x" name="Offset" direction="in"/>
        </method>
        <method name="SetPosition">
            <arg type="o" name="TrackId" direction="in"/>
            <arg type="x" name="Position" direction="in"/>
        </method>
        <method name="OpenUri">
            <arg type="s" name="Uri" direction="in"/>
        </method>
        <signal name="Seeked">
            <arg type="x" name="Position"/>
        </signal>
        <property type="s" name="PlaybackStatus" access="read"/>
        <property type="s" name="LoopStatus" access="readwrite"/>
        <property type="d" name="Rate" access="readwrite"/>
        <property type="b" name="Shuffle" access="readwrite"/>
        <property type="a{sv}" name="Metadata" access="read"/>
        <property type="d" name="Volume" access="readwrite"/>
        <property type="x" name="Position" access="read"/>
        <property type="d" name="MinimumRate" access="read"/>
        <property type="d" name="MaximumRate" access="read"/>
        <property type="b" name="CanGoNext" access="read"/>
        <property type="b" name="CanGoPrevious" access="read"/>
        <property type="b" name="CanPlay" access="read"/>
        <property type="b" name="CanPause" access="read"/>
        <property type="b" name="CanSeek" access="read"/>
        <property type="b" name="CanControl" access="read"/>
    </interface>
</node>
    """

    def __init__(self, isdebug):
        self.isdebug = isdebug
        self.quit = False
        self.driver = tidal_chrome.tidal_chrome_driver.Driver()

        self.baseproperties = {"CanQuit": True,
                               "Fullscreen": False,
                               "CanSetFullscreen": True,
                               "CanRaise": False,
                               "HasTrackList": False,
                               "Identity": "Tidal-Chrome API bridge",
                               "SupportedUriSchemes": [''],
                               "SupportedMimeTypes": ['']}

        self.playerproperties = {"PlaybackStatus": "Stopped",
                                 "LoopStatus": "None",
                                 "Rate": 1.0,
                                 "Shuffle": False,
                                 "Metadata": {
                                     'mpris:trackid': "/org/mpris/MediaPlayer2/TrackList/NoTrack",
                                     'mpris:length': 0,
                                     'mpris:artUrl': "",
                                     'xesam:title': "",
                                     'xesam:album': "",
                                     'xesam:artist': ""
                                 },
                                 "Volume": 0,
                                 "Position": 0,
                                 "MinimumRate": 1.0,
                                 "MaximumRate": 1.0,
                                 "CanGoNext": True,
                                 "CanGoPrevious": True,
                                 "CanPlay": True,
                                 "CanPause": True,
                                 "CanSeek": True,
                                 "CanControl": True}
        self._last_track_name = ""

        self._timer_i = 0
        self.tick_timer = threading.Thread(target=self._timer_start)
        self.tick_timer.start()

    def Raise(self):
        self.driver.raise_window()

    def Quit(self):
        self.driver.quit()
        self.quit = True
        sys.exit(0)

    # Properties
    def Get(self, interface_name, property_name):
        return self.GetAll(interface_name)[property_name]

    def GetAll(self, interface_name):
        if interface_name == BASE_IFACE:
            return self.baseproperties
        elif interface_name == PLAYER_IFACE:
            return self.playerproperties
        else:
            raise dbus.exceptions.DBusException(
                'com.example.UnknownInterface',
                'The Foo object does not implement the %s interface'
                % interface_name)

    def Set(self, interface_name, property_name, new_value):
        if interface_name == BASE_IFACE:
            self._set_base_property(property_name, new_value)
        elif interface_name == PLAYER_IFACE:
            self._set_player_property(property_name, new_value)
        # validate the property name and value, update internal state…
        self.PropertiesChanged(interface_name, {property_name: new_value}, [])

    def PropertiesChanged(self, interface_name, changed_properties,
                          invalidated_properties):
        pass

    # Player controls

    def Next(self):
        self.driver.next()

    def Previous(self):
        self.driver.previous()

    def Pause(self):
        self.driver.pause()
        self.PropertiesChanged(PLAYER_IFACE, {"PlaybackStatus": "Paused"}, [])

    def PlayPause(self):
        if self.driver.is_playing():
            self.Pause()
        else:
            self.Play()

    def Stop(self):
        self.Pause()

    def Play(self):
        if not self.driver.can_play():
            return

        self.driver.play()
        self.PropertiesChanged(PLAYER_IFACE, {"PlaybackStatus": "Playing"},
                               [])

    def Seek(self, offset):
        self.SetPosition("", self.driver.current_track_progress() + offset)

    def SetPosition(self, trackid, position):
        position = int(position)
        if not self.driver.can_play() or position < 0 or \
                position > self.driver.current_track_duration():
            return
        self.driver.set_position(position)
        self.PropertiesChanged(PLAYER_IFACE, {"Position": position}, [])

    def OpenUri(self, uri):
        # TODO
        return None

    def _set_base_property(self, name, value):
        if name not in ["Fullscreen"]:
            return
        if name == "Fullscreen" and value is True:
            self.driver.set_fullscreen()
        self.baseproperties[name] = value

    def _set_player_property(self, name, value):
        if name not in ["Loopstatus", "Rate", "Shuffle", "Volume"]:
            return
        if name == "Shuffle":
            if value != self.driver.is_shuffle():
                self.driver.toggle_shuffle()
        self.playerproperties[name] = value

    def _update_tick(self):
        if self.isdebug:
            print("Tick")
        changed = {}

        curr_title = self.driver.current_track_title()

        if self._last_track_name != curr_title:
            self._last_track_name = curr_title
            duration = self.driver.current_track_duration()
            self.playerproperties["Metadata"] = {
                'mpris:trackid': '/org/mpris/MediaPlayer2/TrackList/' + str(duration),
                'mpris:length': duration,
                'mpris:artUrl': self.driver.current_track_image(),
                'xesam:title': curr_title,
                'xesam:album': self.driver.current_location(),
                'xesam:artist': self.driver.current_track_artists()
            }
            changed["Metadata"] = self.playerproperties["Metadata"]

        canplay = self.driver.can_play()
        if self.playerproperties["CanPlay"] != canplay:
            self.playerproperties["CanPlay"] = canplay
            changed["CanPlay"] = canplay

        state = ("Playing" if self.driver.is_playing() else "Paused") \
            if canplay else "Stopped"
        if self.playerproperties["PlaybackStatus"] != state:
            self.playerproperties["PlaybackStatus"] = state
            changed["PlaybackStatus"] = state

        position = self.driver.current_track_progress()
        if self.playerproperties["Position"] != position:
            self.playerproperties["Position"] = position
            changed["Position"] = position

        if len(changed) > 0:
            self.PropertiesChanged(PLAYER_IFACE, changed, [])

    def _update_reduced_tick(self):
        if self.isdebug:
            print("Reduced Tick")
        changed = {}

        isshuffle = self.driver.is_shuffle()
        if self.playerproperties["Shuffle"] != isshuffle:
            self.playerproperties["Shuffle"] = isshuffle
            changed["Shuffle"] = isshuffle

        if len(changed) > 0:
            self.PropertiesChanged(PLAYER_IFACE, changed, [])

    def _timer_start(self):
        time.sleep(10)
        while not self.quit:
            try:
                self._update_tick()

                self._timer_i += 1
                if self._timer_i >= 5:
                    self._timer_i = 0
                    self._update_reduced_tick()

            except WebDriverException as e:
                if e.msg == "chrome not reachable":
                    print("Quitting")
                    self.Quit()
                else:
                    print("WebDriverException: " + e.msg)
            except ConnectionRefusedError:
                print("Chrome connection refused. Quitting")
                self.Quit()

            except Exception:
                print("Update error: ", traceback.format_exc())

            time.sleep(5)


def run(isdebug=False):
    print("TIDAL-Chrome by SERVCUBED, isdebug=" + str(isdebug))
    loop = GLib.MainLoop()

    a = None

    try:
        a = MPRIS(isdebug)
        print("running")
        bus = SessionBus()
        bus.request_name(BUS_NAME)
        bus.register_object(OPATH, a)
        # bus.publish(BUS_NAME, a)
        print("running")
        loop.run()
    except KeyboardInterrupt:
        print("Keyboard interrupt")
        a.quit = True
    finally:
        loop.quit()
        sys.exit(0)


if __name__ == '__main__':
    run(True)
