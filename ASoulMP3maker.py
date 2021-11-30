# This Python file uses the following encoding: utf-8
import os
import sys
import argparse
import subprocess

parser = argparse.ArgumentParser(description='Asoul\'s song Downloader')
parser.add_argument('-mp3', '--audio-mp3', dest='AudioMP3',
                    action='store_true', help='download mp3 Audio Only')
parser.add_argument('-m4a', '--audio-m4a', dest='AudioM4A',
                    action='store_true', help='download m4a Audio Only')
args = parser.parse_args()
type = 'mp3' if args.AudioMP3 else 'm4a'

pycmd = 'python' if sys.platform=='win32' else 'python3'
#pycmd = 'python3'

with open(sys.path[0] + r"/downloadlist.txt", "r") as listtxt:
    errorlist = []
    lowQlist = []
    os.chdir(sys.path[0])
    for i in listtxt.readlines():
        try:
            os.path.exists(sys.path[0]+r"/download")
        except FileNotFoundError:
            os.mkdir(sys.path[0]+r"/download")
        try:
            one_audio = subprocess.run(
                [pycmd,
                r"./bili_Download.py",
                "-o",
                './download',
                '-'+type,
                '-a',
                i.replace('\n','')]
            )
            if one_audio.returncode == 1: 
                errorlist.append(i)
            elif one_audio.returncode == 2:
                lowQlist.append(i)
        except Exception as e:
            print(e)
        print("*" * 40)
    print('finished')
    if errorlist:
        print('以下链接视频下载失败，共计',len(errorlist),'个')
        print(errorlist)
    if lowQlist:
        print('一下链接的码率低于128k，但仍下载下来了')
        print(lowQlist)
