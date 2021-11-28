import os, sys

with open(sys.path[0] + "\\downloadlist.txt", "r") as listtxt:
    for i in listtxt.readlines():
        try:
            os.path.exists(sys.path[0]+"./download")
        except FileNotFoundError :
            os.mkdir(sys.path[0]+"./download")
        try:
            os.system(
                "python "
                + sys.path[0]
                + "\\bili_Download.py -ao -o "
                + sys.path[0]
                + "/download/ -a "
                + i
            )
        except Exception as e:
            print(e)
        print("*" * 40)
    print("全下载完啦")
