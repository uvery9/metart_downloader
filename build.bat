@echo off
rd /s /q Release
md Release

echo "********************copy files********************"
copy urls.txt       Release
copy whitelist.txt  Release
copy blacklist.txt  Release

echo "********************build start********************"

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
