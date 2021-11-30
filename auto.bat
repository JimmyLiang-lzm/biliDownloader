@echo off
:select
set location=%~dp0
set flag=0
echo 请输入音频格式或者选择批量下载
echo 请输入数字1-4
echo 1.aac
echo 2.m4a
echo 3.mp3
echo 4.批量下载
set /p type=请输入：
if %type% == 1 goto aac
if %type% == 2 goto m4a
if %type% == 3 goto mp3
if %type% == 4 goto batchformat
if not %type% == 1 (if not %type% == 2 (if not %type% == 3 (if not %type% == 4 goto again)))
exit

:aac
set format=-aac
if %flag% == 0 goto download
if %flag% == 1 goto batch
exit

:m4a
set format=-m4a
if %flag% == 0 goto download
if %flag% == 1 goto batch
exit

:mp3
set format=-mp3
if %flag% == 0 goto download
if %flag% == 1 goto batch
exit

:download
set /p url=请粘贴视频链接：
start cmd /k "cd /d %location%&&python bili_Download.py -a %url% %format%"
goto download
exit

:batchformat
set flag=1
echo 请选择批量下载格式
echo 请输入数字1-3
echo 1.aac
echo 2.m4a
echo 3.mp3
set /p batchtype=请输入：
if %batchtype% == 1 goto aac
if %batchtype% == 2 goto m4a
if %batchtype% == 3 goto mp3
if not %type% == 1 (if not %type% == 2 (if not %type% == 3 goto again))
exit

:batch
start cmd /k "cd /d %location%&&python ASoulMP3maker.py %format%"
exit

:again
cls
echo 输入错误，请重新输入
if %flag% == 0 goto select
if %flag% == 1 goto batchformat
exit()