"""
ctk_gui.launcher
================
Responsive CTk‑based launcher (sidebar + topbar + stacked pages).
"""

from __future__ import annotations
import sys, pathlib, platform, ctypes
import customtkinter as ctk

# ---------------------------------------------------------------- project imports
from ctk_gui.common            import PY312, CHAT_DIR, ROOT
from ctk_gui.theme             import apply_theme, load_icon, FONT_BODY
from ctk_gui.widgets.side_button import SideButton
from ctk_gui.widgets.server_tab  import ServerTab
from ctk_gui.widgets.client_tab  import ClientTab
from ctk_gui.widgets.log_tab     import LogTab
from ctk_gui.widgets.db_tab      import DbTab
from ctk_gui.widgets.security_tab import SecurityTab
from ctk_gui.ui_theme import style_utils

# ---------------------------------------------------------------- Hi‑DPI support
if platform.system() == "Windows" and int(platform.release()) >= 10:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)   # per‑monitor DPI
elif sys.platform == "darwin":
    ctk.scaling = 2.0

# ---------------------------------------------------------------- icon mapping
ICON_FOR = {
    "Server":   "server.svg",
    "Clients":  "users.svg",
    "Logs":     "log.svg",
    "Database": "db.svg",
    "Security": "security.svg",
}

# ==================================================================== AppWindow
class AppWindow(ctk.CTk):
    WIDTH_EXP, WIDTH_COLL = 200, 60

    def __init__(self):
        super().__init__()
        self.title("SecureChatApp – Modern CTk UI")
        self.geometry("1280x770")
        self.minsize(900, 560)

        apply_theme(dark=True)

        # ---------- master grid:  sidebar  |  stack  ------------------------
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ── Sidebar ---------------------------------------------------------
        self.sidebar = ctk.CTkFrame(self, width=self.WIDTH_COLL, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)              # keep width fixed
        self.sidebar.grid_rowconfigure(99, weight=1)    # push icons to top

        btn_toggle = SideButton(
            self.sidebar, "menu.svg", "Toggle sidebar", self._toggle_sidebar
        )
        btn_toggle.grid(row=0, column=0, pady=(6,2))

        # ── Stacked pages container ----------------------------------------
        self.stack = ctk.CTkFrame(self, fg_color="transparent")
        self.stack.grid(row=0, column=1, sticky="nsew")
        self.stack.grid_rowconfigure(0, weight=1)
        self.stack.grid_columnconfigure(0, weight=1)

        self.pages = {
            "Server":   ServerTab(self.stack),
            "Clients":  ClientTab(self.stack),
            "Logs":     LogTab(self.stack),
            "Database": DbTab(self.stack, db_path=ROOT / "utils" / "users.db"),
            "Security": SecurityTab(self.stack),
        }

        for idx, (name, page) in enumerate(self.pages.items(), start=1):
            SideButton(
                self.sidebar,
                ICON_FOR[name],
                name,
                lambda n=name: self._show(n)
            ).grid(row=idx, column=0, pady=2)
            page.grid(row=0, column=0, sticky="nsew")

        self._show("Server")

        # ── Top bar ---------------------------------------------------------
        bar = ctk.CTkFrame(self, height=36, fg_color="transparent")
        bar.place(relx=0, rely=0, relwidth=1)

        ctk.CTkLabel(bar, text=" SecureChatApp", font=FONT_BODY
                     ).pack(side="left", padx=8)
        SideButton(bar, "bell.svg",  "Notifications"
                   ).pack(side="right", padx=(0,6))
        SideButton(bar, "moon.svg",  "Toggle theme", style_utils.toggle_theme
           ).pack(side="right", padx=4)

    # ---------------------------------------------------------------- stack
    def _show(self, name:str):
        for n,p in self.pages.items():
            p.grid_remove()
        self.pages[name].grid()

    # ---------------------------------------------------------------- sidebar
    def _toggle_sidebar(self):
        cur = self.sidebar.winfo_width()
        new = self.WIDTH_EXP if cur == self.WIDTH_COLL else self.WIDTH_COLL
        self.sidebar.configure(width=new)

    # ---------------------------------------------------------------- theming
    def _toggle_theme(self):
        apply_theme(ctk.get_appearance_mode() == "Light")

# ==================================================================== entry
def main():
    ctk.set_default_color_theme("blue")   # placeholder until apply_theme() kicks in
    AppWindow().mainloop()

if __name__ == "__main__":
    main()
