#!/usr/bin/python

# Tidal-Chrome MPRIS bridge

# Author: SERVCUBED
# License: GPL

# MPRIS Specification: https://specifications.freedesktop.org/mpris-spec/latest/
# D-Bus Specification: https://dbus.freedesktop.org/doc/dbus-specification.html

from gi.repository import GLib
import sys
import threading
import time
import dbus
import dbus.service
import tidal_chrome.tidal_chrome_driver
import traceback
from selenium.common.exceptions import WebDriverException

from dbus.mainloop.glib import DBusGMainLoop

OPATH = "/org/mpris/MediaPlayer2"
BASE_IFACE = "org.mpris.MediaPlayer2"
PLAYER_IFACE = "org.mpris.MediaPlayer2.Player"
BUS_NAME = "org.mpris.MediaPlayer2.tidal-chrome"


class MPRIS(dbus.service.Object):
    def __init__(self, isdebug):
        self.isdebug = isdebug
        self.quit = False
        self.driver = tidal_chrome.tidal_chrome_driver.Driver()
        self.baseproperties = {"CanQuit": True, "Fullscreen": False, "CanSetFullscreen": True, "CanRaise": False,
                               "HasTrackList": False, "Identity": "Tidal-Chrome API bridge",
                               "SupportedUriSchemes": [''],
                               "SupportedMimeTypes": ['']}
        self.playerproperties = {"PlaybackStatus": "Stopped", "LoopStatus": "None", "Rate": 1.0, "Shuffle": False,
                                 "Metadata": dbus.Dictionary({
                                     'mpris:trackid': "",
                                     'mpris:length': 0,
                                     'mpris:artUrl': "",
                                     'xesam:title': "",
                                     'xesam:album': "",
                                     'xesam:artist': ""
                                 }, signature="sv"),
                                 "Volume": 0, "Position": 0, "MinimumRate": 1.0, "MaximumRate": 1.0,
                                 "CanGoNext": True, "CanGoPrevious": True, "CanPlay": True, "CanPause": True,
                                 "CanSeek": True, "CanControl": True}
        self._last_track_name = ""

        bus = dbus.SessionBus()
        bus.request_name(BUS_NAME)
        bus_name = dbus.service.BusName(BUS_NAME, bus=bus)
        dbus.service.Object.__init__(self, bus_name, OPATH)

        self._timer_i = 0
        self.tick_timer = threading.Thread(target=self._timer_start)
        self.tick_timer.start()

    @dbus.service.method(dbus_interface=BASE_IFACE, in_signature="", out_signature="")
    def Raise(self):
        self.driver.raiseWindow()

    @dbus.service.method(dbus_interface=BASE_IFACE, in_signature="", out_signature="")
    def Quit(self):
        self.driver.quit()
        self.quit = True
        sys.exit(0)

    # Properties
    @dbus.service.method(dbus_interface=dbus.PROPERTIES_IFACE, in_signature='ss', out_signature='v')
    def Get(self, interface_name, property_name):
        return self.GetAll(interface_name)[property_name]

    @dbus.service.method(dbus_interface=dbus.PROPERTIES_IFACE, in_signature='s', out_signature='a{sv}')
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

    @dbus.service.method(dbus_interface=dbus.PROPERTIES_IFACE, in_signature='ssv')
    def Set(self, interface_name, property_name, new_value):
        if interface_name == BASE_IFACE:
            self._set_base_property(property_name, new_value)
        elif interface_name == PLAYER_IFACE:
            self._set_player_property(property_name, new_value)
        # validate the property name and value, update internal state…
        self.PropertiesChanged(interface_name, {property_name: new_value}, [])

    @dbus.service.signal(dbus_interface=dbus.PROPERTIES_IFACE, signature='sa{sv}as')
    def PropertiesChanged(self, interface_name, changed_properties,
                          invalidated_properties):
        pass

    # Player controls

    @dbus.service.method(dbus_interface=PLAYER_IFACE, in_signature="", out_signature="")
    def Next(self):
        self.driver.next()

    @dbus.service.method(dbus_interface=PLAYER_IFACE, in_signature="", out_signature="")
    def Previous(self):
        self.driver.previous()

    @dbus.service.method(dbus_interface=PLAYER_IFACE, in_signature="", out_signature="")
    def Pause(self):
        self.driver.pause()
        self.PropertiesChanged(PLAYER_IFACE, {"PlaybackStatus": "Paused"}, [])

    @dbus.service.method(dbus_interface=PLAYER_IFACE, in_signature="", out_signature="")
    def PlayPause(self):
        if self.driver.isPlaying():
            self.Pause()
        else:
            self.Play()

    @dbus.service.method(dbus_interface=PLAYER_IFACE, in_signature="", out_signature="")
    def Stop(self):
        self.Pause()

    @dbus.service.method(dbus_interface=PLAYER_IFACE, in_signature="", out_signature="")
    def Play(self):
        if not self.driver.CanPlay():
            return

        self.driver.play()
        self.PropertiesChanged(PLAYER_IFACE, {"PlaybackStatus": "Playing"}, [])

    @dbus.service.method(dbus_interface=PLAYER_IFACE, in_signature='x', out_signature="")
    def Seek(self, offset):
        self.SetPosition("", self.driver.currentTrackProgress() + offset)

    @dbus.service.method(dbus_interface=PLAYER_IFACE, in_signature='ox', out_signature="")
    def SetPosition(self, trackid, position):
        position = int(position)
        if not self.driver.CanPlay() or position < 0 or position > self.driver.currentTrackDuration():
            return
        self.driver.setPosition(position)
        self.PropertiesChanged(PLAYER_IFACE, {"Position": position}, [])

    @dbus.service.method(dbus_interface=PLAYER_IFACE, in_signature='s', out_signature="")
    def OpenUri(self, uri):
        # TODO
        return None

    def _set_base_property(self, name, value):
        if name not in ["Fullscreen"]:
            return
        if name == "Fullscreen" and value is True:
            self.driver.setFullscreen()
        self.baseproperties[name] = value

    def _set_player_property(self, name, value):
        if name not in ["Loopstatus", "Rate", "Shuffle", "Volume"]:
            return
        if name == "Shuffle":
            if value != self.driver.isShuffle():
                self.driver.toggleShuffle()
        self.playerproperties[name] = value

    def _update_tick(self):
        if self.isdebug:
            print("Tick")
        changed = {}

        curr_title = self.driver.currentTrackTitle()

        if self._last_track_name != curr_title:
            self._last_track_name = curr_title
            self.playerproperties["Metadata"] = dbus.Dictionary({
                'mpris:length': self.driver.currentTrackDuration(),
                'mpris:artUrl': self.driver.currentTrackImage(),
                'xesam:title': curr_title,
                'xesam:album': self.driver.currentLocation(),
                'xesam:artist': self.driver.currentTrackArtists()
            }, signature="sv")
            changed["Metadata"] = self.playerproperties["Metadata"]

        canplay = self.driver.CanPlay()
        if self.playerproperties["CanPlay"] != canplay:
            self.playerproperties["CanPlay"] = canplay
            changed["CanPlay"] = canplay

        state = ("Playing" if self.driver.isPlaying() else "Paused") if canplay else "Stopped"
        if self.playerproperties["PlaybackStatus"] != state:
            self.playerproperties["PlaybackStatus"] = state
            changed["PlaybackStatus"] = state

        position = self.driver.currentTrackProgress()
        if self.playerproperties["Position"] != position:
            self.playerproperties["Position"] = position
            changed["Position"] = position

        if len(changed) > 0:
            self.PropertiesChanged(PLAYER_IFACE, changed, [])

    def _update_reduced_tick(self):
        if self.isdebug:
            print("Reduced Tick")
        changed = {}

        isshuffle = self.driver.isShuffle()
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

            except:
                print("Update error: ", traceback.format_exc())

            time.sleep(5)


def run(isdebug=False):
    print("TIDAL-Chrome by SERVCUBED, isdebug=" + str(isdebug))
    DBusGMainLoop(set_as_default=True)
    loop = GLib.MainLoop()

    a = None

    try:
        a = MPRIS(isdebug)
        loop.run()
    except KeyboardInterrupt:
        print("Keyboard interrupt")
        a.quit = True
    finally:
        loop.quit()
        sys.exit(0)


if __name__ == '__main__':
    run(True)
