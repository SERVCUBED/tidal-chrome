__version__ = '1.4'
__description__ = 'Tidal-Chrome MPRIS bridge'
requires = ['selenium', 'gobject', 'dbus-python']

OPATH = "/org/mpris/MediaPlayer2"
BASE_IFACE = "org.mpris.MediaPlayer2"
PLAYER_IFACE = "org.mpris.MediaPlayer2.Player"
BUS_NAME = "org.mpris.MediaPlayer2.tidal-chrome"

# Tidal-Chrome MPRIS bridge

# Author: SERVCUBED
# License: GPL

# Dependencies:
# chromedriver (AUR), google-chrome, selenium (pip/distro)
