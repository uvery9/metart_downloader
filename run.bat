@echo off

xcopy urls.txt       Release\ /d /y /i /q
xcopy whitelist.txt  Release\ /d /y /i /q
xcopy blacklist.txt  Release\ /d /y /i /q
xcopy MetArtDownloader.config.ini  Release\ /d /y /i /q

cd Release
.\MetArtDownloader.exe
pause
