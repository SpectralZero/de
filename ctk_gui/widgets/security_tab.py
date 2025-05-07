"""
SecurityTab
===========

Feature toggles for TLS‑only mode, USB 2FA and Tor allowance.
Now presented in a centred card layout.
"""

import customtkinter as ctk
from core import api
from ctk_gui.ui_theme import style_utils

class SecurityTab(ctk.CTkFrame):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)

        # ------------ responsive wrapper card ------------------------------
        card = ctk.CTkFrame(self, corner_radius=12, fg_color="#ffffff")
        card.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")
        self.grid_rowconfigure(0, weight=1); self.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(self, corner_radius=12, fg_color="#ffffff")
        card.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")

        style_utils.set_card_background(card)

        # ------------ title -----------------------------------------------
        ctk.CTkLabel(card, text="Security Settings",
                     font=("Segoe UI Semibold", 18)
                     ).pack(anchor="w", pady=(0,12))

        # ------------ switches --------------------------------------------
        self.tls_sw = ctk.CTkSwitch(card, text="Enforce TLS 1.3",
                                    command=self._toggle_tls)
        self.usb_sw = ctk.CTkSwitch(card, text="Require USB Key",
                                    command=self._toggle_usb)
        self.tor_sw = ctk.CTkSwitch(card, text="Allow Tor mode",
                                    command=self._toggle_tor)

        for sw in (self.tls_sw, self.usb_sw, self.tor_sw):
            sw.pack(anchor="w", pady=4)

        self._sync_from_backend()

    # ---------------------------------------------------------------- API bridges
    def _toggle_tls(self): api.set_tls_enforced(self.tls_sw.get())
    def _toggle_usb(self): api.set_usb_required(self.usb_sw.get())
    def _toggle_tor(self): api.set_tor_allowed(self.tor_sw.get())

    def _sync_from_backend(self):
        (self.tls_sw.select() if api.is_tls_enforced() else self.tls_sw.deselect())
        (self.usb_sw.select() if api.is_usb_required() else self.usb_sw.deselect())
        (self.tor_sw.select() if api.is_tor_allowed()  else self.tor_sw.deselect())
