# This Python file uses the following encoding: utf-8
import os, sys

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
                + r"/bili_Download.py -ao -o "
                + sys.path[0]
                + r"/download/ -a "
                + i
            )
        except Exception as e:
            print(e)
        print("*" * 40)
    print("finished")
