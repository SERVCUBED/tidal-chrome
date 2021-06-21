# TIDAL-Chrome - an unofficial "official TIDAL client" client

A TIDAL desktop client for Linux built on top of the official web client, but with MPRIS support for desktop
integration.

# Installation

Install Google Chrome from your repositories first. Then install the module with:

    # pip3 install chromedriver_installer
    # pip3 install --upgrade setuptools
    # python3 setup.py install
    # update-mime-database /usr/share/mime
    # xdg-mime install /usr/share/applications/tidal-google-chrome.desktop

# Using TIDAL-Chrome

1. Launch `TIDAL` in your application launcher or run `tidal-chrome` in your favourite terminal.
2. A new Chrome window will be opened. Sign in to TIDAL.
3. Play some music.

The `tidal-chrome` executable accepts command line options and searches for a configuration file with the
default path of `~/.config/tidal-chrome-prefs.json`. This path can be changed with the `--conf` command
line argument. You can run `tidal-chrome --create-conf` to create the default JSON configuration file.

# Troubleshooting

First, ensure you have chromedriver installed. The `chromedriver_installer` pip package must be manually installed.

If the TIDAL webpage is stuck at the loading image, then try clearing the cache. The easiest way to do this is to
close all app windows and delete the user data folder `~/.config/tidal-google-chrome`.
