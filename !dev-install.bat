@echo off
REM Reinstall cleanvibe from this checkout into the active Python.
REM Use this (not `pip install -e .`) when developing cleanvibe — see
REM README.md "Developer install" for the namespace-shadowing quirk that
REM editable installs hit on Windows when the parent dir is on sys.path.
cd /d "%~dp0"
python -m pip install . %*
