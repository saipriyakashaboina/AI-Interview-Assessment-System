@echo off
title AI Interview Assessment - Project

cd /d C:\Users\SaiPranavi\Desktop\AI_Interview_MiniProject\elevra

start "Backend" cmd /k "cd /d C:\Users\SaiPranavi\Desktop\AI_Interview_MiniProject\elevra\backend && ..\.venv\Scripts\activate && uvicorn app.main:app --reload --port 8001"

start "Frontend" cmd /k "cd /d C:\Users\SaiPranavi\Desktop\AI_Interview_MiniProject\elevra\frontend && npm run dev"

timeout /t 5 /nobreak >nul

start http://127.0.0.1:5173