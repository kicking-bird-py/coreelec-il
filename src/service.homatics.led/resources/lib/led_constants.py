import colorsys

# ────────────────────────────────────────────────
#  [CoreELEC-IL] LED constants — Homatics 4K box status LED
# ────────────────────────────────────────────────
# Hardware path for the bct3236 LED controller chip (10 individual RGB channels).
# Supports writing space-separated hex values for animations or solid states.

LED_COLORS_PATH  = "/sys/class/leds/bct3236/colors"
LED_NUM_CHANNELS = 10

# ── Idle rainbow animation (led_idle_mode = 0) ──
LED_RAINBOW_HUE_STEP_DEG = 30
LED_RAINBOW_INTERVAL_SEC = 0.1
LED_RAINBOW_BRIGHTNESS   = 0.45

# ── Idle color-cycle animation (led_idle_mode = 2) — Homatics-style fade ──
LED_CYCLE_HUE_STEP_DEG = 1
LED_CYCLE_INTERVAL_SEC = 0.15
LED_CYCLE_BRIGHTNESS   = 0.5

# ── Named color list shown in settings.xml (must match indices & order) ──
LED_COLOR_NAMES_HEX = [
    "ff0000",  # 0 Red
    "ff6a00",  # 1 Orange
    "ffd500",  # 2 Yellow
    "00ff40",  # 3 Green
    "00ffc8",  # 4 Turquoise
    "0080ff",  # 5 Blue
    "8a5fbf",  # 6 Purple
    "ff3fa4",  # 7 Pink
    "ffffff",  # 8 White
    "000000",  # 9 Off / black
]

# ── Fallback default settings (mirroring settings.xml defaults) ──
LED_DEFAULT_IDLE_MODE        = 0  # 0 = rainbow, 1 = solid, 2 = color-cycle
LED_DEFAULT_IDLE_COLOR_INDEX = 9  # Off
LED_DEFAULT_PLAY_MODE        = 1  # 0 = rainbow, 1 = solid, 2 = color-cycle
LED_DEFAULT_PLAY_COLOR_INDEX = 6  # Purple
LED_DEFAULT_BUSY_MODE        = 2  # 0 = rainbow, 1 = solid, 2 = color-cycle
LED_DEFAULT_BUSY_COLOR_INDEX = 0  # Red


def hsv_to_hex(hue_deg, saturation, value):
    """Convert HSV (hue in degrees) to an 'RRGGBB' hex string."""
    r, g, b = colorsys.hsv_to_rgb((hue_deg % 360) / 360.0, saturation, value)
    return "%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


def color_hex_from_index(index, fallback_index):
    """Map a color setting index to its 'rrggbb' hex string with fallback."""
    try:
        index = int(index)
    except (TypeError, ValueError):
        index = fallback_index
    if index < 0 or index >= len(LED_COLOR_NAMES_HEX):
        index = fallback_index
    return LED_COLOR_NAMES_HEX[index]