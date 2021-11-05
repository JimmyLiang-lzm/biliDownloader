@echo off
echo --------------------------------------------------------------------------------
echo                         Bili Downloader Starter V3.0(bat)
echo --------------------------------------------------------------------------------
echo optional arguments:
echo  -h, --help            show this help message and exit
echo  -a ADDRESS, --address ADDRESS
echo                        Input the HTTP/HTTPS address of video page.
echo  -o OUTPUT, --output OUTPUT
echo                        Output folder location of Video(s).
echo  -l DOWNLIST, --download-list DOWNLIST
echo                        The List of Download partition video.
echo  -vq VIDEOQUALITY, --video-quality VIDEOQUALITY
echo                        Videos quality. You can use "-c" or "--check" to view
echo                        it, default is 0.
echo  -ar AUDIOQUALITY, --audio-quality AUDIOQUALITY
echo                        Audio quality. You can use "-c" or "--check" to view
echo                        it, default is 0.
echo  -s {0,1}, --synthesis {0,1}
echo                        Perform video synthesis after downloading audio and
echo                        video streams. You HAVE TO make sure FFMPEG executable
echo                        program is exist.
echo  -i, --interact        For download interactive video.
echo  -c, --check           Show video and audio download stream.
echo  -v, --version         show program's version number and exit
echo --------------------------------------------------------------------------------
echo Please enter your command:
cmd /k cd %cd%\bili_Download
