# TIDAL-Chrome - an unofficial "official TIDAL client" client

A TIDAL desktop client for Linux built on top of the official web client, but with MPRIS support for desktop 
integration.

# Installation

Install Google Chrome and Chrome's flash player plugin from your repositories first. Then install the module with:

    # pip install chromedriver_installer 
    # python setup.py install
    # cp tidal-google-chrome.desktop /usr/share/applications/tidal-google-chrome.desktop

# Using TIDAL-Chrome

1. Launch `TIDAL` in your application launcher or run `tidal-chrome` in your favourite terminal.
2. A new Chrome window will be opened. Sign in to TIDAL.
3. Play something. You may need to follow through on the prompts to install/run flash.


# Troubleshooting

First, ensure you have chromedriver installed. The `chromedriver_installer` pip package must be manually installed. 

If the TIDAL webpage is stuck at the loading image, then try clearing the cache. The easiest way to do this is to 
close all app windows and delete the user data folder `~/.config/tidal-google-chrome`.