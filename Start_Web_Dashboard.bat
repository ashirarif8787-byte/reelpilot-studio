@echo off
title Social Media Automation & Scheduler Web Dashboard
cd /d "%~dp0"
echo ================================================================
echo   Starting Social Media Automation & Scheduler App...
echo   Opening Web Dashboard at http://localhost:5000
echo ================================================================
start http://localhost:5000
.\.venv\Scripts\python.exe web_app.py
pause
