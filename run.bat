@echo off
copy urls.txt       Release
copy whitelist.txt  Release
copy blacklist.txt  Release
cd Release
.\metart_downloader.exe
pause
