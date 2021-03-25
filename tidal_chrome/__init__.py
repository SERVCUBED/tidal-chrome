version = '1.7.2'
description = 'Tidal-Chrome MPRIS bridge'
requires = ['selenium', 'gobject', 'dbus-python']

OPATH = "/org/mpris/MediaPlayer2"
BASE_IFACE = "org.mpris.MediaPlayer2"
PLAYER_IFACE = "org.mpris.MediaPlayer2.Player"
BUS_NAME = "org.mpris.MediaPlayer2.tidal-chrome"
DEFAULT_CONF_PATH = "~/.config/tidal-chrome-prefs.json"

# Tidal-Chrome MPRIS bridge

# Author: SERVCUBED
# License: GPL

# Dependencies:
# chromedriver (AUR), google-chrome, selenium (pip/distro)
