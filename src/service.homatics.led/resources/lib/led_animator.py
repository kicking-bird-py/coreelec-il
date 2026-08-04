import threading

import xbmc

from led_constants import (
    LED_NUM_CHANNELS,
    LED_RAINBOW_HUE_STEP_DEG,
    LED_RAINBOW_INTERVAL_SEC,
    LED_RAINBOW_BRIGHTNESS,
    LED_CYCLE_HUE_STEP_DEG,
    LED_CYCLE_INTERVAL_SEC,
    LED_CYCLE_BRIGHTNESS,
    LED_COLOR_NAMES_HEX,
    LED_DEFAULT_IDLE_MODE,
    LED_DEFAULT_IDLE_COLOR_INDEX,
    LED_DEFAULT_PLAY_MODE,
    LED_DEFAULT_PLAY_COLOR_INDEX,
    LED_DEFAULT_BUSY_MODE,
    LED_DEFAULT_BUSY_COLOR_INDEX,
    hsv_to_hex,
)


class LedIdleAnimator(threading.Thread):
    """Background thread managing LED animation states (IDLE, PLAYBACK, BUSY)."""

    def __init__(self, led_path, idle_mode=LED_DEFAULT_IDLE_MODE,
                 idle_color_hex=None, play_mode=LED_DEFAULT_PLAY_MODE,
                 play_color_hex=None, busy_mode=LED_DEFAULT_BUSY_MODE,
                 busy_color_hex=None):
        super().__init__(daemon=True)
        self.led_path       = led_path
        self._stop_event    = threading.Event()
        self._playing       = threading.Event()
        self._busy          = threading.Event()
        self._write_lock    = threading.Lock()
        self._consecutive_failures = 0

        self.idle_mode      = idle_mode
        self.idle_color_hex = idle_color_hex or LED_COLOR_NAMES_HEX[LED_DEFAULT_IDLE_COLOR_INDEX]
        self.play_mode      = play_mode
        self.play_color_hex = play_color_hex or LED_COLOR_NAMES_HEX[LED_DEFAULT_PLAY_COLOR_INDEX]
        self.busy_mode      = busy_mode
        self.busy_color_hex = busy_color_hex or LED_COLOR_NAMES_HEX[LED_DEFAULT_BUSY_COLOR_INDEX]

    def stop(self):
        self._stop_event.set()

    def set_idle_settings(self, idle_mode, idle_color_hex):
        """Update idle mode/color live."""
        self.idle_mode      = idle_mode
        self.idle_color_hex = idle_color_hex

    def set_play_settings(self, play_mode, play_color_hex):
        """Update playback mode/color live."""
        self.play_mode      = play_mode
        self.play_color_hex = play_color_hex

    def set_busy_settings(self, busy_mode, busy_color_hex):
        """Update busy-state mode/color live."""
        self.busy_mode      = busy_mode
        self.busy_color_hex = busy_color_hex

    def pause_for_playback(self):
        """Switch to playback mode."""
        xbmc.log("service.homatics.led: Animator paused for playback", level=xbmc.LOGDEBUG)
        self._playing.set()

    def resume_idle(self):
        """Resume idle mode."""
        xbmc.log("service.homatics.led: Animator resuming idle", level=xbmc.LOGDEBUG)
        self._playing.clear()

    def pause_for_busy(self):
        """Switch to busy mode (takes priority)."""
        xbmc.log("service.homatics.led: Animator paused for busy state", level=xbmc.LOGDEBUG)
        self._busy.set()

    def resume_from_busy(self):
        """Clear busy state and fall back to playback or idle."""
        xbmc.log("service.homatics.led: Animator resumed from busy state", level=xbmc.LOGDEBUG)
        self._busy.clear()

    def _write(self, colors_line):
        """Write one frame to the LED chip with safe retry handling."""
        try:
            with self._write_lock:
                with open(self.led_path, "w") as f:
                    f.write(colors_line)
            self._consecutive_failures = 0
            return True
        except Exception as e:
            self._consecutive_failures += 1
            if self._consecutive_failures == 1 or self._consecutive_failures % 20 == 0:
                xbmc.log(
                    "service.homatics.led: LED write failed at %s (%s) — retrying "
                    "(%d failures so far)" % (
                        self.led_path, str(e), self._consecutive_failures
                    ),
                    level=xbmc.LOGINFO
                )
            return False

    def _write_solid(self, hex_color):
        line = " ".join([hex_color] * LED_NUM_CHANNELS)
        return self._write(line)

    def run(self):
        xbmc.log("service.homatics.led: LED idle animation started", level=xbmc.LOGINFO)
        base_hue = 0.0
        try:
            while not self._stop_event.is_set():
                if self._busy.is_set():
                    mode      = self.busy_mode
                    solid_hex = self.busy_color_hex
                elif self._playing.is_set():
                    mode      = self.play_mode
                    solid_hex = self.play_color_hex
                else:
                    mode      = self.idle_mode
                    solid_hex = self.idle_color_hex

                if mode == 1:
                    self._write_solid(solid_hex)
                    self._stop_event.wait(timeout=0.5)
                    continue

                if mode == 2:
                    hex_color = hsv_to_hex(base_hue, 1.0, LED_CYCLE_BRIGHTNESS)
                    self._write_solid(hex_color)
                    base_hue = (base_hue + LED_CYCLE_HUE_STEP_DEG) % 360
                    self._stop_event.wait(timeout=LED_CYCLE_INTERVAL_SEC)
                    continue

                colors = [
                    hsv_to_hex(
                        base_hue + i * (360.0 / LED_NUM_CHANNELS),
                        1.0,
                        LED_RAINBOW_BRIGHTNESS
                    )
                    for i in range(LED_NUM_CHANNELS)
                ]
                self._write(" ".join(colors))

                base_hue = (base_hue + LED_RAINBOW_HUE_STEP_DEG) % 360
                self._stop_event.wait(timeout=LED_RAINBOW_INTERVAL_SEC)
        except Exception as e:
            xbmc.log("service.homatics.led: LED animator ERROR: %s" % str(e), level=xbmc.LOGERROR)
        xbmc.log("service.homatics.led: LED idle animation stopped", level=xbmc.LOGINFO)