@echo off
rd /s /q Release
md Release

pyinstaller  -F -i metart.ico metart_downloader.py
move /y dist\metart_downloader.exe Release\metart_downloader.exe

pyinstaller  -F -w -i metart.ico metart_downloader.py
move /y dist\metart_downloader.exe Release\metart_downloader_noconsole.exe

echo "********************built********************"

::clean
echo "********************cleaning temp files********************"
rd /s /q build
rd /s /q __pycache__
del /q metart_downloader.spec
rd /s /q dist

echo "********************succeed********************"

pause
