# This Python file uses the following encoding: utf-8
import os
import sys
import argparse

parser = argparse.ArgumentParser(description='Asoul\'s song Downloader')
parser.add_argument('-mp3', '--audio-mp3', dest='AudioMP3',
                    action='store_true', help='download mp3 Audio Only')
parser.add_argument('-m4a', '--audio-m4a', dest='AudioM4A',
                    action='store_true', help='download m4a Audio Only')
args = parser.parse_args()
type = 'mp3' if args.AudioMP3 else 'm4a'

with open(sys.path[0] + r"/downloadlist.txt", "r") as listtxt:
    for i in listtxt.readlines():
        try:
            os.path.exists(sys.path[0]+r"/download")
        except FileNotFoundError :
            os.mkdir(sys.path[0]+r"/download")
        try:
            os.system(
                "python3 "
                + sys.path[0]
                + r"/bili_Download.py -o"
                + sys.path[0]
                + '/download -'
                + type
                + ' -a '
                + i
            )
        except Exception as e:
            print(e)
        print("*" * 40)
    print("finished")
