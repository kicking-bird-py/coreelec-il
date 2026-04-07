# -*- coding: utf8 -*-
# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details
# Modified and maintained by kicking-bird-py | coreELEC-IL
# Integrated All-in-One Version

"""
CoreELEC-IL Edition Changes:
1. Simplified Logic: Replaced original complex engine with a direct Settings Launcher.
2. Logging: Added version tracking and process status to kodi.log for easier debugging.
3. UTF-8 Support: Ensured full compatibility for Hebrew strings and comments.
"""

import xbmcaddon
import xbmc

ADDON_ID = "plugin.program.autocompletion"
ADDON = xbmcaddon.Addon(ADDON_ID)

def run():
    xbmc.log(f"[CoreELEC-IL] Opening settings for {ADDON_ID}", xbmc.LOGINFO)
    ADDON.openSettings()

if __name__ == "__main__":
    run()