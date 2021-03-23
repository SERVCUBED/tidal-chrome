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
from typing import Optional

from .__init__ import *


def run(isdebug: Optional[bool] = None):
    DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()

    # Parse URI
    import argparse
    par = argparse.ArgumentParser()#description=__description__)
    par.add_argument("-v", "--verbose", dest="isdebug", action="store_true", help="Enable debugging mode")
    par.add_argument("-d", "--no-conf", dest="default_only", action="store_true",
                     help="Use the default configuration file values; do not write the configuration file if it does "
                          "not exist.")
    par.add_argument("-c", "--conf", nargs=1, action="store",
                     help="Path to JSON configuration file (default: \"%(default)s\").", default=DEFAULT_CONF_PATH,
                     metavar="FILE")
    par.add_argument("-i", "--interactive", dest="interactive", action="store_true",
                     help="Enable interactive prompt for debugging.")
    par.add_argument("URI", nargs="?", help="TIDAL URI to open.", metavar="tidal://...|https://listen.tidal.com/...")
    args = par.parse_args()

    if args.isdebug:
        isdebug = True

    l = None
    if args.URI is not None:
        if args.URI.startswith("tidal:/"):
            l = args.URI
        else:
            for pfx in ["https://listen.tidal.com", "https://tidal.com/browse"]:
                if args.URI.startswith(pfx):
                    l = args.URI.replace(pfx, "tidal:/")
                    break

    # Check if already running
    if bus.name_has_owner(BUS_NAME):
        if l is not None:
            bus.call_async(BUS_NAME, OPATH, PLAYER_IFACE, "OpenUri", 's', [l], None, None)
        bus.call_async(BUS_NAME, OPATH, BASE_IFACE, "Raise", '', [], None, None)
        sys.exit(0)

    print("TIDAL-Chrome by SERVCUBED")
    from gi.repository import GLib
    loop = GLib.MainLoop()
    t_c = None

    from . import mpris, preferences
    prefs = preferences.Preferences(default_only=args.default_only, path=args.conf)
    if isdebug is None:
        isdebug = prefs.values["force_is_debug_if_stdin_isatty"] and sys.stdin.isatty()
    print("isdebug=" + str(isdebug))
    try:
        t_c = mpris.MPRIS(isdebug, bus, loop, prefs)
        if l is not None:
            t_c.driver._driver.get(l.replace("tidal:/", "https://listen.tidal.com"))
        if (prefs.values["force_interactive_prompt_if_stdin_isatty"] or args.interactive) and sys.stdin.isatty():
            import threading
            thr = threading.Thread(target=loop.run)
            thr.start()
            from IPython import embed
            print ("""
Starting interactive mode. The MPRIS interface can be accessed with \"t_c\";
Hints:\tt_c.quit() to quit;
\tt_c.driver to access tidal_chrome_driver.Driver;
\tt_c.driver._driver to access Selenium WebDriver;
\tprefs.values to access preferences dictionary. Note that some changes only take affect after a restart;
\tprefs.Save(path=None) to save preferences to <path>[=None: current set path].""")
            embed()
        else:
            loop.run()
    except KeyboardInterrupt:
        print("Keyboard interrupt")
        if t_c is not None:
            t_c.quit = True
        loop.quit()
    except Exception as e:
        raise e
    finally:
        loop.quit()
        sys.exit(0)


if __name__ == '__main__':
    run(True)
