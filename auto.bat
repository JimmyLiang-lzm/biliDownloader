@echo off
:select
set location=%~dp0
set flag=0
echo ��������Ƶ��ʽ����ѡ����������
echo ����������1-4
echo 1.aac
echo 2.m4a
echo 3.mp3
echo 4.��������
set /p type=�����룺
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
set /p url=��ճ����Ƶ���ӣ�
start cmd /k "cd /d %location%&&python bili_Download.py -a %url% %format%"
goto download
exit

:batchformat
set flag=1
echo ��ѡ���������ظ�ʽ
echo ����������1-3
echo 1.aac
echo 2.m4a
echo 3.mp3
set /p batchtype=�����룺
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
echo �����������������
if %flag% == 0 goto select
if %flag% == 1 goto batchformat
exit()