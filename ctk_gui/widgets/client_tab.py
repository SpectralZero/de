"""
ClientTab  – launch / kill demo clients, filter table (now in a card).
"""

from __future__ import annotations
import subprocess, os, queue, threading, signal, pathlib, re
import customtkinter as ctk
from tkinter import ttk, messagebox
from ctk_gui.common import PY312, CHAT_DIR
from ctk_gui.ui_theme import style_utils



class ClientTab(ctk.CTkFrame):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)

        # ---------- wrapper card -------------------------------------------
        card = ctk.CTkFrame(self, corner_radius=12, fg_color="#ffffff")
        card.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")
        self.grid_rowconfigure(0, weight=1); self.grid_columnconfigure(0, weight=1)

        card.grid_rowconfigure(3, weight=1)   # table row stretches
        card.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(self, corner_radius=12, fg_color="#ffffff")
        card.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")

        style_utils.set_card_background(card)   # <── add this line 

        # ---------- discover scripts ---------------------------------------
        root = CHAT_DIR
        self.cfg: dict[str, tuple[pathlib.Path,int]] = {
            "Client 1": (root/"secure_chat_client1.py", 12346),
            "Client 2": (root/"secure_chat_client2.py", 12347),
            "Client 3": (root/"secure_chat_client3.py", 12348),
        }
        self._procs: dict[str, subprocess.Popen[str]] = {}
        self._q: queue.Queue[tuple[str,str]] = queue.Queue()

        # ---------- toolbar -------------------------------------------------
        bar = ctk.CTkFrame(card, fg_color="transparent")
        bar.grid(row=0, column=0, sticky="w", pady=(0,6))

        def pill(txt, clr, cmd):
            return ctk.CTkButton(bar, text=txt, fg_color=clr,
                                 width=95, corner_radius=6, command=cmd)
        pill("Launch",     "#424242", self.launch_selected).pack(side="left", padx=4)
        pill("Launch All", "#2e7d32", self.launch_all).pack(side="left", padx=4)
        pill("Kill",       "#c62828", self.kill_selected).pack(side="left", padx=4)
        pill("Clear",      "#1565c0", self.clear_empty).pack(side="left", padx=4)

        # ---------- filter row ---------------------------------------------
        flt = ctk.CTkFrame(card, fg_color="transparent")
        flt.grid(row=1, column=0, sticky="ew")
        flt.grid_columnconfigure(2, weight=1)

        self.combo_client = ctk.CTkOptionMenu(flt, values=["ALL"]+list(self.cfg))
        self.combo_state  = ctk.CTkOptionMenu(flt, values=["ALL","idle","running","exited","killed"])
        self.search       = ctk.CTkEntry      (flt, placeholder_text="Search…")

        self.combo_client.grid(row=0,column=0,padx=(0,4))
        self.combo_state .grid(row=0,column=1,padx=4)
        self.search      .grid(row=0,column=2,padx=(4,0),sticky="ew")

        for w in (self.combo_client, self.combo_state):
            w.configure(command=lambda *_: self._apply_filter())
        self.search.bind("<KeyRelease>", lambda *_: self._apply_filter())

        # ---------- table ---------------------------------------------------
        tbl_frm = ctk.CTkFrame(card, fg_color="transparent")
        tbl_frm.grid(row=3, column=0, sticky="nsew")
        tbl_frm.grid_rowconfigure(0, weight=1)
        tbl_frm.grid_columnconfigure(0, weight=1)

        cols = ("pid","client","state")
        self.tree = ttk.Treeview(tbl_frm, columns=cols, show="headings")

        for c,w in zip(cols,(90,160,90)):
            self.tree.heading(c,text=c.upper())
            self.tree.column(c,width=w,anchor="w",stretch=True)

        ysb = ttk.Scrollbar(tbl_frm, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=ysb.set)
        self.tree.grid(row=0,column=0,sticky="nsew")
        ysb .grid(row=0,column=1,sticky="ns")

        for name in self.cfg:
            self.tree.insert("", "end", iid=name, values=("", name, "idle"))

        self.after(300, self._poll_queue)

    # ---------- Spawning / Killing -----------------------------------------
    def _spawn(self, iid:str):
        if self.tree.set(iid,"pid"):   # already running
            return
        script, port = self.cfg[iid]
        env = os.environ.copy(); env["PYTHONUTF8"]="1"

        proc = subprocess.Popen(
            [PY312, str(script),"localhost","4444",str(port)],
            cwd=str(CHAT_DIR), env=env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1,
        )
        self._procs[iid] = proc
        self.tree.item(iid, values=(proc.pid, iid, "running"))
        threading.Thread(target=self._reader, args=(iid,proc), daemon=True).start()

    def _reader(self, iid:str, proc: subprocess.Popen[str]):
        assert proc.stdout
        for ln in proc.stdout:
            self._q.put((iid, ln.rstrip()))
        self._q.put((iid, "[exited]"))

    # ---------- Buttons -----------------------------------------------------
    def launch_selected(self):
        if not self.tree.selection():
            messagebox.showinfo("Nothing selected","Select one or more rows.")
            return
        for iid in self.tree.selection():
            self._spawn(iid)

    def launch_all(self):   [self._spawn(i) for i in self.cfg]
    def kill_selected(self):
        for iid in self.tree.selection():
            p = self._procs.pop(iid,None)
            if p and p.poll() is None:
                p.send_signal(signal.SIGINT)
            self.tree.item(iid, values=("", iid, "killed"))
    def clear_empty(self):
        for iid in list(self.tree.get_children()):
            pid,state = self.tree.set(iid,"pid"), self.tree.set(iid,"state")
            if not pid and state in ("exited","killed"):
                self.tree.delete(iid)

    # ---------- Filtering ---------------------------------------------------
    def _apply_filter(self):
        clt, st, pat = self.combo_client.get(), self.combo_state.get(), self.search.get().lower()

        for iid in self.cfg:
            pid, client, state = self.tree.item(iid,"values")
            visible = (
                (clt=="ALL" or client==clt) and
                (st =="ALL" or state ==st)   and
                (not pat or pat in client.lower())
            )
            self.tree.detach(iid) if not visible else self.tree.reattach(iid,"","end")

    # ---------- Queue poll --------------------------------------------------
    def _poll_queue(self):
        try:
            while True:
                iid, line = self._q.get_nowait()
                if "[exited]" in line:
                    self.tree.item(iid, values=("", iid, "exited"))
        except queue.Empty:
            pass
        self.after(300, self._poll_queue)
