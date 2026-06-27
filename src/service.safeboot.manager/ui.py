import xbmcgui
import xbmcvfs





class BlockOverlay(xbmcgui.WindowDialog):
    def __init__(self):
        """Build the overlay window with bubble, icon, labels, and progress bar.

        All controls are created once and reused throughout the session.
        """
        w, h = 1920, 1080


        self._white = self._find_white_image()

        self.bg = xbmcgui.ControlImage(0, 0, w, h, self._white)
        self.bg.setColorDiffuse("0xDD000000")
        self.addControl(self.bg)

        bubble_w, bubble_h = 550, 180
        bubble_x = (w - bubble_w) // 2 -250
        bubble_y = (h - bubble_h) // 2

        shadow = xbmcgui.ControlImage(bubble_x + 6, bubble_y + 6, bubble_w, bubble_h, self._white)
        shadow.setColorDiffuse("0x88000000")
        self.addControl(shadow)

        self.bubble_bg = xbmcgui.ControlImage(bubble_x, bubble_y, bubble_w, bubble_h, self._white)
        self.bubble_bg.setColorDiffuse("0xFF1A1A2E")
        self.addControl(self.bubble_bg)

        # --- Addon icon ---
        icon_size = 130
        icon_x = bubble_x + 30
        icon_y = bubble_y + (bubble_h - icon_size) // 2 + 20  # slightly above the progress bar
        icon_path = xbmcvfs.translatePath('special://home/addons/service.safeboot.manager/icon.png')
        self.icon = xbmcgui.ControlImage(icon_x, icon_y, icon_size, icon_size, icon_path)
        self.addControl(self.icon)

        # --- Shift text right to make room for the icon ---
        text_offset = 100 
        accent = xbmcgui.ControlImage(bubble_x, bubble_y, bubble_w, 4, self._white)
        accent.setColorDiffuse("0xFF00AAFF")
        self.addControl(accent)

        self.label_text = xbmcgui.ControlLabel(
            bubble_x + text_offset, bubble_y + 30, bubble_w - text_offset, 50,
            "", font="font14", textColor="0xFFCCCCCC", alignment=6
        )
        self.addControl(self.label_text)

        self.label_percent = xbmcgui.ControlLabel(
            bubble_x + text_offset, bubble_y + 75, bubble_w - text_offset, 60,
            "", font="font20", textColor="0xFF00AAFF", alignment=6
        )
        self.addControl(self.label_percent)

        bar_w, bar_h = 320, 10  # slightly smaller bar to fit the offset layout
        bar_x = bubble_x + text_offset + (bubble_w - bar_w - text_offset) // 2
        bar_y = bubble_y + 155

        self.progress_bg = xbmcgui.ControlImage(bar_x, bar_y, bar_w, bar_h, self._white)
        self.progress_bg.setColorDiffuse("0xFF2A2A3E")
        self.addControl(self.progress_bg)

        self.progress_fill = xbmcgui.ControlImage(bar_x, bar_y, 1, bar_h, self._white)
        self.progress_fill.setColorDiffuse("0xFF00AAFF")
        self.addControl(self.progress_fill)

        self.bar_x = bar_x
        self.bar_y = bar_y
        self.bar_w = bar_w
        self.bar_h = bar_h

        self.blocker = xbmcgui.ControlButton(0, 0, w, h, "", focusTexture="", noFocusTexture="")
        self.addControl(self.blocker)

    def _find_white_image(self):
        """Return a path to a 1x1 white PNG image.

        Searches known skin locations first. If none found,
        generates a minimal PNG file in special://temp/.
        """
        candidates = [
            "special://home/addons/skin.estuary/media/white.png",
            "special://xbmc/addons/skin.estuary/media/white.png",
            "special://home/addons/skin.confluence/media/white.png",
        ]
        for path in candidates:
            real = xbmcvfs.translatePath(path)
            if xbmcvfs.exists(real):
                return path
        tmp = xbmcvfs.translatePath("special://temp/white_1x1.png")
        if not xbmcvfs.exists(tmp):
            png_bytes = bytes([
                0x89,0x50,0x4E,0x47,0x0D,0x0A,0x1A,0x0A,
                0x00,0x00,0x00,0x0D,0x49,0x48,0x44,0x52,
                0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x01,
                0x08,0x02,0x00,0x00,0x00,0x90,0x77,0x53,
                0xDE,0x00,0x00,0x00,0x0C,0x49,0x44,0x41,
                0x54,0x08,0xD7,0x63,0xF8,0xFF,0xFF,0x3F,
                0x00,0x05,0xFE,0x02,0xFE,0xDC,0xCC,0x59,
                0xE7,0x00,0x00,0x00,0x00,0x49,0x45,0x4E,
                0x44,0xAE,0x42,0x60,0x82
            ])
            f = xbmcvfs.File(tmp, 'wb')
            f.write(bytearray(png_bytes))
            f.close()
        return tmp

    def onAction(self, action):
        """Intercept remote/keyboard actions while the overlay is visible.

        Swallows all back-key presses to prevent accidental navigation.
        """
        BACK_ACTIONS = (
            10,   # ACTION_PREVIOUS_MENU
            92,   # ACTION_BACK
            110,  # ACTION_NAV_BACK
        )
        if action.getId() in BACK_ACTIONS:
            self.setFocus(self.blocker)  # return focus to the blocker button
            return                       # swallow the action — do nothing

    def show(self):
        """Show the overlay and lock focus on the blocker button."""
        self.is_open = True
        super().show()
        self.setFocus(self.blocker)

    def close(self):
        """Close the overlay and mark it as inactive."""
        self.is_open = False
        super().close()

    def set_progress(self, percent, text=""):
        """Update the progress bar and status labels.

        Args:
            percent (int): Progress value between 0 and 100.
            text    (str): Status message displayed above the percentage.
        """
        percent = max(0, min(100, int(percent)))
        self.label_text.setLabel(text)
        self.label_percent.setLabel(f"{percent}%")

        fill_width = max(1, int(self.bar_w * percent / 100))
        self.removeControl(self.progress_fill)
        self.progress_fill = xbmcgui.ControlImage(
            self.bar_x, self.bar_y, fill_width, self.bar_h, self._white
        )
        self.progress_fill.setColorDiffuse("0xFF00AAFF")
        self.addControl(self.progress_fill)