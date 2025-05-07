"""
DbTab  – view / add / delete users (now in a responsive card).
"""

from __future__ import annotations
import sqlite3, pathlib, hashlib
import customtkinter as ctk
from tkinter import ttk, messagebox
from ctk_gui.ui_theme import style_utils

class DbTab(ctk.CTkFrame):
    def __init__(self, master, *, db_path: pathlib.Path, **kw):
        super().__init__(master, **kw)

        # ---------- wrapper card -------------------------------------------
        card = ctk.CTkFrame(self, corner_radius=12, fg_color="#ffffff")
        card.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(self, corner_radius=12, fg_color="#ffffff")
        card.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")

        style_utils.set_card_background(card)   # <── add this line

        # ---------- DB ------------------------------------------------------
        self._conn = sqlite3.connect(db_path)
        self._hash_col = self._ensure_table()

        # ---------- title ---------------------------------------------------
        ctk.CTkLabel(card, text="User Database",
                     font=("Segoe UI Semibold", 18)
                     ).grid(row=0,column=0,sticky="w",pady=(0,8))

        # ---------- table ---------------------------------------------------
        cols=("username","pwd")
        tree = self.tree = ttk.Treeview(card, columns=cols, show="headings")
        tree.heading("username",text="Username")
        tree.heading("pwd",text="Password (hash)")
        tree.column("username", width=160, anchor="w")
        tree.column("pwd", anchor="w")

        ysb = ttk.Scrollbar(card, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=ysb.set)
        tree.grid(row=1,column=0,sticky="nsew")
        ysb .grid(row=1,column=1,sticky="ns")

        # ---------- form / buttons -----------------------------------------
        bar = ctk.CTkFrame(card, fg_color="transparent")
        bar.grid(row=2,column=0,sticky="w",pady=8)

        self.ent_user=ctk.CTkEntry(bar,placeholder_text="username",width=140)
        self.ent_pass=ctk.CTkEntry(bar,placeholder_text="password",show="*",width=140)
        ctk.CTkButton(bar,text="Add",width=90,command=self._add).pack(side="left",padx=4)
        ctk.CTkButton(bar,text="Delete selected",width=120,command=self._del_sel
                      ).pack(side="left",padx=4)
        self.ent_user.pack(side="left",padx=4)
        self.ent_pass.pack(side="left",padx=4)

        self._refresh()

    # ---------- schema check ----------------------------------------------
    def _ensure_table(self)->str:
        cur=self._conn.execute("PRAGMA table_info(users)")
        cols={c[1] for c in cur.fetchall()}
        if not cols:
            self._conn.execute("CREATE TABLE users(username TEXT PRIMARY KEY,pwdhash TEXT)")
            return "pwdhash"
        for cand in ("pwdhash","password_hash","password","hash"):
            if cand in cols:return cand
        self._conn.execute("ALTER TABLE users ADD COLUMN pwdhash TEXT")
        return "pwdhash"

    # ---------- CRUD -------------------------------------------------------
    def _add(self):
        u,p=self.ent_user.get().strip(), self.ent_pass.get()
        if not u or not p:
            messagebox.showwarning("Missing","Enter username & password");return
        h=hashlib.sha256(p.encode()).hexdigest()
        try:
            with self._conn: self._conn.execute(
                f"INSERT INTO users (username,{self._hash_col}) VALUES(?,?)",(u,h))
        except sqlite3.IntegrityError:
            messagebox.showerror("Exists",f"User '{u}' already exists");return
        self.ent_user.delete(0,"end"); self.ent_pass.delete(0,"end")
        self._refresh()

    def _del_sel(self):
        if not self.tree.selection(): return
        if not messagebox.askyesno("Delete","Remove selected user(s)?"): return
        for iid in self.tree.selection():
            u=self.tree.item(iid,"values")[0]
            with self._conn: self._conn.execute("DELETE FROM users WHERE username=?", (u,))
        self._refresh()

    # ---------- refresh ----------------------------------------------------
    def _refresh(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        cur=self._conn.execute(
            f"SELECT username,{self._hash_col} FROM users ORDER BY username")
        for u,h in cur.fetchall():
            h = h.hex() if isinstance(h,(bytes,bytearray)) else str(h or "")
            self.tree.insert("", "end", values=(u, h[:32]+"…"))
