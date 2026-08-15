@echo off
echo Starting server at http://localhost:8080
echo Open http://localhost:8080 in your browser
cd /d "%~dp0site"
python -m http.server 8080
