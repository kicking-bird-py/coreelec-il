# -*- coding: utf8 -*-

# ==============================================================================
# Original Author: Philipp Temminghoff <phil65@kodi.tv> (C) 2015
# License: This program is Free Software; see LICENSE file for details.
# ==============================================================================
#
# [CoreELEC-IL] CURRENT VERSION: v3.0.0
# [CoreELEC-IL] LEAD DEVELOPER: kicking-bird-py | coreELEC-IL
# [CoreELEC-IL] UPDATED: 2026
#
# DESCRIPTION: 
# Optimized Autocompletion engine. 
# Features high-performance caching, specialized POV data cleaning, 
# and full Python 3 compatibility with a zero-dependency architecture.
# ==============================================================================

import os, time, json, hashlib, requests, xbmcaddon, xbmcvfs
from urllib.parse import quote_plus

# [CoreELEC-IL] Redefined constants and simplified path management for Python 3.
# Removed complex 'special://' logic and legacy PY2 checks for better stability.
SCRIPT_ID = "plugin.program.autocompletion"
ADDON = xbmcaddon.Addon(SCRIPT_ID)
PROFILE_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo("profile"))

# [CoreELEC-IL] Centralized performance settings.
FETCH_TIMEOUT = 10 
CACHE_DAYS = 7 

def clean_for_provider(text):
    """
    [CoreELEC-IL] EXCLUSIVE POV OPTIMIZATION:
    New specialized function to strip "garbage" keywords (e.g., "Direct Watch", "Season").
    This is triggered only upon selection to maximize search accuracy in POV scrapers.
    """
    if not text: return ""
    garbage = ["סדרה", "סרטים", "סרט", "ביקורת", "ביקורות", "עונה", "פרק", "צפייה ישירה", "הורדה", "טריילר"]
    cleaned = text
    for word in garbage:
        cleaned = cleaned.replace(word, " ")
    return " ".join(cleaned.split())

def fetch_with_cache(url):
    """
    [CoreELEC-IL] REFACTORED CACHE ENGINE:
    1. Replaced the bulky 'get_JSON_response' and 'save_to_file' with a streamlined logic.
    2. Uses MD5 hashing for unique cache keys and handles directory creation on-the-fly.
    3. Implemented a strict 10s timeout to prevent UI freezing during network drops.
    """
    if not xbmcvfs.exists(PROFILE_PATH): xbmcvfs.mkdirs(PROFILE_PATH)

    hashed_url = hashlib.md5(url.encode('utf-8')).hexdigest()
    cache_file = os.path.join(PROFILE_PATH, f"{hashed_url}.json")
    
    if xbmcvfs.exists(cache_file):
        if (time.time() - os.path.getmtime(cache_file)) < (CACHE_DAYS * 86400):
            try:
                with xbmcvfs.File(cache_file) as f: return json.loads(f.read())
            except: pass
    try:
        # [CoreELEC-IL] Using modern 'requests' with a global timeout instead of legacy loops.
        r = requests.get(url, timeout=FETCH_TIMEOUT)
        if r.ok:
            data = r.json()
            with xbmcvfs.File(cache_file, 'w') as f: f.write(json.dumps(data))
            return data
    except: pass
    return None

def get_autocomplete_items(search_str, limit=10):
    """
    [CoreELEC-IL] OPTIMIZED PROVIDER LOGIC:
    1. Removed the complex Class-based Provider system (Google/Bing/Netflix) to eliminate overhead.
    2. Hardcoded Hebrew (hl=he) and Chrome client for the fastest and most relevant results in Israel.
    3. Removed legacy 'prep_search_str' logic which caused issues with modern Kodi RTL handling.
    """
    if not search_str: return []
    url = f'https://suggestqueries.google.com/complete/search?client=chrome&q={quote_plus(search_str.strip())}&hl=he'
    data = fetch_with_cache(url)
    if data:
        # Returns raw labels for the UI; cleaning only happens later via 'clean_for_provider'.
        return [{"label": res, "search_string": res} for res in data[1][:int(limit)]]
    return []