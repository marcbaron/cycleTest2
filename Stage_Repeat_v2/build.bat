@echo off
set IRONPYTHON=c:\Program Files (x86)\IronPython 2.7

set IPY="%IRONPYTHON%\ipy.exe"
set PYC="%IRONPYTHON%\Tools\Scripts\pyc.py"

set OUT=Stage_Repeat_V2

del build\%OUT%.*
copy "%IRONPYTHON%\*.dll" build\
copy "%IRONPYTHON%\DLLs\IronPython.Wpf.dll" build\

%IPY% %PYC% /out:%OUT% /target:winexe src/arduino.py src/gui.py src/driver.py src/pyevent.py src/syringe.py /main:src/main.py /embed
move %OUT%.* build\
copy src\precision.png build\
copy src\pyserialV2.ino build\