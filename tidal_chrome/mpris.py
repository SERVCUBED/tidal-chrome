# Part of the Tidal-Chrome MPRIS bridge
# Author: SERVCUBED 2018-
# License: AGPL

import sys
import threading
import time
import traceback

import dbus
import dbus.service
from selenium.common.exceptions import WebDriverException

from .__init__ import *
from . import tidal_chrome_driver


def handle_driver_error(err: str):
    print("Error in finding driver element: %s" % err)


class MPRIS(dbus.service.Object):
    def __init__(self, isdebug, bus, loop=None, prefs=None):
        self.isdebug = isdebug
        self.loop = loop
        if not prefs:
            from . import preferences
            prefs = preferences.Preferences(True)
        self.prefs = prefs
        self.quit = False
        self.driver = tidal_chrome_driver.Driver(prefs, handle_driver_error)

        self.baseproperties = {"CanQuit": True,
                               "Fullscreen": False,
                               "CanSetFullscreen": True,
                               "CanRaise": True,
                               "HasTrackList": False,
                               "DesktopEntry": "tidal-google-chrome",
                               "Identity": "Tidal-Chrome API bridge",
                               "SupportedUriSchemes": ['tidal'],
                               "SupportedMimeTypes": ['x-scheme-handler/tidal']}

        self.playerproperties = {"PlaybackStatus": "Stopped",
                                 "LoopStatus": "None",
                                 "Rate": 1.0,
                                 "Shuffle": False,
                                 "Metadata": dbus.Dictionary({
                                     'mpris:trackid': dbus.ObjectPath(
                                         "/org/mpris/MediaPlayer2/TrackList/NoTrack",
                                         variant_level=0),
                                     'mpris:length': dbus.Int64(0),
                                     'mpris:artUrl': "",
                                     'xesam:title': "",
                                     'xesam:album': "",
                                     'xesam:artist': dbus.Array([], signature="s")
                                 }, signature="sv"),
                                 "Volume": 1.0,
                                 "Position": dbus.Int64(0),
                                 "MinimumRate": 1.0,
                                 "MaximumRate": 1.0,
                                 "CanGoNext": True,
                                 "CanGoPrevious": True,
                                 "CanPlay": True,
                                 "CanPause": True,
                                 "CanSeek": True,
                                 "CanControl": True}
        self._last_track_name = ""

        bus.request_name(BUS_NAME)
        bus_name = dbus.service.BusName(BUS_NAME, bus=bus)
        dbus.service.Object.__init__(self, bus_name, OPATH)

        self._timer_i = 0
        self.tick_timer = threading.Thread(target=self.__timer_start)
        self.tick_timer.start()

    @dbus.service.method(dbus_interface=BASE_IFACE, in_signature="",
                         out_signature="")
    def Raise(self):
        self.driver.raise_window()

    @dbus.service.method(dbus_interface=BASE_IFACE, in_signature="",
                         out_signature="")
    def Quit(self):
        self.driver.quit()
        self.quit = True
        if self.loop:
            self.loop.quit()
        sys.exit(0)

    # Properties
    @dbus.service.method(dbus_interface=dbus.PROPERTIES_IFACE,
                         in_signature='ss', out_signature='v')
    def Get(self, interface_name, property_name):
        return self.GetAll(interface_name)[property_name]

    @dbus.service.method(dbus_interface=dbus.PROPERTIES_IFACE,
                         in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface_name):
        if interface_name == BASE_IFACE:
            return self.baseproperties
        elif interface_name == PLAYER_IFACE:
            return self.playerproperties
        else:
            raise dbus.exceptions.DBusException(
                'com.example.UnknownInterface',
                'The tidal-chrome object does not implement the %s interface'
                % interface_name)

    @dbus.service.method(dbus_interface=dbus.PROPERTIES_IFACE,
                         in_signature='ssv')
    def Set(self, interface_name, property_name, new_value):
        if interface_name == BASE_IFACE:
            self.__set_base_property(property_name, new_value)
        elif interface_name == PLAYER_IFACE:
            self.__set_player_property(property_name, new_value)

    @dbus.service.signal(dbus_interface=dbus.PROPERTIES_IFACE,
                         signature='sa{sv}as')
    def PropertiesChanged(self, interface_name, changed_properties,
                          invalidated_properties):
        pass

    @dbus.service.method(dbus_interface=dbus.INTROSPECTABLE_IFACE,
                         in_signature='', out_signature='s',
                         path_keyword='object_path',
                         connection_keyword='connection')
    def Introspect(self, object_path, connection):
        return """
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
        <property type="b" name="Fullscreen" access="readwrite"/>
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

    # Player controls

    @dbus.service.method(dbus_interface=PLAYER_IFACE, in_signature="",
                         out_signature="")
    def Next(self):
        self.driver.next()

    @dbus.service.method(dbus_interface=PLAYER_IFACE, in_signature="",
                         out_signature="")
    def Previous(self):
        self.driver.previous()

    @dbus.service.method(dbus_interface=PLAYER_IFACE, in_signature="",
                         out_signature="")
    def Pause(self):
        self.driver.pause()
        self.PropertiesChanged(PLAYER_IFACE, {"PlaybackStatus": "Paused"}, [])

    @dbus.service.method(dbus_interface=PLAYER_IFACE, in_signature="",
                         out_signature="")
    def PlayPause(self):
        ps = self.driver.play_pause()
        if ps is None:
            return
        self.PropertiesChanged(PLAYER_IFACE, {"PlaybackStatus": "Playing" if ps else "Paused"}, [])

    @dbus.service.method(dbus_interface=PLAYER_IFACE, in_signature="",
                         out_signature="")
    def Stop(self):
        self.Pause()

    @dbus.service.method(dbus_interface=PLAYER_IFACE, in_signature="",
                         out_signature="")
    def Play(self):
        if not self.driver.can_play():
            return

        self.driver.play()
        self.PropertiesChanged(PLAYER_IFACE, {"PlaybackStatus": "Playing"},
                               [])

    @dbus.service.method(dbus_interface=PLAYER_IFACE, in_signature='x',
                         out_signature="")
    def Seek(self, offset):
        position = self.driver.current_track_progress() + offset
        self.SetPosition("", position)
        self.Seeked(position)

    @dbus.service.signal(dbus_interface=PLAYER_IFACE, signature='x')
    def Seeked(self, position):
        pass

    @dbus.service.method(dbus_interface=PLAYER_IFACE, in_signature='ox',
                         out_signature="")
    def SetPosition(self, trackid, position):
        position = int(position)
        if not self.driver.can_play() or position < 0 or \
                position > self.driver.current_track_duration():
            return
        self.driver.set_position(position)
        self.PropertiesChanged(PLAYER_IFACE, {"Position": position}, [])
        self.Seeked(position)

    @dbus.service.method(dbus_interface=PLAYER_IFACE, in_signature='s',
                         out_signature="")
    def OpenUri(self, uri):
        self.driver.open_uri(uri)

    def __set_base_property(self, name, value):
        if name not in ["Fullscreen"]:
            return
        if self.baseproperties[name] == value:
            return
        if name == "Fullscreen":
            self.driver.set_fullscreen(value)
        self.baseproperties[name] = value
        self.PropertiesChanged(BASE_IFACE, {name: value}, [])

    def __set_player_property(self, name, value):
        if name not in ["LoopStatus", "Rate", "Shuffle", "Volume"]:
            return
        if self.playerproperties[name] == value:
            return
        if name == "Shuffle":
            isshuffle = self.driver.is_shuffle()
            if isshuffle is None or value == isshuffle:
                return
            self.driver.toggle_shuffle()
        if name == "LoopStatus":
            value = value.lower()
            if value not in ["track", "playlist"]:
                return
            o = self.prefs.values["use_loop_status_%s_for" % value]
            if o is not None:
                if "action" not in o or "args" not in o:
                    print(f"Cannot set property: Malformed value for use_loop_status_{value}_for preferences")
                    return
                if o["action"] == "add_cur_to_playlist":
                    self.driver.add_cur_to_playlist(*o["args"])
            return

        self.playerproperties[name] = value
        self.PropertiesChanged(PLAYER_IFACE, {name: value}, [])

    def __update_tick(self):
        if self.isdebug:
            print("Tick")
        changed = {}

        canplay = self.driver.can_play()
        if self.playerproperties["CanPlay"] != canplay:
            self.playerproperties["CanPlay"] = canplay
            changed["CanPlay"] = canplay

        state = ("Playing" if self.driver.is_playing() else "Paused") \
            if canplay else "Stopped"
        if self.playerproperties["PlaybackStatus"] != state:
            self.playerproperties["PlaybackStatus"] = state
            changed["PlaybackStatus"] = state

        if canplay:
            curr_title = self.driver.current_track_title()

            if self._last_track_name != curr_title:
                self._last_track_name = curr_title
                duration = self.driver.current_track_duration()
                self.playerproperties["Metadata"] = dbus.Dictionary({
                    'mpris:trackid': dbus.ObjectPath(
                        '/org/mpris/MediaPlayer2/TrackList/' + str(duration),
                        variant_level=0),
                    'mpris:length': dbus.Int64(duration),
                    'mpris:artUrl': self.driver.current_track_image(),
                    'xesam:title': curr_title,
                    'xesam:album': "",
                    'xesam:artist': dbus.Array(self.driver.current_track_artists(), signature="s")
                }, signature="sv")
                changed["Metadata"] = self.playerproperties["Metadata"]
                changed["PlaybackStatus"] = state

            position = self.driver.current_track_progress()
            if self.playerproperties["Position"] != position:
                changed["Position"] = self.playerproperties["Position"] = dbus.Int64(position)

            # Update favourited state on track change
            if self.driver.useShuffleAsCurFavourite:
                isshuffle = self.driver.is_shuffle()
                if isshuffle is not None and self.playerproperties["Shuffle"] != isshuffle:
                    self.playerproperties["Shuffle"] = isshuffle
                    changed["Shuffle"] = isshuffle

        elif self._last_track_name != "":
            self._last_track_name = ""
            self.playerproperties["Metadata"] = dbus.Dictionary({
                'mpris:trackid': dbus.ObjectPath(
                    '/org/mpris/MediaPlayer2/TrackList/0',
                    variant_level=0),
                'mpris:length': dbus.Int64(0),
                'mpris:artUrl': "",
                'xesam:title': 0,
                'xesam:album': "",
                'xesam:artist': dbus.Array([], signature="s")
            }, signature="sv")
            changed["Metadata"] = self.playerproperties["Metadata"]
            changed["Position"] = self.playerproperties["Position"] = dbus.Int64(0)
            changed["PlaybackStatus"] = state

        if len(changed) > 0:
            self.PropertiesChanged(PLAYER_IFACE, changed, [])

    def __update_reduced_tick(self):
        if self.isdebug:
            print("Reduced Tick")
        changed = {}

        if not self.playerproperties["CanPlay"] and self.playerproperties["Shuffle"]:
            self.playerproperties["Shuffle"] = changed["Shuffle"] = False
        else:
            isshuffle = self.driver.is_shuffle()
            if isshuffle is not None and self.playerproperties["Shuffle"] != isshuffle:
                self.playerproperties["Shuffle"] = isshuffle
                changed["Shuffle"] = isshuffle

        if len(changed) > 0:
            self.PropertiesChanged(PLAYER_IFACE, changed, [])

    def __timer_start(self):
        time.sleep(10)
        while not self.quit:
            try:
                self.__update_tick()

                self._timer_i += 1
                if self._timer_i >= 5:
                    self._timer_i = 0
                    self.__update_reduced_tick()

            except WebDriverException as e:
                if "chrome not reachable" in e.msg or "invalid session id" in e.msg or "window already closed" in e.msg:
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
