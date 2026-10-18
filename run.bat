@echo off
echo === Running tests ===
python -m pytest tests/
echo.
echo === Running application ===
python -m src.main --package test_pkg --repo-url http://example.com
pause