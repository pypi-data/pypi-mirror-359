
# -*- coding: utf-8 -*-
import sys
import uuid
import requests
import hashlib
import time
import json
#from imp import reload
from importlib import reload
import time
from owlt_mcp_server.utils.txtext import abc_download

reload(sys)

YOUDAO_URL = 'https://openapi.youdao.com/api'
APP_KEY = '498c4440cb5c591f'
APP_SECRET = 'X4DzuXNZq1vlvT6jLFO3RZ6j9R7IuEaS'


def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()


def truncate(q):
    if q is None:
        return None
    size = len(q)
    return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]


def do_request(data):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    return requests.post(YOUDAO_URL, data=data, headers=headers)


##中文zh-CHS
def yd_text_translate(text, lang):
    if lang == "zh":
        lang = 'zh-CHS'
    q = text

    data = {}
    data['from'] = 'auto'
    data['to'] = lang
    data['signType'] = 'v3'
    curtime = str(int(time.time()))
    data['curtime'] = curtime
    salt = str(uuid.uuid1())
    signStr = APP_KEY + truncate(q) + salt + curtime + APP_SECRET
    sign = encrypt(signStr)
    data['appKey'] = APP_KEY
    data['q'] = q
    data['salt'] = salt
    data['sign'] = sign
    #data['vocabId'] = "您的用户词表ID"
    data['domain'] = "computers"  # 20250703 add 

    response = do_request(data)
    contentType = response.headers['Content-Type']
    if contentType == "audio/mp3":
        millis = int(round(time.time() * 1000))
        filePath = "合成的音频存储路径" + str(millis) + ".mp3"
        fo = open(filePath, 'wb')
        fo.write(response.content)
        fo.close()
    else:
        #print(response.content)
        json_str = response.content.decode('utf-8')
        mydata = data = json.loads(json_str)
        res_list = (mydata['translation'])
        return ''.join(res_list)

    return ""
    

### abc是混淆名    
def domain_translate(text, target_lang):
    return "T1:" + yd_text_translate(text, target_lang) + "\r\nT2:" +  abc_download(text, target_lang)
    
    
