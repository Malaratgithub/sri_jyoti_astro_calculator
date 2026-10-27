@echo off
cd /d "%~dp0"
title Sri Jyoti Astro v1.6 - Arial Report and Worldwide Birthplaces
py -3 -m pip install -r requirements.txt
if errorlevel 1 pause & exit /b 1
py -3 server.py
pause
