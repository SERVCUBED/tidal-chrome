# Part of the Tidal-Chrome MPRIS bridge
# Author: SERVCUBED 2018-
# License: AGPL

import os
import json
from typing import Optional

from .__init__ import *


class Preferences:

    def __init__(self, default_only: bool = False, path: Optional[str] = None,
                 should_create_if_not_exist: bool = False):
        self.encoder = self.path = None
        self.values = {
            "chrome_binary_path": None,
            "profile_path": "~/.config/tidal-google-chrome/",
            "chromedriver_binary_path": "chromedriver",
            "enable_kiosk_mode": False,
            "force_is_debug_if_stdin_isatty": False,
            "force_interactive_prompt_if_stdin_isatty": False,
            "force_quit_interactive_prompt_on_driver_quit": True,
            # TODO "scrensaver_inhibitor": None
        }
        if default_only:
            return

        if path is None:
            path = DEFAULT_CONF_PATH
        self.path = os.path.expanduser(path)
        if not os.path.isfile(self.path):
            if should_create_if_not_exist:
                self.save()
            return

        f = newvalues = None
        try:
            f = open(self.path, mode="rt", encoding="UTF-8")
            newvalues = json.JSONDecoder().decode(f.read())
        except IOError as e:
            print("Error reading configuration file " + self.path, e)
        except json.JSONDecodeError as e:
            print("JSON Error reading decoding configuration file " + self.path, e)
        finally:
            if f is not None:
                f.close()

        if newvalues is None:
            return
        for k, v in newvalues.items():
            if k in self.values:
                self.values[k] = v

    def save(self, path: Optional[str] = None) -> None:
        """
        Save the current preferences as a json file.

        :Args
          path: String, filename to save JSON values.
        """
        if path is None:
            path = self.path

        if path is None:
            raise ValueError("File path is not defined.")
        else:
            path = os.path.expanduser(path)

        if not self.encoder:
            self.encoder = json.JSONEncoder()

        f = None
        try:
            f = open(path, mode="wt", encoding="UTF-8")
            for c in self.encoder.iterencode(self.values):
                f.write(c)
        except IOError as e:
            print("Error writing configuration file " + path, e)
        finally:
            if f is not None:
                f.close()
