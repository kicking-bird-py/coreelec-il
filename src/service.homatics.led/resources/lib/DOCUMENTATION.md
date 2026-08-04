# Technical Code Documentation – Homatics LED Service (`service.homatics.led`)

Comprehensive documentation for developers detailing classes, methods, and helper functions across all project files.

---

## 1. `service.py` (Service Entry Point)

Handles the service initialization at Kodi boot, listens for playback events and settings updates, and continuously monitors whether Kodi is busy (e.g., library scans or active busy dialogs).

### Class: `LedStatusService`
Inherits from `xbmc.Monitor` and `LedStatusMixin`. Manages the background service lifecycle.

* **`__init__(self)`**
  * **Description:** Initializes the service instance.
  * **Behavior:** Calls `_led_init()` to set up hardware state and settings, and resets the busy tracking flag (`self._was_busy = False`).

* **`onNotification(self, sender, method, data)`**
  * **Description:** Listens for Kodi player notifications.
  * **Parameters:** `sender` (event origin), `method` (Kodi event name), `data` (event parameters).
  * **Behavior:** Triggers `_led_on_play_start()` on `Player.OnAVStart` and `_led_on_play_stop()` on `Player.OnStop`.

* **`onSettingsChanged(self)`**
  * **Description:** Handles settings updates live.
  * **Behavior:** Called automatically by Kodi when settings are modified in `settings.xml`, applying new values instantly via `_led_apply_settings()` without requiring a service restart.

* **`_is_busy(self)`**
  * **Description:** Checks if Kodi is performing background or blocking operations.
  * **Returns:** `bool` (`True` if video/music library scans, PVR scans, or busy dialogs are active; otherwise `False`).

* **`run(self)`**
  * **Description:** Main execution loop (Daemon Loop).
  * **Behavior:** Logs service startup, launches the animation thread, and polls Kodi's busy state every second (`BUSY_POLL_SEC`). On service shutdown/abort, ensures a clean thread teardown via `_led_shutdown()`.

---

## 2. `led_status_mixin.py` (Hardware Initialization & Middleware Logic)

Serves as a mixin providing settings reading, safe-boot hardware auto-detection, and interface methods to control the animator thread.

### Class: `LedStatusMixin`

* **`_led_read_settings(self)`**
  * **Description:** Reads all `led_*` keys from `settings.xml` with safe fallbacks to prevent crashes on missing or invalid configurations.
  * **Returns:** `tuple` containing activation status, animation modes (Idle, Play, Busy), and Hex color values.

* **`_led_init(self)`**
  * **Description:** Hardware detection and initial setup.
  * **Behavior:** Verifies if `/sys/class/leds/bct3236/colors` exists. Executes a one-time auto-detect check; if the hardware path is missing on the device, it automatically disables the setting to reflect device capability and instantiates `LedIdleAnimator` accordingly.

* **`_led_start(self)`**
  * **Description:** Starts the background LED animator thread if the hardware is available and feature is enabled.

* **`_led_on_play_start(self)` / `_led_on_play_stop(self)`**
  * **Description:** Signals the animator thread to enter playback mode or return to idle.

* **`_led_on_busy_start(self)` / `_led_on_busy_stop(self)`**
  * **Description:** Signals the animator thread to switch to/from the high-priority busy animation mode.

* **`_led_apply_settings(self)`**
  * **Description:** Applies settings live while the service is running. Updates animation modes/colors or starts/stops the animator thread dynamically based on user toggle.

* **`_led_shutdown(self)`**
  * **Description:** Gracefully stops the animator thread when Kodi shuts down or unloads the addon.

---

## 3. `led_constants.py` (Hardware Paths, Defaults & Color Helpers)

Defines system hardware constants, default fallback values, and color conversion utilities.

* **Key Constants:**
  * `LED_COLORS_PATH`: System sysfs path for the bct3236 LED chip (`/sys/class/leds/bct3236/colors`).
  * `LED_NUM_CHANNELS`: Total number of RGB channels on the LED ring (10 channels).
  * `LED_COLOR_NAMES_HEX`: Predefined list of hex colors mapped to `settings.xml` selection indices.

* **`hsv_to_hex(hue_deg, saturation, value)`**
  * **Description:** Converts HSV (Hue in degrees, Saturation, Value) color coordinates to an `RRGGBB` hex string.
  * **Parameters:** `hue_deg` (0–360°), `saturation` (0.0–1.0), `value` (0.0–1.0).
  * **Returns:** 6-character hex string.

* **`color_hex_from_index(index, fallback_index)`**
  * **Description:** Maps a setting index to a hex color string with fallback bounds checking.

---

## 4. `led_animator.py` (Threaded LED Animation Engine)

Manages a dedicated background thread (`threading.Thread`) that streams color frames to the LED sysfs device node.

### Class: `LedIdleAnimator`

* **`__init__(self, led_path, ...)`**
  * **Description:** Initializes the thread instance, state events (`_stop_event`, `_playing`, `_busy`), writing locks (`threading.Lock`), and mode/color configurations.

* **`stop(self)`**
  * **Description:** Sets `_stop_event` to terminate the thread loop cleanly.

* **`set_idle_settings(...)` / `set_play_settings(...)` / `set_busy_settings(...)`**
  * **Description:** Live-updates mode integers and color hexes for IDLE, PLAYBACK, and BUSY states.

* **`pause_for_playback(self)` / `resume_idle(self)`**
  * **Description:** Sets/clears the `_playing` thread event flag.

* **`pause_for_busy(self)` / `resume_from_busy(self)`**
  * **Description:** Sets/clears the `_busy` thread event flag (takes priority over IDLE and PLAYBACK states).

* **`_write(self, colors_line)`**
  * **Description:** Thread-safe method to write a space-separated string of 10 hex colors to the LED sysfs file.
  * **Fault Tolerance:** Includes consecutive failure counting (`_consecutive_failures`) to prevent log spamming if the device node is temporarily locked.

* **`_write_solid(self, hex_color)`**
  * **Description:** Convenience method that duplicates a single hex color across all 10 channels and writes it to hardware.

* **`run(self)`**
  * **Description:** The core animation loop running on the background thread.
  * **Logic:**
    1. Determines current priority state: `BUSY` > `PLAYBACK` > `IDLE`.
    2. **Solid Color (Node 1):** Writes the static hex color and waits for timeout.
    3. **Color-Cycle Fade (Node 2):** Computes a shifting hue across time for a uniform fading effect.
    4. **Rotating Rainbow (Node 0):** Generates 10 offset hue channels across 360° to create a spinning rainbow effect on the ring.
