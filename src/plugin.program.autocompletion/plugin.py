# -*- coding: utf-8 -*-

# ==============================================================================
# Original Author: Philipp Temminghoff <phil65@kodi.tv> (C) 2015
# License: This program is Free Software; see LICENSE file for details.
# ==============================================================================
#
# [CoreELEC-IL] CURRENT VERSION: v3.0.0
# [CoreELEC-IL] LEAD DEVELOPER: kicking-bird-py | coreELEC-il
# [CoreELEC-IL] UPDATED: 2026
#
# DESCRIPTION: 
# Optimized Autocompletion plugin for Kodi. 
# Re-engineered for Python 3 with specialized POV search logic and 
# zero-dependency architecture.
# ==============================================================================

import xbmc, xbmcaddon, xbmcgui, xbmcplugin, json, sys
from urllib.parse import parse_qsl
import AutoCompletion

# [CoreELEC-IL] Constant Addon ID to ensure consistency and reduce redundant calls.
ADDON_ID = "plugin.program.autocompletion"

def get_kodi_json(method, params):
    """
    [CoreELEC-IL] Enhanced JSON-RPC wrapper: Added try/except error handling 
    to prevent addon crashes during communication issues with Kodi.
    """
    try:
        query_params = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
        return json.loads(xbmc.executeJSONRPC(json.dumps(query_params)))
    except Exception: 
        return {}

def run():
    """
    [CoreELEC-IL] Complete rewrite of the Main Execution Loop:
    1. Optimized logic by removing redundant helper functions to improve performance.
    2. Direct utilization of sys.argv for robust parameter management in Python 3.
    """
    if len(sys.argv) < 2: return
    handle = int(sys.argv[1])
    params = dict(parse_qsl(sys.argv[2][1:]))
    info = params.get("info", "")
    
    if info == 'autocomplete':
        # [CoreELEC-IL] Improved retrieval: Support for 'id' or 'q' keys for skin compatibility.
        search_term = params.get("id") or params.get("q") or ""
        data = AutoCompletion.get_autocomplete_items(search_term, params.get("limit", 10))
        items = []
        
        for result in data:
            label = result.get("label", "")
            # [CoreELEC-IL] Added 'is_suggestion' to distinguish between selection and manual input.
            path = f"plugin://{ADDON_ID}/?info=selectautocomplete&id={label}&is_suggestion=true"
            items.append((path, xbmcgui.ListItem(label), False))
            
        xbmcplugin.addDirectoryItems(handle, items)
        xbmcplugin.endOfDirectory(handle)

    elif info == 'selectautocomplete':
        # [CoreELEC-IL] UI Optimization: Immediate busydialog closure and reduced sleep (100ms).
        xbmc.executebuiltin('Dialog.Close(busydialog)')
        xbmc.sleep(100)
        
        search_term = params.get("id", "")
        cleaned_term = AutoCompletion.clean_for_provider(search_term)
        xbmc.log(f"[AutoCompletion] sending to POV: '{cleaned_term}' (raw: '{search_term}')", xbmc.LOGINFO)
        
        # [CoreELEC-IL] FIX: Apply clean_for_provider here, right before sending to POV,
        # so garbage words like "סרט"/"עונה"/"פרק" don't break the provider's search.
        get_kodi_json('Input.SendText', {"text": cleaned_term, "done": True})

if __name__ == "__main__":
    run()