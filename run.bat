@echo off

xcopy urls.txt       Release\ /d /y /i /q
xcopy whitelist.txt  Release\ /d /y /i /q
xcopy blacklist.txt  Release\ /d /y /i /q

cd Release
.\metart_downloader.exe
pause
