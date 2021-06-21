# TIDAL-Chrome - an unofficial "official TIDAL client" client

A TIDAL desktop client for Linux built on top of the official web client, but with MPRIS support for desktop
integration.

# Installation

Install Google Chrome from your repositories first. Then install the module with:

    # pip3 install chromedriver_installer
    # pip3 install --upgrade setuptools
    # python3 setup.py install

## Desktop integration

A desktop entry will be installed for easy access from within an application launcher. This will have the path `/usr/share/applications/tidal-google-chrome.desktop`. You may run the following command as root if the installation script fails to register the desktop entry:

    # xdg-mime install /usr/share/applications/tidal-google-chrome.desktop

For other mime type handling, the file `/usr/share/mime/packages/tital-google-chrome.xml`, conforming to [Freedesktop's MIME database specification](https://www.freedesktop.org/wiki/Specifications/shared-mime-info-spec/) will be created and then an attempt will be made to update your mime database using the `update-mime-database` tool.

If either of these fail, the installation will still continue, but it is recommended to run these commands yourself.

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
