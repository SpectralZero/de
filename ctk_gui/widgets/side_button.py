from __future__ import annotations
import customtkinter as ctk
from ctk_gui.theme import load_icon


class SideButton(ctk.CTkButton):
    """
    Small square icon button for sidebar / top‑bar (40 × 40 px).

    • Shows a tooltip on hover.
    • Uses CTkImage so icons scale on High‑DPI.
    """

    def __init__(self, master, svg: str, tip: str, command=None):
        super().__init__(
            master,
            image=load_icon(svg),
            text="",
            width=40,
            height=40,
            fg_color="transparent",
            hover=False,
            corner_radius=0,
            command=command,
        )
        self.configure(cursor="hand2")  # pointing hand
        self._create_tooltip(tip)

    # ---------------------------------------------------------------- tooltip
    def _create_tooltip(self, text: str):
        if not text:
            return

        tip = ctk.CTkLabel(
            master=self,                 # <-- master required
            text=text,
            fg_color="#333",
            text_color="#fff",
            font=("Segoe UI", 10),
            corner_radius=4,
            padx=4, pady=2,
        )
        tip.place_forget()               # hide initially

        def enter(_):
            x, y = self.winfo_pointerxy()
            tip.place(x=x + 14, y=y + 14, anchor="nw")

        def leave(_):
            tip.place_forget()

        self.bind("<Enter>", enter, add="+")
        self.bind("<Leave>", leave, add="+")