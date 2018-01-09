# TIDAL-Chrome - an unofficial "official TIDAL client" client

A TIDAL desktop client for Linux built on top of the official web client, but with MPRIS support for desktop 
integration.

# Installation

Install Google Chrome and Chrome's flash player plugin from your repositories first. Then install the module with:

    # pip install chromedriver_installer 
    # python setup.py install

# Using TIDAL-Chrome

1. Launch `tidal-chrome` in your favourite terminal
2. A new Chrome window will be opened. Sign in to TIDAL.
3. Play something. You may need to follow through on the prompts to install/run flash.

Currently, the only way to quit completely (other than `pkill`) is to Ctrl+C on the terminal window and wait for 
the running threads to break/quit. This can take up to 30 seconds (the length of the longest timer)
