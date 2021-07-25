@echo off
setlocal enableextensions
setlocal enabledelayedexpansion 
FOR /F "tokens=* USEBACKQ" %%F IN (`netstat -n ^| find "3389" ^| find "ESTABLISHED" /c`) DO SET /A var=%%F

SET IP=None
SET MAC=None
SET /A RDP=0
IF %VAR%==1 (
    SET /A RDP = 1
    FOR /F "tokens=2 delims=:,  USEBACKQ"  %%F IN (`netstat -n ^| find "3389" ^| find "ESTABLISHED"`) DO SET temp=%%F
    FOR /F "tokens=2 USEBACKQ" %%F IN (`echo !temp! `) DO SET IP=%%F
    FOR /F "tokens=2 skip=3" %%F in (' arp -a !IP! ') DO SET MAC=%%F
)

SET DTIME=%time%:%date%

IF %1.==. (
	for /f "tokens=2 skip=1" %%F IN (' nslookup %USERDNSDOMAIN% ^| find "Address" ') DO SET conn=%%F
	) ELSE (
	SET conn=%1 )

curl -k https://%conn%:5000/monitor?check=1^&action=1^&rdp=%RDP%^&ip=%IP%^&user=%USERNAME%^&mac=%MAC%^&pc=%COMPUTERNAME%^&time=%DTIME%^&domain=%USERDNSDOMAIN%
