import xbmc
import xbmcvfs
import os
import xbmcaddon
import time
import xbmcgui
import threading

from ui import BlockOverlay


# ────────────────────────────────────────────────
#  BackKeyWatcher — detects double back-key press
#  only during active playback (video / IPTV / radio)
# ────────────────────────────────────────────────
class BackKeyWatcher(threading.Thread):
    """
    Runs in a separate thread.
    Polls every 30ms to check if the player is active and calls
    _on_double_back() if the user pressed Back twice quickly.

    Kodi does not expose raw key-events to services directly,
    so we use xbmc.getCondVisibility as a workaround:
    when the user presses Back during playback, Kodi briefly drops
    Window.IsActive(fullscreenvideo) to False, then returns to True.
    We detect that momentary drop.
    """

    DOUBLE_BACK_WINDOW_MS = 2000  # time window between two back presses (milliseconds)
    POLL_MS               = 30    # polling interval (milliseconds)

    def __init__(self, monitor):
        super().__init__(daemon=True)
        self.monitor         = monitor
        self._stop_event     = threading.Event()
        self._last_back_ts   = 0.0
        self._was_fullscreen = False

    def stop(self):
        """Signal the stop event to gracefully shut down the thread."""
        self._stop_event.set()

    def _is_playing_media(self):
        """Return True if any media is currently playing
        (Video, Audio, PVR TV, or PVR Radio)."""
        return (
            xbmc.getCondVisibility("Pvr.IsPlayingTv")    or
            xbmc.getCondVisibility("Pvr.IsPlayingRadio") or
            xbmc.getCondVisibility("Player.HasVideo")    or
            xbmc.getCondVisibility("Player.HasAudio")
        )

    def _is_fullscreen(self):
        """Return True if Kodi is currently rendering a fullscreen
        playback window (video, radio, or visualisation)."""
        return (
            xbmc.getCondVisibility("Window.IsActive(fullscreenvideo)") or
            xbmc.getCondVisibility("Window.IsActive(fullscreenradio)") or
            xbmc.getCondVisibility("Window.IsActive(visualisation)")
        )

    def _on_double_back(self):
        """Stop playback immediately when a double back-press is detected."""
        xbmc.log("SafeBoot: Double-Back detected → stopping player", level=xbmc.LOGINFO)
        xbmc.Player().stop()

    def run(self):
        """Main polling loop (every 30ms).

        Monitors fullscreen → windowed transitions during playback.
        If the user exits fullscreen twice within DOUBLE_BACK_WINDOW_MS,
        triggers _on_double_back() to stop the player.
        """
        xbmc.log("SafeBoot: BackKeyWatcher started", level=xbmc.LOGINFO)
        try:
            while not self._stop_event.is_set():
                self._stop_event.wait(timeout=self.POLL_MS / 1000.0)
                if self._stop_event.is_set():
                    break

                playing = self._is_playing_media()

                if not playing:
                    self._was_fullscreen = False
                    self._last_back_ts   = 0.0
                    continue

                now_fullscreen = self._is_fullscreen()

                if self._was_fullscreen and not now_fullscreen:
                    now      = time.time()
                    delta_ms = (now - self._last_back_ts) * 1000
                    xbmc.log("SafeBoot: Back pressed, delta=%.0fms" % delta_ms, level=xbmc.LOGINFO)

                    if 0 < delta_ms <= self.DOUBLE_BACK_WINDOW_MS:
                        self._on_double_back()
                        self._last_back_ts = 0.0
                    else:
                        self._last_back_ts = now

                self._was_fullscreen = now_fullscreen

        except Exception as e:
            xbmc.log("SafeBoot: BackKeyWatcher ERROR: %s" % str(e), level=xbmc.LOGERROR)

        xbmc.log("SafeBoot: BackKeyWatcher stopped", level=xbmc.LOGINFO)


# ────────────────────────────────────────────────
#  SafeBootManager
# ────────────────────────────────────────────────
class SafeBootManager(xbmc.Monitor):

    def __init__(self):
        """Initialize the service.

        Loads all settings from settings.xml, creates the GUI overlay,
        and starts the BackKeyWatcher thread if enabled by the user.
        """
        super().__init__()
        self.addon            = xbmcaddon.Addon(id='service.safeboot.manager')
        self.overlay          = BlockOverlay()
        self._play_start_time = None
        self._play_type       = None

        # Load settings — matches settings.xml
        self._enabled             = self.addon.getSettingBool('enabled')
        self._show_player_overlay = self.addon.getSettingBool('show_player_overlay')
        self._double_back_stop    = self.addon.getSettingBool('double_back_stop')
        self._show_busy_overlay   = self.addon.getSettingBool('show_busy_overlay')

        # Provider check settings
        self._check_trakt         = self.addon.getSettingBool('check_trakt')
        self._check_torbox        = self.addon.getSettingBool('check_torbox')
        self._check_alldebrid     = self.addon.getSettingBool('check_alldebrid')
        self._check_realdebrid    = self.addon.getSettingBool('check_realdebrid')
        self._check_premiumize    = self.addon.getSettingBool('check_premiumize')
        self._check_easynews      = self.addon.getSettingBool('check_easynews')

        # Constants — always active while the addon is running
        self._show_iptv_loading   = True
        self._clear_temp_on_start = True

        # Start the BackKeyWatcher thread
        self._back_watcher = BackKeyWatcher(self)
        if self._double_back_stop:
            self._back_watcher.start()


    # ── Real-time settings update ─────────────────
    def onSettingsChanged(self):
        """Called automatically when the user changes a setting.

        Refreshes overlay flags in real-time and manages the
        BackKeyWatcher thread lifecycle without restarting the service.
        """
        self._show_player_overlay = self.addon.getSettingBool('show_player_overlay')
        self._show_busy_overlay   = self.addon.getSettingBool('show_busy_overlay')
        self._check_trakt         = self.addon.getSettingBool('check_trakt')
        self._check_torbox        = self.addon.getSettingBool('check_torbox')
        self._check_alldebrid     = self.addon.getSettingBool('check_alldebrid')
        self._check_realdebrid    = self.addon.getSettingBool('check_realdebrid')
        self._check_premiumize    = self.addon.getSettingBool('check_premiumize')
        self._check_easynews      = self.addon.getSettingBool('check_easynews')

        new_double = self.addon.getSettingBool('double_back_stop')
        if new_double != self._double_back_stop:
            self._double_back_stop = new_double
            if new_double:
                if self._back_watcher and self._back_watcher.is_alive():
                    self._back_watcher.stop()
                self._back_watcher = BackKeyWatcher(self)
                self._back_watcher.start()
                xbmc.log("SafeBoot: Double-Back ENABLED", level=xbmc.LOGINFO)
            else:
                if self._back_watcher:
                    self._back_watcher.stop()
                xbmc.log("SafeBoot: Double-Back DISABLED", level=xbmc.LOGINFO)


    def onNotification(self, sender, method, data):
        """Handle Kodi player notifications.

        - Player.OnPlay   : show loading overlay while media starts.
        - Player.OnAVStart: record playback start time, close overlay.
        - Player.OnStop   : show brief overlay after playback ends.
        """
        if method == "Player.OnPlay":
            keyboard_active = xbmc.getCondVisibility("Window.IsActive(keyboard)")
            if self._show_player_overlay and not self.overlay.is_open and not keyboard_active:
                self.overlay.show()
                for i in range(0, 101, 10):
                    if self.abortRequested():
                        break
                    # Stop loading immediately if keyboard opens mid-animation
                    if xbmc.getCondVisibility("Window.IsActive(keyboard)"):
                        xbmc.log("SafeBoot: Keyboard detected — aborting player overlay", level=xbmc.LOGINFO)
                        break
                    self.overlay.set_progress(i, self.addon.getLocalizedString(30021))
                    xbmc.sleep(500)

        elif method == "Player.OnAVStart":
            self._play_start_time = time.time()
            if xbmc.getCondVisibility("Pvr.IsPlayingTv"):
                self._play_type = "tv"
            elif xbmc.getCondVisibility("Pvr.IsPlayingRadio"):
                self._play_type = "radio"
            else:
                self._play_type = "video"
            if self.overlay.is_open:
                self.overlay.close()

        elif method == "Player.OnStop":
            if not xbmc.Player().isPlaying():
                now           = time.time()
                start_time    = self._play_start_time or (now - 0.5)
                play_duration = now - start_time

                if self._show_player_overlay:
                    self.overlay.show()
                    wait_ms    = int((15 - play_duration) * 1000) if play_duration < 15 else 3000
                    step_sleep = max(1, wait_ms // 10)
                    for i in range(0, 101, 10):
                        if self.abortRequested():
                            break
                        self.overlay.set_progress(i, self.addon.getLocalizedString(30020))
                        xbmc.sleep(step_sleep)
                    self.overlay.close()

                self._play_start_time = None


    # ── Temporary file cleanup ────────────────────
    def clear_temp_cache(self):
        """Delete temporary files from special://temp/.

        Skips .log files and white_1x1.png to preserve
        runtime assets needed by the service.
        """
        xbmc.log("SafeBoot: Starting cache clear", level=xbmc.LOGINFO)
        temp_path = xbmcvfs.translatePath('special://temp/')
        if os.path.exists(temp_path):
            for filename in os.listdir(temp_path):
                if filename.endswith('.log'):
                    continue
                if filename == 'white_1x1.png':
                    continue
                file_path = os.path.join(temp_path, filename)
                if os.path.isfile(file_path):
                    try:
                        os.unlink(file_path)
                        xbmc.log("SafeBoot: Cleared temp file: %s" % filename, level=xbmc.LOGINFO)
                    except Exception:
                        pass
        xbmc.log("SafeBoot: Cache clear done", level=xbmc.LOGINFO)


    def check_service(self, setting_name, title, message):
        """Check if a third-party token (Trakt / TorBox) is set.

        If the token is missing, prompts the user with a yes/no dialog.
        On confirmation, opens the POV addon's service management screen.
        """
        try:
            pov_addon = xbmcaddon.Addon('plugin.video.pov')
            token = pov_addon.getSetting(setting_name)
            xbmc.log("SafeBoot: %s = '%s'" % (setting_name, token), level=xbmc.LOGINFO)
            if not token:
                xbmc.log("SafeBoot: %s not connected" % title, level=xbmc.LOGINFO)
                if xbmcgui.Dialog().yesno(title, message):
                    xbmc.executebuiltin('RunPlugin(plugin://plugin.video.pov/?mode=myservices)')
        except Exception as e:
            xbmc.log("SafeBoot: %s error = %s" % (title, str(e)), level=xbmc.LOGINFO)


    def is_system_idle(self):
        """Return True if Kodi is idle.

        Requires: no video library scan, no PVR scan,
        and at least 5 seconds of inactivity on the remote.
        """
        scanning  = xbmc.getCondVisibility("Library.IsScanningVideo")
        pvr_scan  = xbmc.getCondVisibility("Pvr.IsScanning")
        idle_time = xbmc.getGlobalIdleTime()
        return (not scanning) and (not pvr_scan) and idle_time > 5


    def wait_for_stable_system(self, timeout=60):
        """Block until the system is stable, up to timeout seconds.

        Requires 5 consecutive idle checks to pass before returning True.
        Any busy state resets the counter. Updates the progress overlay
        while waiting, and respects abortRequested() for clean shutdown.
        """
        stable      = 0
        pseudo_prog = 55.0
        for _ in range(timeout * 2):
            if self.abortRequested():
                return False
            if self.is_system_idle():
                stable += 1
            else:
                stable      = 0
                pseudo_prog = 55.0
            if stable >= 5:
                return True
            if pseudo_prog < 68:
                pseudo_prog += 0.2
            self.overlay.set_progress(int(pseudo_prog), self.addon.getLocalizedString(30009))
            xbmc.sleep(500)
        return False


    # ── Service entry point ───────────────────────
    def run_service(self):
        """Main service entry point. Consists of two phases:

        Boot Sequence:
            Shows the overlay, clears temp cache, waits for Kodi startup
            to complete, checks IPTV loading, and validates Trakt/TorBox tokens.

        Guardian Loop:
            Runs indefinitely in the background. Detects busy states
            (library scan, PVR scan, busy dialog) and shows the blocking
            overlay to prevent accidental keypresses during heavy load.
        """

        # ── First run — enable all providers and open settings ──
        if self.addon.getSettingBool('first_run'):
            xbmc.log("SafeBoot: First run detected — enabling all providers", level=xbmc.LOGINFO)
            self.addon.setSettingBool('check_trakt',      True)
            self.addon.setSettingBool('check_torbox',     True)
            self.addon.setSettingBool('check_alldebrid',  True)
            self.addon.setSettingBool('check_realdebrid', True)
            self.addon.setSettingBool('check_premiumize', True)
            self.addon.setSettingBool('check_easynews',   True)
            self.addon.setSettingBool('first_run',        False)
            # Reload into memory
            self._check_trakt      = True
            self._check_torbox     = True
            self._check_alldebrid  = True
            self._check_realdebrid = True
            self._check_premiumize = True
            self._check_easynews   = True
            # Open settings so user can choose
            xbmc.sleep(2000)
            xbmc.executebuiltin('Addon.OpenSettings(service.safeboot.manager)')

        # ── Boot sequence — only if enabled ──────────────
        if self._enabled:
            self.overlay.show()

            # Step 1-10%: clear temp cache
            for i in range(1, 11):
                if self.abortRequested():
                    break
                self.overlay.set_progress(i, self.addon.getLocalizedString(30001))
                xbmc.sleep(100)
            if self._clear_temp_on_start:
                # Wait until keyboard is closed before clearing temp files
                while xbmc.getCondVisibility("Window.IsActive(keyboard)"):
                    xbmc.sleep(200)
                self.clear_temp_cache()
            xbmc.sleep(500)

            # Step 11-20%: wait for Kodi startup window to close
            for i in range(11, 21):
                if self.abortRequested():
                    break
                self.overlay.set_progress(i, self.addon.getLocalizedString(30002))
                xbmc.sleep(200)
            while xbmc.getCondVisibility("Window.IsActive(startup)"):
                if self.abortRequested():
                    break
                xbmc.sleep(200)

            self.overlay.set_progress(25, self.addon.getLocalizedString(30003))
            xbmc.sleep(800)

            # Step 26-50%: wait for system resources to load
            for i in range(26, 51):
                if self.abortRequested():
                    break
                self.overlay.set_progress(i, self.addon.getLocalizedString(30007))
                xbmc.sleep(150)
            xbmc.sleep(1000)

            self.wait_for_stable_system()

            # Step 55-69%: IPTV Simple loading (if installed)
            has_iptv = xbmc.getCondVisibility("System.HasAddon(pvr.iptvsimple)")
            if has_iptv and self._show_iptv_loading:
                for i in range(55, 68):
                    if self.abortRequested():
                        break
                    self.overlay.set_progress(i, self.addon.getLocalizedString(30005))
                    xbmc.sleep(200)
                for i in range(68, 70):
                    if self.abortRequested():
                        break
                    self.overlay.set_progress(i, self.addon.getLocalizedString(30004))
                    xbmc.sleep(150)
            elif not has_iptv:
                self.overlay.set_progress(55, self.addon.getLocalizedString(30008))
                xbmc.sleep(2000)

            # Step 70-100%: check provider tokens
            for i in range(70, 78):
                if self.abortRequested():
                    break
                self.overlay.set_progress(i, self.addon.getLocalizedString(30014))
                xbmc.sleep(100)

            if self._check_trakt:
                self.overlay.set_progress(78, self.addon.getLocalizedString(30010))
                xbmc.sleep(1500)
                try:
                    pov_addon = xbmcaddon.Addon('plugin.video.pov')
                    if pov_addon.getSetting('trakt.token'):
                        self.overlay.set_progress(82, self.addon.getLocalizedString(30016))
                    else:
                        self.overlay.set_progress(82, self.addon.getLocalizedString(30011))
                except Exception:
                    pass
                xbmc.sleep(1500)
            else:
                xbmc.log("SafeBoot: Trakt check disabled by user", level=xbmc.LOGINFO)

            if self._check_torbox:
                self.overlay.set_progress(83, self.addon.getLocalizedString(30012))
                xbmc.sleep(1500)
                try:
                    pov_addon = xbmcaddon.Addon('plugin.video.pov')
                    if pov_addon.getSetting('tb.token'):
                        self.overlay.set_progress(87, self.addon.getLocalizedString(30017))
                    else:
                        self.overlay.set_progress(87, self.addon.getLocalizedString(30013))
                except Exception:
                    pass
                xbmc.sleep(1500)
            else:
                xbmc.log("SafeBoot: TorBox check disabled by user", level=xbmc.LOGINFO)

            # ── ספקים נוספים — סטטוס בלבד, ללא דיאלוג ──
            try:
                pov_addon = xbmcaddon.Addon('plugin.video.pov')
                if self._check_alldebrid:
                    self.overlay.set_progress(89, self.addon.getLocalizedString(30024))
                    xbmc.sleep(800)
                    msg = self.addon.getLocalizedString(30026) if pov_addon.getSetting('ad.token') else self.addon.getLocalizedString(30025)
                    self.overlay.set_progress(90, msg)
                    xbmc.sleep(800)

                if self._check_realdebrid:
                    self.overlay.set_progress(91, self.addon.getLocalizedString(30028))
                    xbmc.sleep(800)
                    msg = self.addon.getLocalizedString(30030) if pov_addon.getSetting('rd.token') else self.addon.getLocalizedString(30029)
                    self.overlay.set_progress(93, msg)
                    xbmc.sleep(800)

                if self._check_premiumize:
                    self.overlay.set_progress(94, self.addon.getLocalizedString(30032))
                    xbmc.sleep(800)
                    msg = self.addon.getLocalizedString(30034) if pov_addon.getSetting('pm.token') else self.addon.getLocalizedString(30033)
                    self.overlay.set_progress(96, msg)
                    xbmc.sleep(800)

                if self._check_easynews:
                    self.overlay.set_progress(97, self.addon.getLocalizedString(30036))
                    xbmc.sleep(800)
                    msg = self.addon.getLocalizedString(30038) if pov_addon.getSetting('easynews_user') else self.addon.getLocalizedString(30037)
                    self.overlay.set_progress(99, msg)
                    xbmc.sleep(800)
            except Exception:
                pass

            self.overlay.set_progress(100, self.addon.getLocalizedString(30018))
            xbmc.sleep(3000)
            self.overlay.close()

            # דיאלוג התחברות — רק Trakt ו-TorBox
            if self._check_trakt:
                self.check_service('trakt.token', 'Trakt',
                                   self.addon.getLocalizedString(30022))
            if self._check_torbox:
                self.check_service('tb.token', 'TorBox',
                                   self.addon.getLocalizedString(30023))

        else:
            xbmc.log("SafeBoot: startup disabled — skipping boot sequence", level=xbmc.LOGINFO)

        # ── Guardian — always runs unless show_busy_overlay is off ──
        if not self._show_busy_overlay:
            xbmc.log("SafeBoot: Guardian disabled — service idle", level=xbmc.LOGINFO)
            while not self.abortRequested():
                xbmc.sleep(500)
        else:
            counter = 0
            while not self.abortRequested():
                keyboard_active = xbmc.getCondVisibility("Window.IsActive(keyboard)")
                is_busy = (
                    not keyboard_active and (
                        xbmc.getCondVisibility("Window.IsActive(busydialog)") or
                        xbmc.getCondVisibility("Library.IsScanningVideo")     or
                        xbmc.getCondVisibility("Pvr.IsScanning")
                    )
                )
                if is_busy:
                    if not self.overlay.is_open:
                        self.overlay.show()
                    counter = (counter + 2) if counter < 100 else 0
                    self.overlay.set_progress(counter, self.addon.getLocalizedString(30019))
                    if self.overlay.getFocusId() != self.overlay.blocker.getId():
                        self.overlay.setFocus(self.overlay.blocker)
                else:
                    if self.overlay.is_open:
                        self.overlay.close()
                xbmc.sleep(200)

        # Cleanup on shutdown
        self._back_watcher.stop()


if __name__ == "__main__":
    SafeBootManager().run_service()