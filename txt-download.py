import os,sys
with open(sys.path[0]+'\\downloadlist.txt', "r") as listtxt:
    for i in listtxt.readlines():
        os.system('python ' + sys.path[0] + '\\bili_Download.py -ao -a ' + i)
        print('*'*20)
    print('全下载完啦')