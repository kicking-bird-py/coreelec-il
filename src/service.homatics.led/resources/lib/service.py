import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import xbmc
import xbmcaddon

from led_status_mixin import LedStatusMixin


class LedStatusService(xbmc.Monitor, LedStatusMixin):
    """Entry point class, run by resources/lib/service.py at boot."""

    # Busy-state poll interval (seconds) — no Kodi notification exists for it.
    BUSY_POLL_SEC = 1.0

    def __init__(self):
        super().__init__()
        self.addon = xbmcaddon.Addon()
        self._led_init()
        self._was_busy = False

    def onNotification(self, sender, method, data):
        """Playback start/stop -> switch LED effect."""

        if method == "Player.OnAVStart":
            self._led_on_play_start()
        elif method == "Player.OnStop":
            self._led_on_play_stop()

    def onSettingsChanged(self):
        """Live-apply led_* settings, no restart needed."""

        self._led_apply_settings()

    def _is_busy(self):
        """Library/PVR scan or a busy dialog in progress."""

        return (
            xbmc.getCondVisibility("Library.IsScanningVideo") or
            xbmc.getCondVisibility("Library.IsScanningMusic") or
            xbmc.getCondVisibility("Pvr.IsScanning") or
            xbmc.getCondVisibility("Window.IsActive(busydialog)") or
            xbmc.getCondVisibility("Window.IsActive(busydialognocancel)")
        )

    def run(self):
        """Runs every second while the addon is active. Checks if Kodi is
        busy (scanning, or showing a "please wait" dialog) and tells the
        LED mixin to switch effects only when that state changes. On
        shutdown, stops the LED thread cleanly."""

        # Confirms in kodi.log that the service started.
        xbmc.log("Homatics LED: service starting", level=xbmc.LOGINFO)

        self._led_start()
        try:
            while not self.abortRequested():
                busy = self._is_busy()
                if busy and not self._was_busy:
                    self._led_on_busy_start()
                elif not busy and self._was_busy:
                    self._led_on_busy_stop()
                self._was_busy = busy

                if self.waitForAbort(self.BUSY_POLL_SEC):
                    break
        finally:
            self._led_shutdown()

        # Confirms in kodi.log that the service shut down cleanly.
        xbmc.log("Homatics LED: service stopped", level=xbmc.LOGINFO)


if __name__ == "__main__":
    LedStatusService().run()