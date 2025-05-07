"""
ui_theme.style_utils
====================
Single place that controls dark / light and card backgrounds.
"""

from __future__ import annotations
from pathlib import Path
import customtkinter as ctk
from PIL import Image
import cairosvg, io

# ---- constants ------------------------------------------------------------
from ..ui_theme.constants import BG_DARK, BG_WHITE     # keep your own path constants

APP_THEME      = "dark"
BG_IMAGE_PATH  = BG_DARK

# registry of every CTkFrame we skin ----------------------------------------
_CARDS: list[ctk.CTkFrame] = []
_BG_CACHE: dict[str, ctk.CTkImage] = {}

# ---------------------------------------------------------------- utilities
def apply_theme_background() -> None:
    """(Re)build JSON theme via ctk_gui.theme and set CTk appearance mode."""
    from ctk_gui.theme import apply_theme          # local import → no circular loop
    dark = (APP_THEME == "dark")
    apply_theme(dark=dark)
    ctk.set_appearance_mode("dark" if dark else "light")

def get_theme_colors() -> dict[str,str]:
    return {
        "fg":    "#212121" if APP_THEME == "dark" else "#f5f5f5",
        "hover": "#2a2d2e" if APP_THEME == "dark" else "#e0e0e0",
        "text":  "white"   if APP_THEME == "dark" else "black",
    }

def get_bg_image_path() -> str:
    return str(BG_IMAGE_PATH)

# ---------------------------------------------------------------- card skin
def set_card_background(card: ctk.CTkFrame) -> None:
    """
    Paint *card* with the current BG_IMAGE_PATH.
    The image is resized to the card’s exact size and updated on every resize.
    """
    if card not in _CARDS:
        _CARDS.append(card)

    img_path = Path(BG_IMAGE_PATH)
    if not img_path.is_file():
        print("[BG] missing file:", img_path)
        return

    # Load once (keep original resolution for quality)
    if img_path.suffix.lower() == ".svg":
        import cairosvg, io
        pil_original = Image.open(io.BytesIO(cairosvg.svg2png(url=str(img_path))))
    else:
        pil_original = Image.open(img_path)

    # ---------- helper that (re)creates the CTkImage at the right size -----
    def _apply_bg(event=None):
        w, h = card.winfo_width(), card.winfo_height()
        if w <= 2 or h <= 2:
            card.after(20, _apply_bg); return

        pil = pil_original.resize((w, h), Image.LANCZOS)

        # -------- FIX: don't pass size= --------
        ctk_img = ctk.CTkImage(light_image=pil, dark_image=pil)
        # ---------------------------------------

        if not hasattr(card, "_bg_label"):
            lbl = card._bg_label = ctk.CTkLabel(card, text="", image=ctk_img)
            lbl.place(relx=0, rely=0, relwidth=1, relheight=1)
            lbl.lower()
        else:
            card._bg_label.configure(image=ctk_img)
        card._bg_label.image = ctk_img

    _apply_bg()                 # draw once now
    card.bind("<Configure>", _apply_bg)   # redraw on resize

# ---------------------------------------------------------------- toggle
def toggle_theme() -> None:
    """Flip dark / light, rebuild JSON theme, repaint every registered card."""
    global APP_THEME, BG_IMAGE_PATH

    if APP_THEME == "dark":
        APP_THEME, BG_IMAGE_PATH = "light", BG_WHITE
    else:
        APP_THEME, BG_IMAGE_PATH = "dark", BG_DARK

    apply_theme_background()

    # repaint all known cards
    for card in _CARDS:
        set_card_background(card)