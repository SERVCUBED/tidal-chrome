import os

__version__ = '1.0'
__description__ = 'Tidal-Chrome MPRIS bridge'
requires = ['selenium', 'gi', 'dbus-python']

with open(os.path.join(os.path.dirname(__file__), '..', 'README.md')) as f:
    README = f.read()

# Tidal-Chrome MPRIS bridge

# Author: SERVCUBED
# License: GPL

# Dependencies:
# chromedriver (AUR), google-chrome, selenium (pip/distro)
