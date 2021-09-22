@echo off
setlocal enableextensions
setlocal enabledelayedexpansion

IF %1.==. (
	for /f "tokens=2 skip=1" %%F IN (' nslookup %USERDNSDOMAIN% ^| find "Address" ') DO SET conn=%%F
	) ELSE (
	SET conn=%1 )

SET dtime=%time%:%date%

curl -k https://%conn%:5000/monitor?action=0^&user=%USERNAME%^&pc=%COMPUTERNAME%^&time=%dtime%^&domain=%USERDNSDOMAIN%