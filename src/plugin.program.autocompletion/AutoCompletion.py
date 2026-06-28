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

import os, time, json, hashlib, requests, re, xbmcaddon, xbmcvfs
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
    [CoreELEC-IL] EXCLUSIVE POV OPTIMIZATION - v3 (Hebrew + English dictionary edition):
    Strips Google Suggest "noise" so the provider receives a clean title only.

    Design:
    1. Categorized garbage dictionary, mixing Hebrew and English entries, so both
       languages get filtered with the boundary logic that fits them.
    2. Hebrew prefix-awareness: Hebrew attaches prefixes like ה-/ו-/ש-/ב-/ל-/מ-
       directly onto words ("הסדרה", "ולצפייה"). A naive word match misses these,
       so each Hebrew garbage word is matched with an OPTIONAL prefix cluster
       before it.
    3. English uses standard \b word boundaries, case-insensitive, so "Season",
       "SEASON", "season" all match, but "seasonal" does not.
    4. Word-boundary safe in both languages, e.g. "סרט" won't eat "מסרטט", and
       "part" won't eat "department".
    5. SEASON/EPISODE/PART words (Hebrew + English) also consume a trailing
       number or range right after them (e.g. "Season 8", "עונה 1-3"), since a
       stray leftover number breaks the provider's search.
    6. Multi-word phrases are matched before their sub-words within the same
       category, so longer phrases don't get partially eaten and leave stray
       leftovers (e.g. "Full Movie" before "Movie").
    7. Cleans leftover punctuation/empty-parentheses/double-spaces at the end.
    """
    if not text:
        return ""

    # Hebrew prefix letters that can stack onto the start of a word
    # (ה-, ו-, ש-, ב-, כ-, ל-, מ- and simple combinations like "וה", "שב", "ול")
    HE_PREFIX = r"(?:[והשבכלמ]{1,2})?"
    # Boundary: start/end of string, or a non-Hebrew-letter character
    HE_START = r"(?<![\u05D0-\u05EA])"
    HE_END = r"(?![\u05D0-\u05EA])"

    def is_hebrew(word):
        return bool(re.search(r"[\u05D0-\u05EA]", word))

    def word_pattern(word):
        """Build a boundary-safe match pattern for a single garbage word/phrase."""
        if is_hebrew(word):
            return HE_START + HE_PREFIX + re.escape(word) + HE_END
        return r"(?i)\b" + re.escape(word) + r"\b"

    # --- Categorized garbage dictionary (Hebrew + English) -------------------
    GARBAGE = {
        # Words typically followed by a number/range that must be removed too
        # e.g. "עונה 8", "Season 8", "Episode 3-5", "פרק 12"
        "season_episode": [
            "עונה", "עונות", "פרק", "פרקים", "חלק", "חלקים",
            "Season", "Seasons", "Episode", "Episodes", "Part", "Parts", "Ep",
        ],
        # Plain content-type words with no attached number
        "content_type": [
            "סדרה", "סדרות", "סרטים", "סרט", "סרט מלא", "אנימה", "טריילר",
            "פרומו", "קליפ",
            "Full Movie", "Movie", "Series", "TV Series", "Anime", "Trailer",
            "Promo", "Clip", "Teaser",
        ],
        # Review / discussion noise
        "review": [
            "ביקורת", "ביקורות", "סיכום", "ספוילר", "ספוילרים",
            "Review", "Reviews", "Recap", "Spoiler", "Spoilers",
            "Ending Explained",
        ],
        # Streaming / download / quality phrases (mostly multi-word, no number)
        "streaming_quality": [
            "צפייה ישירה", "צפייה online", "לצפייה ישירה", "לצפייה", "צפייה",
            "הורדה", "להורדה", "הורדת", "מלא לצפייה", "אונליין", "סטרימינג",
            "מתורגם", "מתורגמת", "מדובב", "מדובבת", "כתוביות",
            "באיכות גבוהה", "באיכות", "איכות גבוהה", "איכות הטובה ביותר",
            "HD", "FULL HD", "4K", "1080p", "720p", "480p", "BluRay", "WEB-DL",
            "Watch Online", "Watch Free", "Free Download", "Download Free",
            "Download", "Streaming", "Stream", "Dubbed", "Subbed", "Subtitled",
            "Subtitles", "English Subtitles", "High Quality", "Full HD",
        ],
        # Generic site/portal noise that sometimes rides along in suggestions
        "site_noise": [
            "לצפיה", "ויקיפדיה",
            "Watch Online Free", "Online Free", "Free Online",
            "Watch Free Online", "Wiki", "Wikipedia", "IMDB",
            "Rotten Tomatoes", "Cast", "Cast List", "Release Date",
            "Where To Watch",
        ],
    }

    cleaned = text

    # 1. Season/episode/part words: eat the word + optional range/number after it
    #    e.g. "עונה 8", "Season 8", "Episode 1-3"
    for word in sorted(GARBAGE["season_episode"], key=len, reverse=True):
        base = word_pattern(word)
        pattern_with_num = base + r"\s*[-–:.]?\s*\d+(?:\s*[-–]\s*\d+)?"
        cleaned = re.sub(pattern_with_num, " ", cleaned)
        # also catch the bare word with no number attached
        cleaned = re.sub(base, " ", cleaned)

    # 2. All other categories: phrase removal, longest phrases first so a
    #    multi-word entry (e.g. "Full Movie") is consumed whole before its
    #    sub-word (e.g. "Movie") could partially match and leave leftovers.
    for category in ("content_type", "review", "streaming_quality", "site_noise"):
        for word in sorted(GARBAGE[category], key=len, reverse=True):
            cleaned = re.sub(word_pattern(word), " ", cleaned)

    # 3. Tidy up: stray brackets/parentheses left empty, dashes, dots, extra spaces
    cleaned = re.sub(r"[\(\[\{]\s*[\)\]\}]", " ", cleaned)   # empty () [] {}
    cleaned = re.sub(r"[-–_|]{1,}", " ", cleaned)            # stray separators
    cleaned = re.sub(r"\s{2,}", " ", cleaned)

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