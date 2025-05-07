"""
ServerTab
=========   (wrapped in a centred  card)
"""

from __future__ import annotations
import subprocess, os, threading, queue, signal, datetime
import customtkinter as ctk
from ctk_gui.theme   import FONT_BODY, load_icon
from ctk_gui.common  import PY312, CHAT_DIR
from ctk_gui.ui_theme import style_utils

class ServerTab(ctk.CTkFrame):
    PORT = 4444

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        # ---------- responsive wrapper card ---------------------------------
        card = ctk.CTkFrame(self, corner_radius=12, fg_color="#ffffff")
        card.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(self, corner_radius=12, fg_color="#ffffff")
        card.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")

        style_utils.set_card_background(card)   # <── add this line

        # ---------- UI ------------------------------------------------------
        ctk.CTkLabel(card, text="Server Control",
                     font=("Segoe UI Semibold", 18)
                     ).pack(anchor="w", pady=(0,12))

        self.status = ctk.CTkLabel(card, text="Status: ⏹ Stopped", font=FONT_BODY)
        self.status.pack(anchor="w")

        btn_bar = ctk.CTkFrame(card, fg_color="transparent")
        btn_bar.pack(anchor="w", pady=8)

        self.start_btn = ctk.CTkButton(
            btn_bar, width=110, text="Start",
            image=load_icon("server.svg"), command=self._start
        )
        self.stop_btn  = ctk.CTkButton(
            btn_bar, width=110, text="Stop",
            image=load_icon("server.svg"), command=self._stop, state="disabled"
        )
        self.start_btn.pack(side="left", padx=(0,4))
        self.stop_btn .pack(side="left")

        self.tail = ctk.CTkTextbox(card, state="disabled", wrap="none", height=220)
        self.tail.pack(fill="both", expand=True, pady=(8,0))

        # ---------- runtime -------------------------------------------------
        self._proc: subprocess.Popen[str] | None = None
        self._q:   queue.Queue[str] = queue.Queue()
        self.after(200, self._drain_queue)

    # ── process control ----------------------------------------------------
    def _start(self):
        if self._proc and self._proc.poll() is None:
            return
        script = CHAT_DIR / "secure_chat_server.py"
        env    = os.environ.copy(); env["PYTHONUTF8"] = "1"

        self._proc = subprocess.Popen(
            [PY312, str(script), str(self.PORT)],
            cwd=str(CHAT_DIR), env=env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1,
        )
        threading.Thread(target=self._reader, daemon=True).start()
        self._set_state(True)

    def _stop(self):
        if self._proc and self._proc.poll() is None:
            self._proc.send_signal(signal.SIGINT)
            self._proc.wait(timeout=5)
        self._set_state(False)

    # ── helpers ------------------------------------------------------------
    def _set_state(self, running: bool):
        self.status.configure(text=f"Status: {'🟢 Running' if running else '⏹ Stopped'}")
        self.start_btn.configure(state=("disabled" if running else "normal"))
        self.stop_btn .configure(state=("normal" if running else "disabled"))

    def _reader(self):
        assert self._proc and self._proc.stdout
        for line in self._proc.stdout:
            self._q.put(line.rstrip())
        self._q.put("[Server] exited")

    def _drain_queue(self):
        try:
            while True:
                ln = self._q.get_nowait()
                self._append(ln)
        except queue.Empty:
            pass
        self.after(200, self._drain_queue)

    def _append(self, txt: str):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.tail.configure(state="normal")
        self.tail.insert("end", f"[{ts}] {txt}\n")
        self.tail.configure(state="disabled")
        self.tail.see("end")

    # exposed for ClientTab
    @property
    def is_running(self): return self._proc and self._proc.poll() is None
    @property
    def port(self):       return self.PORT
