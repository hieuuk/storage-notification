@echo off
schtasks /Create /TN "StorageMonitor" /TR "\"C:\Users\sshuser\AppData\Local\Programs\Python\Python312\pythonw.exe\" \"C:\Projects\storage-notification\monitor.py\"" /SC ONLOGON /RL HIGHEST /F
if %ERRORLEVEL% EQU 0 (
    echo Task created successfully. StorageMonitor will run on every logon.
    echo.
    echo To start it now without rebooting:
    schtasks /Run /TN "StorageMonitor"
) else (
    echo Failed to create task. Try running this script as Administrator.
)
pause
