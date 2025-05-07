# test_bg.py  – run this next to your project
import customtkinter as ctk
from .ui_theme import style_utils

style_utils.APP_THEME = "dark"      # force dark so BG_DARK is chosen
style_utils.apply_theme_background()

root = ctk.CTk()
root.geometry("400x250")

card = ctk.CTkFrame(root,
                    width=380, height=230,
                    corner_radius=12,
                    fg_color="transparent")
card.pack(padx=10, pady=10)
style_utils.set_card_background(card)

ctk.CTkLabel(card, text="Hello on background!").place(relx=.5, rely=.5, anchor="center")

root.after(2000, style_utils.toggle_theme)  # auto‑toggle after 2 s
root.mainloop()
