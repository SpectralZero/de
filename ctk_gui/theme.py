# # ctk_gui/theme.py
# """
# theme.py
# ========
# • Inherit CTk's own JSON themes so you never miss a key.
# • Apply only our colour overrides.
# • Provide font constants and load_icon helper.
# """

# import customtkinter as ctk
# import json
# import tempfile
# import os
# from pathlib import Path

# # ── Fonts used by widgets ─────────────────────────────────────────────
# FONT_HEADLINE = ("Segoe UI Semibold", 16)
# FONT_BODY     = ("Segoe UI", 12)

# # ── Your palette overrides ────────────────────────────────────────────
# PRIMARY  = "#0066FF"
# BG_DARK  = "#1e1e1e"
# BG_LIGHT = "#f2f2f2"


# def apply_theme(dark: bool = True) -> None:
#     """
#     • Load CTk's built-in 'dark-blue' or 'blue' theme JSON.
#     • Override only the colours we care about.
#     • Save to a temp file and activate it.
#     """
#     # 1) pick base theme name
#     base_name = "dark-blue" if dark else "blue"

#     # 2) load CTk's packaged JSON
#     base_dict = _load_builtin_theme(base_name)

#     # 3) override root background
#     base_dict["CTk"]["fg_color"] = [BG_DARK] if dark else [BG_LIGHT]

#     # 4) override button palette
#     btn = base_dict["CTkButton"]
#     btn["fg_color"]     = [PRIMARY, PRIMARY]
#     btn["hover_color"]  = ["#0052cc", "#0052cc"]
#     btn["border_color"] = [PRIMARY, PRIMARY]

#     # 5) dump to temp JSON file
#     fd, path = tempfile.mkstemp(prefix="_sc_theme_", suffix=".json")
#     with os.fdopen(fd, "w", encoding="utf-8") as f:
#         json.dump(base_dict, f)

#     # 6) apply to CTk
#     ctk.set_appearance_mode("dark" if dark else "light")
#     ctk.set_default_color_theme(path)


# def _load_builtin_theme(name: str) -> dict:
#     """
#     Locate CustomTkinter's own '{name}.json' under its assets/themes folder
#     and return the parsed dict.
#     """
#     # customtkinter.__file__ → .../site-packages/customtkinter/__init__.py
#     pkg_dir = Path(ctk.__file__).parent
#     theme_dir = pkg_dir / "assets" / "themes"
#     theme_path = theme_dir / f"{name}.json"
#     if not theme_path.exists():
#         raise FileNotFoundError(f"Unable to find CTk theme at {theme_path}")
#     with open(theme_path, "r", encoding="utf-8") as f:
#         return json.load(f)


# def load_icon(name: str, size: int = 20):
#     """
#     Return a CTk-compatible PhotoImage from ctk_gui/assets/.
#     Supports .svg (via cairosvg) and .png/.jpg.
#     """
#     from PIL import Image, ImageTk
#     import io, cairosvg

#     assets_dir = Path(__file__).parent / "assets"
#     file = assets_dir / name
#     if not file.exists():
#         raise FileNotFoundError(f"Icon not found: {file}")

#     if file.suffix.lower() == ".svg":
#         png_bytes = cairosvg.svg2png(
#             url=str(file), output_width=size, output_height=size
#         )
#         return ImageTk.PhotoImage(Image.open(io.BytesIO(png_bytes)))

#     # PNG or JPG fallback
#     img = Image.open(file).resize((size, size))
#     return ImageTk.PhotoImage(img)

"""
theme.py
========
Inherit CTk's built-in theme JSON, override just colours.
Provides fonts + load_icon helper.
"""
import customtkinter as ctk, json, tempfile, os
from pathlib import Path

FONT_BODY = ("Segoe UI", 12)

# overrides
PRIMARY  = "#0066FF"
BG_DARK  = "#1e1e1e"
BG_LIGHT = "#f2f2f2"

def apply_theme(*, dark: bool) -> None:
    name = "dark-blue" if dark else "blue"
    data = _load_builtin_theme(name)

    data["CTk"]["fg_color"] = [BG_DARK] if dark else [BG_LIGHT]

    btn = data["CTkButton"]
    btn["fg_color"]     = [PRIMARY, PRIMARY]
    btn["hover_color"] = ["#0047B3", "#0047B3"]
    btn["border_color"] = [PRIMARY, PRIMARY]

    fd, path = tempfile.mkstemp(prefix="_sc_theme_", suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f)
    # ctk.set_appearance_mode("dark" if dark else "light")
    # ctk.set_default_color_theme(path)
    

def _load_builtin_theme(n:str)->dict:
    pkg = Path(ctk.__file__).parent/"assets"/"themes"
    fn = pkg/f"{n}.json"
    return json.loads(fn.read_text(encoding="utf-8"))

def load_icon(name:str)->ctk.CTkImage:
    from PIL import Image
    import cairosvg, io
    assets = Path(__file__).parent/"assets"
    f = assets/name
    if f.suffix==".svg":
        png = cairosvg.svg2png(url=str(f),output_width=20,output_height=20)
        return ctk.CTkImage(light_image=Image.open(io.BytesIO(png)),size=(20,20))
    img = Image.open(f).resize((20,20))
    return ctk.CTkImage(light_image=img,size=(20,20))
