@echo off
cd /d %~dp0
rem ─── Install GUI deps on first run (system Python 3.12) ─────────────

rem ─── Launch the Qt demo UI ─────────────────────────────────────────
py -3.12 -m ctk_gui.launcher
