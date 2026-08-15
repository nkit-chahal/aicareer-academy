@echo off
echo === Scraping schoolofcoreai.com ===
python build\scrape.py
if errorlevel 1 exit /b 1

echo.
echo === Generating static site ===
python build\generate.py
if errorlevel 1 exit /b 1

echo.
echo === Link audit ===
python build\link_audit.py
if errorlevel 1 exit /b 1

echo.
echo Done. Preview with: cd site ^&^& python -m http.server 8080
