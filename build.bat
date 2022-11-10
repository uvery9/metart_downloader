@echo off
rd /s /q Release
md Release

echo "********************copy files********************"
copy urls.txt       Release
copy whitelist.txt  Release
copy blacklist.txt  Release
copy MetArtDownloader.config.ini  Release

echo "********************build start********************"

pip install -r Requirements
pyinstaller  -F -i metart.ico MetArtDownloader.py
move /y dist\MetArtDownloader.exe Release\MetArtDownloader.exe

pyinstaller  -F -w -i metart.ico MetArtDownloader.py
move /y dist\MetArtDownloader.exe Release\MetArtDownloaderSlient.exe

:: echo "********************built********************"

:: clean
echo "********************cleaning temp files********************"
rd /s /q build
rd /s /q __pycache__
del /q MetArtDownloader.spec
rd /s /q dist
:: 
:: "C:\Program Files\7-Zip\7z.exe" a MetArtDownloader.7z Release
:: move /y MetArtDownloader.7z Release\MetArtDownloader.7z

echo "********************succeed********************"

pause
