import os

import xbmc

from led_constants import (
    LED_COLORS_PATH,
    LED_COLOR_NAMES_HEX,
    LED_DEFAULT_IDLE_MODE,
    LED_DEFAULT_IDLE_COLOR_INDEX,
    LED_DEFAULT_PLAY_MODE,
    LED_DEFAULT_PLAY_COLOR_INDEX,
    LED_DEFAULT_BUSY_MODE,
    LED_DEFAULT_BUSY_COLOR_INDEX,
    color_hex_from_index,
)
from led_animator import LedIdleAnimator

# ────────────────────────────────────────────────
#  [CoreELEC-IL] LedStatusMixin — Homatics 4K box status LED
# ────────────────────────────────────────────────
# Manages the Homatics Box R 4K Plus LED status ring (IDLE, PLAYBACK, BUSY states).
# Controlled via settings.xml (led_* settings). Runs in a daemon thread.
# Safely disables itself if the sysfs chip path doesn't exist on the device.


class LedStatusMixin:
    """Status-LED integration for Homatics Box R 4K Plus."""

    def _led_read_settings(self):
        """Read led_* settings with safe fallbacks."""
        try:
            enabled = self.addon.getSettingBool('led_status_enabled')
        except Exception:
            enabled = True
        try:
            idle_mode = self.addon.getSettingInt('led_idle_mode')
        except Exception:
            idle_mode = LED_DEFAULT_IDLE_MODE
        try:
            idle_color_hex = color_hex_from_index(
                self.addon.getSettingInt('led_idle_color'),
                LED_DEFAULT_IDLE_COLOR_INDEX
            )
        except Exception:
            idle_color_hex = LED_COLOR_NAMES_HEX[LED_DEFAULT_IDLE_COLOR_INDEX]
        try:
            play_mode = self.addon.getSettingInt('led_play_mode')
        except Exception:
            play_mode = LED_DEFAULT_PLAY_MODE
        try:
            play_color_hex = color_hex_from_index(
                self.addon.getSettingInt('led_play_color'),
                LED_DEFAULT_PLAY_COLOR_INDEX
            )
        except Exception:
            play_color_hex = LED_COLOR_NAMES_HEX[LED_DEFAULT_PLAY_COLOR_INDEX]
        try:
            busy_mode = self.addon.getSettingInt('led_busy_mode')
        except Exception:
            busy_mode = LED_DEFAULT_BUSY_MODE
        try:
            busy_color_hex = color_hex_from_index(
                self.addon.getSettingInt('led_busy_color'),
                LED_DEFAULT_BUSY_COLOR_INDEX
            )
        except Exception:
            busy_color_hex = LED_COLOR_NAMES_HEX[LED_DEFAULT_BUSY_COLOR_INDEX]

        xbmc.log(
            f"service.homatics.led: Loaded settings -> enabled={enabled}, "
            f"idle_mode={idle_mode}, play_mode={play_mode}, busy_mode={busy_mode}",
            level=xbmc.LOGDEBUG
        )

        return (enabled, idle_mode, idle_color_hex, play_mode, play_color_hex,
                busy_mode, busy_color_hex)

    def _led_init(self):
        self._led_hw_available = os.path.exists(LED_COLORS_PATH)
        (self._led_status_enabled, self._led_idle_mode,
         self._led_idle_color_hex, self._led_play_mode,
         self._led_play_color_hex, self._led_busy_mode,
         self._led_busy_color_hex) = self._led_read_settings()

        # One-time auto-detect on first boot: if the LED chip is missing, 
        # automatically turn off the toggle in settings to match reality.
        try:
            hw_check_done = self.addon.getSettingBool('led_hw_autodetect_done')
        except Exception:
            hw_check_done = False

        if not hw_check_done:
            if not self._led_hw_available and self._led_status_enabled:
                try:
                    self.addon.setSettingBool('led_status_enabled', False)
                    self._led_status_enabled = False
                    xbmc.log(
                        "service.homatics.led: LED chip not found on this device — "
                        "auto-disabling led_status_enabled (one-time)",
                        level=xbmc.LOGINFO
                    )
                except Exception:
                    pass
            try:
                self.addon.setSettingBool('led_hw_autodetect_done', True)
            except Exception:
                pass

        self._led_available = self._led_hw_available and self._led_status_enabled

        if self._led_hw_available:
            self._led_animator = LedIdleAnimator(
                LED_COLORS_PATH,
                idle_mode=self._led_idle_mode,
                idle_color_hex=self._led_idle_color_hex,
                play_mode=self._led_play_mode,
                play_color_hex=self._led_play_color_hex,
                busy_mode=self._led_busy_mode,
                busy_color_hex=self._led_busy_color_hex,
            )
        else:
            self._led_animator = None
            xbmc.log(
                "service.homatics.led: LED path %s not found — status LED feature "
                "disabled on this device" % LED_COLORS_PATH,
                level=xbmc.LOGINFO
            )

    def _led_start(self):
        if self._led_available and self._led_animator and not self._led_animator.is_alive():
            self._led_animator.start()

    def _led_on_play_start(self):
        if self._led_available and self._led_animator:
            xbmc.log("service.homatics.led: Playback started - pausing animator for playback", level=xbmc.LOGDEBUG)
            self._led_animator.pause_for_playback()

    def _led_on_play_stop(self):
        if self._led_available and self._led_animator:
            xbmc.log("service.homatics.led: Playback stopped - resuming idle state", level=xbmc.LOGDEBUG)
            self._led_animator.resume_idle()

    def _led_on_busy_start(self):
        """Called when the device switches to busy/scanning state."""
        if self._led_available and self._led_animator:
            xbmc.log("service.homatics.led: Busy state started - pausing for busy/scan", level=xbmc.LOGDEBUG)
            self._led_animator.pause_for_busy()

    def _led_on_busy_stop(self):
        """Called when busy state ends and previous state resumes."""
        if self._led_available and self._led_animator:
            xbmc.log("service.homatics.led: Busy state ended - resuming previous state", level=xbmc.LOGDEBUG)
            self._led_animator.resume_from_busy()

    def _led_apply_settings(self):
        """Live-apply settings changes without restarting the service."""
        if not self._led_hw_available:
            return

        (new_enabled, new_idle_mode, new_idle_color_hex,
         new_play_mode, new_play_color_hex, new_busy_mode,
         new_busy_color_hex) = self._led_read_settings()

        xbmc.log(
            f"service.homatics.led: Applying new settings live -> idle_mode={new_idle_mode}, "
            f"play_mode={new_play_mode}, busy_mode={new_busy_mode}",
            level=xbmc.LOGDEBUG
        )

        self._led_status_enabled = new_enabled
        self._led_idle_mode       = new_idle_mode
        self._led_idle_color_hex  = new_idle_color_hex
        self._led_play_mode       = new_play_mode
        self._led_play_color_hex  = new_play_color_hex
        self._led_busy_mode       = new_busy_mode
        self._led_busy_color_hex  = new_busy_color_hex

        was_available = self._led_available
        self._led_available = self._led_hw_available and new_enabled

        if self._led_available:
            if self._led_animator is None or not self._led_animator.is_alive():
                self._led_animator = LedIdleAnimator(
                    LED_COLORS_PATH,
                    idle_mode=new_idle_mode,
                    idle_color_hex=new_idle_color_hex,
                    play_mode=new_play_mode,
                    play_color_hex=new_play_color_hex,
                    busy_mode=new_busy_mode,
                    busy_color_hex=new_busy_color_hex,
                )
                self._led_animator.start()
                xbmc.log("service.homatics.led: LED status feature ENABLED", level=xbmc.LOGINFO)
            else:
                self._led_animator.set_idle_settings(new_idle_mode, new_idle_color_hex)
                self._led_animator.set_play_settings(new_play_mode, new_play_color_hex)
                self._led_animator.set_busy_settings(new_busy_mode, new_busy_color_hex)
        else:
            if was_available and self._led_animator:
                self._led_animator.stop()
                xbmc.log("service.homatics.led: LED status feature DISABLED", level=xbmc.LOGINFO)

    def _led_shutdown(self):
        if self._led_animator:
            self._led_animator.stop()