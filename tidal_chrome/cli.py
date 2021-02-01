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
from gi.repository import GLib

from .__init__ import *


def run(isdebug=False):
    print("TIDAL-Chrome by SERVCUBED, isdebug=" + str(isdebug))
    DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()
    loop = GLib.MainLoop()
    a = None

    from . import mpris
    try:
        a = mpris.MPRIS(isdebug, bus, loop)
        loop.run()
    except KeyboardInterrupt:
        print("Keyboard interrupt")
        a.quit = True
    finally:
        loop.quit()
        sys.exit(0)


if __name__ == '__main__':
    run(True)
