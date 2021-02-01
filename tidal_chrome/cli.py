#!/usr/bin/python

# Tidal-Chrome MPRIS bridge

# Author: SERVCUBED
# License: AGPL

# MPRIS Specification:
#   https://specifications.freedesktop.org/mpris-spec/latest/
# D-Bus Specification:
#   https://dbus.freedesktop.org/doc/dbus-specification.html

import sys
import dbus
from dbus.mainloop.glib import DBusGMainLoop

from .__init__ import *


def run(isdebug=False):
    DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()

    # Parse URI
    l = None
    if len(sys.argv) > 1:
        if sys.argv[1].startswith("tidal:/"):
            l = sys.argv[1]
        else:
            for pfx in ["https://listen.tidal.com", "https://tidal.com/browse"]:
                if sys.argv[1].startswith(pfx):
                    l = sys.argv[1].replace(pfx, "tidal:/")
                    break

    # Check if already running
    if bus.name_has_owner(BUS_NAME):
        if l is not None:
            bus.call_async(BUS_NAME, OPATH, PLAYER_IFACE, "OpenUri", 's', [l], None, None)
        bus.call_async(BUS_NAME, OPATH, BASE_IFACE, "Raise", '', [], None, None)
        sys.exit(0)

    print("TIDAL-Chrome by SERVCUBED, isdebug=" + str(isdebug))
    from gi.repository import GLib
    loop = GLib.MainLoop()
    a = None

    from . import mpris
    try:
        a = mpris.MPRIS(isdebug, bus, loop)
        if l is not None:
            a.driver._driver.get(l.replace("tidal:/", "https://listen.tidal.com"))
        loop.run()
    except KeyboardInterrupt:
        print("Keyboard interrupt")
        a.quit = True
    finally:
        loop.quit()
        sys.exit(0)


if __name__ == '__main__':
    run(True)
