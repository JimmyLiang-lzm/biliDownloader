import os,sys
import argparse
import requests,re,json
from tqdm import tqdm
import subprocess

# Default Path
DF_Path = os.path.dirname(os.path.realpath(sys.argv[0]))

parser = argparse.ArgumentParser(description='Bilibili Video Downloader')
parser.add_argument('-a','--address',dest='Address',type=str,default=None,action='store',help='Input the HTTP/HTTPS address of video page.')
parser.add_argument('-ma','--music-address',dest='MAddress',type=str,default=None,action='store',help='Input the HTTP/HTTPS address of music page.')
parser.add_argument('-o','--output',dest='Output',type=str,default=DF_Path,action='store',help='Output folder location of Video(s).')
parser.add_argument('-l','--download-list',dest='DownList',type=str,default=None,action='store',help='The List of Download partition video.')
parser.add_argument('-vq','--video-quality',dest='VideoQuality',type=int,default=0,action='store',help='Videos quality. You can use "-c" or "--check" to view it, default is 0.')
parser.add_argument('-ar','--audio-quality',dest='AudioQuality',type=int,default=0,action='store',help='Audio quality. You can use "-c" or "--check" to view it, default is 0.')
parser.add_argument('-s','--synthesis',dest='Synthesis',type=int,default=1,choices=[0,1],help='Perform video synthesis after downloading audio and video streams.\nYou HAVE TO make sure FFMPEG executable program is exist.')
parser.add_argument('-i','--interact',action='store_true',help='For download interactive video.')
parser.add_argument('-c','--check',action='store_true',help='Show video and audio download stream.')
parser.add_argument('-v','--version',action='version',version='Bilibili Downloader == 3.1')
args = parser.parse_args()
assert args.Address or args.MAddress is not None
#print(args)

class bili_downloader(object):
    # Parameter Initialize
    def __init__(self,args):
        if args.Address is None:
            self.index_url = args.MAddress
        else:
            self.index_url = args.Address
        self.d_list = args.DownList
        self.VQuality = args.VideoQuality
        self.AQuality = args.AudioQuality
        self.output = args.Output
        self.synthesis = args.Synthesis
        self.re_playinfo = 'window.__playinfo__=([\s\S]*?)</script>'
        self.re_INITIAL_STATE = 'window.__INITIAL_STATE__=([\s\S]*?);\(function'
        self.vname_expression = '<title(.*?)</title>'
        self.chunk_size = 1024
        self.index_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
        }
        self.second_headers = {
            "accept": "*/*",
            "Connection": "keep-alive",
            "accept-encoding": "identity",
            "accept-language": "zh-CN,zh;q=0.9",
            "origin": "https://www.bilibili.com",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "cors",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
        }
        with open('setting.conf', 'r', encoding='utf-8') as f:
            tempr = json.loads(f.read())
            self.index_headers["cookie"] = tempr["cookie"]
            self.second_headers["cookie"] = tempr["cookie"]
            self.systemd = tempr["sys"]
            if tempr["Proxy"] != "":
                self.Proxy = {'http': tempr["Proxy"],'https':tempr["Proxy"],}
            else:
                self.Proxy = {}

    # File name conflict replace
    def name_replace(self,name):
        vn = name.replace(' ', '_').replace('\\', '').replace('/', '')
        vn = vn.replace('*', '').replace(':', '').replace('?', '').replace('<', '')
        vn = vn.replace('>', '').replace('\"', '').replace('|', '')
        return vn

    # Change /SS movie address
    def ssADDRCheck(self,inurl):
        checking1 = re.findall('/play/ss',inurl.split("?")[0],re.S)
        checking2 = re.findall('/play/ep', inurl.split("?")[0], re.S)
        if checking1 != []:
            res = requests.get(inurl, headers=self.index_headers, stream=False,proxies=self.Proxy)
            dec = res.content.decode('utf-8')
            INITIAL_STATE = re.findall(self.re_INITIAL_STATE, dec, re.S)
            temp = json.loads(INITIAL_STATE[0])
            self.index_url = temp["mediaInfo"]["episodes"][0]["link"]
            return 1, temp["mediaInfo"]["episodes"][0]["link"]
        elif checking2 != []:
            return 1, inurl
        else:
            return 0, inurl

    # Searching Key Word
    def search_preinfo(self,index_url):
        # Get Html Information
        index_url = self.ssADDRCheck(index_url)
        res = requests.get(index_url[1],headers=self.index_headers,stream=False,proxies=self.Proxy)
        dec = res.content.decode('utf-8')
        # Use RE to find Download JSON Data
        playinfo = re.findall(self.re_playinfo, dec, re.S)
        INITIAL_STATE = re.findall(self.re_INITIAL_STATE,dec,re.S)
        # If Crawler can GET Data
        if playinfo == [] or INITIAL_STATE == []:
            print("Session等初始化信息获取失败。")
            return 0, "", "", {}
        re_init = json.loads(INITIAL_STATE[0])
        re_GET = json.loads(playinfo[0])
        if index_url[0] == 0:
            now_cid = re_init["videoData"]["pages"][re_init["p"] - 1]["cid"]
            try:
                makeurl = "https://api.bilibili.com/x/player/playurl?cid=" + str(now_cid) + \
                          "&qn=116&type=&otype=json&fourk=1&bvid=" + re_init["bvid"] + \
                          "&fnver=0&fnval=976&session=" + re_GET["session"]
                self.second_headers['referer'] = index_url[1]
                res = requests.get(makeurl, headers=self.second_headers, stream=False, timeout=10, proxies=self.Proxy)
                re_GET = json.loads(res.content.decode('utf-8'))
                # print(json.dumps(re_GET))
            except Exception as e:
                print("获取Playlist失败:", e)
                return 0, "", "", {}
        # If Crawler can GET Data
        try:
            # Get video name
            vn1 = re.findall(self.vname_expression, dec, re.S)[0].split('>')[1]
            vn2 = ""
            if "videoData" in re_init:
                vn2 = re_init["videoData"]["pages"][re_init["p"]-1]["part"]
            elif "mediaInfo" in re_init:
                vn2 = re_init["epInfo"]["titleFormat"] + ":" + re_init["epInfo"]["longTitle"]
            video_name = self.name_replace(vn1) + "_[" + self.name_replace(vn2) + "]"
            # List Video Quality Table
            temp_v = {}
            for i in range(len(re_GET["data"]["accept_quality"])):
                temp_v[str(re_GET["data"]["accept_quality"][i])] = str(re_GET["data"]["accept_description"][i])
            # List Video Download Quality
            down_dic = {"video": {}, "audio": {}}
            i = 0
            # Get Video identity information and Initial SegmentBase.
            for dic in re_GET["data"]["dash"]["video"]:
                if str(dic["id"]) in temp_v:
                    qc = temp_v[str(dic["id"])]
                    down_dic["video"][i] = [qc, [dic["baseUrl"]], 'bytes=' + dic["SegmentBase"]["Initialization"]]
                    for a in range(len(dic["backupUrl"])):
                        down_dic["video"][i][1].append(dic["backupUrl"][a])
                    i += 1
                else:
                    continue
            # List Audio Stream
            i = 0
            for dic in re_GET["data"]["dash"]["audio"]:
                au_stream = dic["codecs"] + "  音频带宽：" + str(dic["bandwidth"])
                down_dic["audio"][i] = [au_stream, [dic["baseUrl"]],'bytes=' + dic["SegmentBase"]["Initialization"]]
                for a in range(len(dic["backupUrl"])):
                    down_dic["audio"][i][1].append(dic["backupUrl"][a])
                i += 1
            # Get Video Length
            length = re_GET["data"]["dash"]["duration"]
            # Return Data
            return 1, video_name, length, down_dic
        except Exception as e:
            print("PreInfo:", e)
            return 0, "", "", {}

    def search_videoList(self,index_url):
        res = requests.get(index_url, headers=self.index_headers, stream=False, proxies=self.Proxy)
        dec = res.content.decode('utf-8')
        INITIAL_STATE = re.findall(self.re_INITIAL_STATE, dec, re.S)
        if INITIAL_STATE != []:
            re_init = json.loads(INITIAL_STATE[0])
            init_list = {}
            if "videoData" in re_init:
                init_list["bvid"] = re_init["bvid"]
                init_list["p"] = re_init["p"]
                init_list["pages"] = re_init["videoData"]["pages"]
                return 1,init_list
            elif "mediaInfo" in re_init:
                init_list["bvid"] = re_init["mediaInfo"]["media_id"]
                init_list["p"] = re_init["epInfo"]["i"]
                init_list["pages"] = re_init["mediaInfo"]["episodes"]
                return 2,init_list
            else:
                return 0,{}
        else:
            return 0,{}

    # Show preDownload Detail
    def show_preDetail(self):
        #flag,video_name,length,down_dic,init_list = self.search_preinfo()
        temp = self.search_preinfo(self.index_url)
        preList = self.search_videoList(self.index_url)
        if temp[0] and preList[0] != 0:
            if preList[0] == 1:
                # Show video pages
                print('当前需要下载的BV号为：',preList[1]["bvid"])
                print('当前BV包含视频数量为%d个'%len(preList[1]["pages"]))
                print('-----------具体分P视频名称与下载号-----------')
                for sp in preList[1]["pages"]:
                    print("{}-->分P名称：{}".format(sp["page"],sp["part"]))
            elif preList[0] == 2:
                # Show media pages
                print('当前需要下载的媒体号为：', preList[1]["bvid"])
                print('当前媒体包含视频数量为%d个' % len(preList[1]["pages"]))
                print('-----------具体分P视频名称与下载号-----------')
                for sp in preList[1]["pages"]:
                    print("{}-->分P名称：{}".format(sp["title"], sp["share_copy"]))
            print('--------------------我是分割线--------------------')
            # Show Video Download Detail
            print('当前下载视频名称：', temp[1])
            print('当前下载视频长度： {} 秒'.format(temp[2]))
            print('当前可下载视频流：')
            for i in range(len(temp[3]["video"])):
                print("{}-->视频画质：{}".format(i, temp[3]["video"][i][0]))
                ic = 1
                for bc_url in temp[3]["video"][i][1]:
                    print("    下载地址{}：{}".format(ic, bc_url.split("?")[0]))
                    ic += 1
            # Show Audio Download Detail
            print('--------------------我是分割线--------------------')
            print('当前可下载音频流：')
            for i in range(len(temp[3]["audio"])):
                print("{}-->音频编码：{}".format(i, temp[3]["audio"][i][0]))
                ic = 1
                for bc_url in temp[3]["audio"][i][1]:
                    print("    下载地址{}：{}".format(ic, bc_url.split("?")[0]))
                    ic += 1
        else:
            print("尚未找到源地址，请检查网站地址或充值大会员！")

    # Download Stream fuction
    def d_processor(self,url_list,output_dir,output_file,dest):
        for line in url_list:
            print('使用线路：', line.split("?")[0])
            try:
                # video stream length sniffing
                video_bytes = requests.get(line, headers=self.second_headers, stream=False, proxies=self.Proxy)
                vc_range = video_bytes.headers['Content-Range'].split('/')[1]
                print("获取{}流范围为：{}".format(dest,vc_range))
                print('{}文件大小：{} MB'.format(dest,round(float(vc_range) / self.chunk_size / 1024), 4))
                # Get the full video stream
                self.second_headers['range'] = 'bytes=0' + '-' + vc_range
                m4sv_bytes = requests.get(line, headers=self.second_headers, stream=True, proxies=self.Proxy)
                pbar = tqdm(total=int(vc_range), initial=0, unit='b', leave=True, desc='正在'+dest, unit_scale=True)
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                with open(output_file, 'ab') as f:
                    for chunks in m4sv_bytes.iter_content(chunk_size=self.chunk_size):
                        if chunks:
                            f.write(chunks)
                            pbar.update(self.chunk_size)
                pbar.close()
                print("{}成功！".format(dest))
                break
            except Exception as e:
                print("{}出错：{}".format(dest,e))
                os.remove(output_dir)

    # Synthesis audio and video function
    def ffmpeg_synthesis(self,input_v,input_a,output_add):
        ffcommand = ""
        if self.systemd == "windows":
            ffpath = os.path.dirname(os.path.realpath(sys.argv[0]))
            ffcommand = ffpath + '/ffmpeg.exe -i ' + input_v + ' -i ' + input_a + ' -c:v copy -c:a copy -strict experimental ' + output_add
        elif self.systemd == "unix":
            ffcommand = 'ffmpeg -i ' + input_v + ' -i  ' + input_a + ' -c:v copy -c:a copy -strict experimental ' + output_add
        else:
            print("未知操作系统：无法确定FFMpeg命令。")
            return -2
        try:
            if subprocess.call(ffcommand, shell=True):
                raise Exception("{} 执行失败。".format(ffcommand))
            print("视频合并完成！")
            os.remove(input_v)
            os.remove(input_a)
        except Exception as e:
            print("视频合成失败：", e)

    # For Download Single Video
    def Download_single(self, index=""):
        # Get video pre-detial
        if index == "":
            flag, video_name, _, down_dic = self.search_preinfo(self.index_url)
            index = self.index_url
        else:
            flag, video_name, _, down_dic = self.search_preinfo(index)
        # If we can access the video page
        if flag:
            # Judge file whether exists
            video_dir = self.output + '/' + video_name + '_video.m4s'
            audio_dir = self.output + '/' + video_name + '_audio.m4s'
            if os.path.exists(video_dir):
                print("文件：{}\n已存在。".format(video_dir))
                return -1
            if os.path.exists(audio_dir):
                print("文件：{}\n已存在。".format(audio_dir))
                return -1
            print("需要下载的视频：",video_name)
            # Perform video stream length sniffing
            self.second_headers['referer'] = index
            self.second_headers['range'] = down_dic["video"][self.VQuality][2]
            # Switch between main line and backup line(video).
            self.d_processor(down_dic["video"][self.VQuality][1],self.output,video_dir,"下载视频")
            # Perform audio stream length sniffing
            self.second_headers['range'] = down_dic["audio"][self.AQuality][2]
            # Switch between main line and backup line(audio).
            self.d_processor(down_dic["audio"][self.AQuality][1],self.output,audio_dir,"下载音频")
            # Merge audio and video (USE FFMPEG)
            if self.synthesis:
                print('正在启动ffmpeg......')
                # Synthesis processor
                self.ffmpeg_synthesis(video_dir,audio_dir,self.output + '/' + video_name + '.mp4')
        else:
            print("下载失败：尚未找到源地址，请检查网站地址或充值大会员！")

    # Args to List
    def args2list(self):
        strlist = self.d_list.split(',')
        se_list = []
        for num in strlist:
            divi_num = num.split("-")
            if len(divi_num) == 1:
                se_list.append(int(divi_num[0]))
            elif len(divi_num) == 2:
                ovlist = list(map(int, divi_num))
                for i in range(ovlist[0], ovlist[1]):
                    se_list.append(i)
                se_list.append(ovlist[1])
            else:
                continue
        return se_list

    # For Download partition Video
    def Download_List(self):
        r_list = self.args2list()
        all_list = self.search_videoList(self.index_url)
        preIndex = self.index_url.split("?")[0]
        if all_list[0] == 1:
            if r_list[0] == 0:
                for p in all_list[1]["pages"]:
                    self.Download_single(preIndex+"?p="+str(p["page"]))
                print("列表视频下载完成！")
            else:
                listLEN = len(all_list[1]["pages"])
                for i in r_list:
                    if i <= listLEN:
                        self.Download_single(preIndex+"?p="+str(i))
                    else:
                        continue
                print("列表视频下载完成！")
        if all_list[0] == 2:
            if r_list[0] == 0:
                for p in all_list[1]["pages"]:
                    self.Download_single(p["link"])
                print("媒体视频下载完成！")
            else:
                listLEN = len(all_list[1]["pages"])
                for i in r_list:
                    if i <= listLEN:
                        self.Download_single(all_list[1]["pages"][i-1]["link"])
                    else:
                        continue
                print("媒体视频下载完成！")
        else:
            print("未找到视频列表信息。")

    # Interactive video download
    def requests_start(self):
        url = self.index_url
        self.now_interact = {"cid": "", "bvid": "", "session": "", "graph_version": "", "node_id": "", "vname": ""}
        iv_structure = {}
        t = self.Get_Init_Info(url)
        if t[0]:
            print(t[1])
            return -1
        self.index_headers['referer'] = url
        self.second_headers = self.index_headers
        t = self.isInteract()
        if t[0]:
            print(t[1])
            return -1
        print(self.now_interact)
        iv_structure[self.now_interact["vname"]] = {}
        iv_structure[self.now_interact["vname"]] = self.recursion_GET_List()
        # print(json.dumps(iv_structure))
        self.recursion_for_Download(iv_structure, self.output)
        print("下载交互视频成功。")


    # Interactive video initial information
    def Get_Init_Info(self, url):
        try:
            res = requests.get(url,headers=self.index_headers,stream=False, proxies=self.Proxy)
            dec = res.content.decode('utf-8')
            playinfo = re.findall(self.re_playinfo, dec, re.S)
            INITIAL_STATE = re.findall(self.re_INITIAL_STATE, dec, re.S)
            if playinfo == [] or INITIAL_STATE == []:
                raise Exception("无法找到初始化信息。")
            playinfo = json.loads(playinfo[0])
            INITIAL_STATE = json.loads(INITIAL_STATE[0])
            self.now_interact["session"] = playinfo["session"]
            self.now_interact["bvid"] = INITIAL_STATE["bvid"]
            self.now_interact["cid"] = str(INITIAL_STATE["cidMap"][INITIAL_STATE["bvid"]]["cids"]["1"])
            self.now_interact["vname"] = self.name_replace(INITIAL_STATE["videoData"]["title"])
            return 0, ""
        except Exception as e:
            return 1, str(e)


    # Judge the interactive video.
    def isInteract(self):
        make_API = "https://api.bilibili.com/x/player/v2?cid=" + self.now_interact["cid"] + "&bvid=" + self.now_interact["bvid"]
        try:
            res = requests.get(make_API,headers=self.index_headers,stream=False,proxies=self.Proxy)
            des = json.loads(res.content.decode('utf-8'))
            if "interaction" not in des["data"]:
                raise Exception("非交互视频")
            self.now_interact["graph_version"] = str(des["data"]["interaction"]["graph_version"])
            return 0, ""
        except Exception as e:
            return 1, str(e)


    # Get interactive video pre-information
    def down_list_make(self, cid_num):
        make_API = "https://api.bilibili.com/x/player/playurl?cid=" + cid_num \
                   + "&bvid=" + self.now_interact["bvid"] + "&qn=116&type=&otype=json&fourk=1&fnver=0&fnval=976&session=" + \
                   self.now_interact["session"]
        try:
            des = requests.get(make_API, headers=self.index_headers, stream=False, proxies=self.Proxy)
            playinfo = json.loads(des.content.decode('utf-8'))
        except Exception as e:
            return False, str(e)
        if playinfo != {}:
            re_GET = playinfo
            # List Video Quality Table
            temp_v = {}
            for i in range(len(re_GET["data"]["accept_quality"])):
                temp_v[str(re_GET["data"]["accept_quality"][i])] = str(re_GET["data"]["accept_description"][i])
            # List Video Download Quality
            down_dic = {"video": {}, "audio": {}}
            i = 0
            # Get Video identity information and Initial SegmentBase.
            for dic in re_GET["data"]["dash"]["video"]:
                if str(dic["id"]) in temp_v:
                    qc = temp_v[str(dic["id"])]
                    down_dic["video"][i] = [qc, [dic["baseUrl"]], 'bytes=' + dic["SegmentBase"]["Initialization"]]
                    for a in range(len(dic["backupUrl"])):
                        down_dic["video"][i][1].append(dic["backupUrl"][a])
                    i += 1
                else:
                    continue
            # List Audio Stream
            i = 0
            for dic in re_GET["data"]["dash"]["audio"]:
                au_stream = dic["codecs"] + "  音频带宽：" + str(dic["bandwidth"])
                down_dic["audio"][i] = [au_stream, [dic["baseUrl"]], 'bytes=' + dic["SegmentBase"]["Initialization"]]
                for a in range(len(dic["backupUrl"])):
                    down_dic["audio"][i][1].append(dic["backupUrl"][a])
                i += 1
            # Get Video Length
            length = re_GET["data"]["dash"]["duration"]
            # Return Data
            return True, length, down_dic
        else:
            return False, "Get Download List Error."


    # Get interactive video node list (Use recursion algorithm)
    def recursion_GET_List(self):
        temp = {"choices": {}}
        temp["cid"] = self.now_interact["cid"]
        if self.now_interact["node_id"] == "":
            make_API = "https://api.bilibili.com/x/stein/nodeinfo?bvid=" + self.now_interact["bvid"] + "&graph_version=" + self.now_interact["graph_version"]
        else:
            make_API = "https://api.bilibili.com/x/stein/nodeinfo?bvid=" + self.now_interact["bvid"] + "&graph_version=" + self.now_interact["graph_version"] + "&node_id=" + self.now_interact["node_id"]
        des = requests.get(make_API, headers=self.index_headers, stream=False, proxies=self.Proxy)
        desp = json.loads(des.content.decode('utf-8'))
        if "edges" not in desp["data"]:
            return temp
        for ch in desp["data"]["edges"]["choices"]:
            self.now_interact["cid"] = str(ch["cid"])
            self.now_interact["node_id"] = str(ch["node_id"])
            temp["choices"][ch["option"]] = self.recursion_GET_List()
        return temp


    # Interactive video download processor (Use recursion algorithm)
    def recursion_for_Download(self, json_list, output_dir):
        for ch in json_list:
            chn = self.name_replace(ch)
            output = output_dir + "/" + chn
            video_dir = output + "/" + chn + '_video.m4s'
            audio_dir = output + "/" + chn + '_audio.m4s'
            dic_return = self.down_list_make(json_list[ch]["cid"])
            if not dic_return[0]:
                print(dic_return[1])
                return -1
            down_dic = dic_return[2]
            self.second_headers["range"] = down_dic["video"][self.VQuality][2]
            self.d_processor(down_dic["video"][self.VQuality][1], output, video_dir, "下载视频：" + chn)
            self.second_headers['range'] = down_dic["audio"][self.AQuality][2]
            self.d_processor(down_dic["audio"][self.AQuality][1], output, audio_dir, "下载音频：" + chn)
            if self.synthesis:
                print('正在启动ffmpeg......')
                self.ffmpeg_synthesis(video_dir, audio_dir, output + '/' + chn + '.mp4')
            self.recursion_for_Download(json_list[ch]["choices"],output)
        return 0

    ###################################################################
    # 音频进程
    def search_AUPreinfo(self, au_url):
        # check1:音乐歌单页面检测；check2:单个音乐页面检测
        check1 = re.findall(r'/audio/am(\d+)', au_url, re.S)
        check2 = re.findall(r'/audio/au(\d+)', au_url, re.S)
        if check1 != []:
            # print(check1[0])
            temps = self.AuList_Maker(check1[0], 2)
            if temps[0]:
                # print(json.dumps(temps[1]))
                return 1, temps[1]
            else:
                return 0, "Audio List Get Error."
        elif check2 != []:
            # print(check2[0])
            temps = self.AuList_Maker(check2[0], 1)
            if temps[0]:
                # print(json.dumps(temps[1]))
                return 2, temps[1]
            else:
                return 0, "Audio Single Get Error."
        else:
            print("Is NOT Music.")
            return 0, {}

    def AuList_Maker(self, sid, modeNUM):
        list_dict = {"audio": [], "total": 0}
        if modeNUM == 1:
            try:
                makeURL = "https://www.bilibili.com/audio/music-service-c/web/song/info?sid=" + sid
                res = requests.get(makeURL, headers=self.index_headers, stream=False, timeout=10, proxies=self.Proxy)
                des = res.content.decode('utf-8')
                auinfo = json.loads(des)["data"]
                temp = {}
                temp["title"] = auinfo["title"] + "_" + auinfo["author"]
                temp["sid"] = sid
                temp["cover"] = auinfo["cover"]
                temp["duration"] = auinfo["duration"]
                temp["lyric"] = auinfo["lyric"]
                list_dict["audio"].append(temp)
                list_dict["total"] = 1
            except Exception as e:
                print("AuList_Maker_Single:", e)
                return 0, "AuList_Maker_Single:{}".format(e)
            return 1, list_dict
        elif modeNUM == 2:
            try:
                pn = 1
                while True:
                    makeURL = "https://www.bilibili.com/audio/music-service-c/web/song/of-menu?sid=" + sid + "&pn=" + str(
                        pn) + "&ps=30"
                    res = requests.get(makeURL, headers=self.index_headers, stream=False, timeout=10, proxies=self.Proxy)
                    des = res.content.decode('utf-8')
                    mu_dic = json.loads(des)["data"]
                    for sp in mu_dic["data"]:
                        # print(sp)
                        temp = {}
                        temp["title"] = sp["title"] + "_" + sp["author"]
                        temp["sid"] = str(sp["id"])
                        temp["cover"] = sp["cover"]
                        temp["duration"] = sp["duration"]
                        temp["lyric"] = sp["lyric"]
                        list_dict["audio"].append(temp)
                        list_dict["total"] += 1
                    if pn >= mu_dic["pageCount"]:
                        break
                    else:
                        pn += 1
                        continue
            except Exception as e:
                print("AuList_Maker_List:", e)
                return 0, "AuList_Maker_List:{}".format(e)
            return 1, list_dict
        else:
            return 0, "ModeNum Error."

    # 显示音频信息
    def Audio_Show(self):
        au_dic = self.search_AUPreinfo(self.index_url)
        if au_dic[0] == 0:
            print(au_dic[1])
            return 0
        if au_dic[0] == 1:
            print('当前歌单包含音乐数量为{}个'.format(au_dic[1]["total"]))
        elif au_dic[0] == 2:
            print('当前下载歌曲名称为：{}'.format(au_dic[1]["audio"][0]["title"]))
            print('歌曲长度为：{}'.format(au_dic[1]["audio"][0]["duration"]))
        else:
            return 0
        i = 0
        for sp in au_dic[1]["audio"]:
            i += 1
            form_make = "{}-->{}".format(i, sp["title"])
            print(form_make)
        return 1

    # 获取单个音频下载地址
    def Audio_getDownloadList(self, sid):
        make_url = "https://www.bilibili.com/audio/music-service-c/web/url?sid=" + sid
        res = requests.get(make_url, headers=self.index_headers, stream=False, timeout=10, proxies=self.Proxy)
        des = res.content.decode('utf-8')
        au_list = json.loads(des)["data"]["cdns"]
        return au_list

    # 附带资源下载
    def simple_downloader(self, url, output_dir, output_file):
        try:
            res = requests.get(url, headers=self.index_headers, timeout=10, proxies=self.Proxy)
            file = res.content
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            with open(output_file, 'wb') as f:
                f.write(file)
        except Exception as e:
            print("附带下载失败：", e)

    # 音乐下载函数
    def audio_downloader(self):
        self.second_headers["referer"] = "https://www.bilibili.com/"
        self.second_headers["sec-fetch-dest"] = 'audio'
        self.second_headers["sec-fetch-mode"] = 'no-cors'
        self.AQuality = 0
        self.VQuality = 0
        if self.d_list != None:
            d_list = self.args2list()
        else:
            d_list = [1]
        temp_dic = self.search_AUPreinfo(self.index_url)
        if temp_dic[0] == 0:
            print("获取音乐前置信息出错。")
            return 0
        try:
            for index in d_list:
                sp = temp_dic[1]["audio"][index - 1]
                output_dir = self.output + "/" + self.name_replace(sp["title"])
                output_name = output_dir + "/" + self.name_replace(sp["title"])
                print("正在下载音乐：{}".format(sp["title"]))
                if sp["cover"] != "":
                    self.simple_downloader(sp["cover"], output_dir, output_name + "_封面.jpg")
                if sp["lyric"] != "":
                    self.simple_downloader(sp["lyric"], output_dir, output_name + "_歌词.lrc")
                au_downlist = self.Audio_getDownloadList(sp["sid"])
                self.second_headers["range"] = 'bytes=0-'
                self.d_processor(au_downlist, output_dir, output_name + ".mp3", "下载音乐")
            print("音乐下载进程结束！")
            return 1
        except Exception as e:
            print("音频下载出错：", e)
            return 0


if __name__ == '__main__':
    rundownloader = bili_downloader(args)
    if args.check:
        if args.Address is None:
            rundownloader.Audio_Show()
        else:
            rundownloader.show_preDetail()
    elif args.DownList != None and args.Address != None:
        rundownloader.Download_List()
    elif args.interact and args.Address != None:
        rundownloader.requests_start()
    elif args.Address != None:
        rundownloader.Download_single()
    elif args.MAddress != None:
        rundownloader.audio_downloader()
    else:
        pass
