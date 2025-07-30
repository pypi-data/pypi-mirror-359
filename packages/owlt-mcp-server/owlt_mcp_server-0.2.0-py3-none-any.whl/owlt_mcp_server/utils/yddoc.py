
# -*- coding: utf-8 -*-
import sys
import uuid
import requests
import base64
import hashlib
import time
from importlib import reload
import json
import os
reload(sys)
#sys.setdefaultencoding('utf-8')

YOUDAO_URL_UPLOAD = 'https://openapi.youdao.com/file_trans/upload'
YOUDAO_URL_QUERY = 'https://openapi.youdao.com/file_trans/query'
YOUDAO_URL_DOWNLOAD = 'https://openapi.youdao.com/file_trans/download'
#APP_KEY = '24852101c39ccbd8'



file_path = os.path.join(os.path.dirname(__file__), '..', 'myjson.json')
file_path = os.path.abspath(file_path)
with open(file_path, 'r') as f:
    config = json.load(f)

def truncate(q):
    if q is None:
        return None
    #print("***" + q)
    print(type(q))
    #q_utf8 = q.decode("utf-8")
    q_utf8 = q
    size = len(q_utf8)
    return q_utf8 if size <= 20 else q_utf8[0:10] + str(size) + q_utf8[size - 10:size]


def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()


def do_request(url, data):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    return requests.post(url, data=data, headers=headers)


def upload(filepath: str, langFrom: str, langTo: str):
    max_size = 2 * 1024 * 1024  # 2MB
    file_size = os.path.getsize(filepath)
    if file_size > max_size:
        print("文件太大，超过2MB限制")
        return "103"  # api error code
    
    f = open(filepath, 'rb')  # 二进制方式打开文件
    q = base64.b64encode(f.read())  # 读取文件内容，转换为base64编码
    q = q.decode("utf-8")
    f.close()
    salt = str(uuid.uuid1())
    curtime = str(int(time.time()))
    signStr = config['yddoc_app_key'] + truncate(q) + salt + curtime + config['yddoc_app_secret']
    sign = encrypt(signStr)

    data = {}
    data['q'] = q
    basename = os.path.basename(filepath)
    file_ext = os.path.splitext(basename)[1]
    file_ext = file_ext.lstrip('.')
    data['fileName'] = basename
    data['fileType'] = file_ext
    data['langFrom'] = langFrom #'zh-CHS'
    data['langTo'] = langTo
    data['appKey'] = config['yddoc_app_key']
    data['salt'] = salt
    data['curtime'] = curtime
    data['sign'] = sign
    data['docType'] = 'json'
    data['signType'] = 'v3'

    response = do_request(YOUDAO_URL_UPLOAD, data)
    content_str = response.content.decode('utf-8')
    print(content_str)
    res = json.loads(content_str)
    if res["errorCode"] == "0":
        return res["flownumber"]
    else:   
        return res["errorCode"]


def query(flownumber):
    print("query begin")
    #flownumber = '文件流水号'
    salt = str(uuid.uuid1())
    curtime = str(int(time.time()))
    signStr = config['yddoc_app_key'] + truncate(flownumber) + salt + curtime + config['yddoc_app_secret']
    sign = encrypt(signStr)

    data = {}
    data['flownumber'] = flownumber
    data['appKey'] = config['yddoc_app_key']
    data['salt'] = salt
    data['curtime'] = curtime
    data['sign'] = sign
    data['docType'] = 'json'
    data['signType'] = 'v3'

    response = do_request(YOUDAO_URL_QUERY, data)
    content_str = response.content.decode('utf-8')
    print(content_str)
    res = json.loads(content_str)
    return res["status"]


def download(flownumber):
    #flownumber = '文件流水号'
    salt = str(uuid.uuid1())
    curtime = str(int(time.time()))
    signStr = config['yddoc_app_key'] + truncate(flownumber) + salt + curtime + config['yddoc_app_secret']
    sign = encrypt(signStr)

    data = {}
    data['flownumber'] = flownumber
    data['downloadFileType'] = 'pdf'
    data['appKey'] = config['yddoc_app_key']
    data['salt'] = salt
    data['curtime'] = curtime
    data['sign'] = sign
    data['docType'] = 'json'
    data['signType'] = 'v3'

    response = do_request(YOUDAO_URL_DOWNLOAD, data)
    
    content_type = response.headers.get('Content-Type', '')
    if 'application/json' in content_type:
        # 下载失败，返回 JSON 信息
        try:
            #return response.json()
            json.dumps(response.json())
        except ValueError:
            return "Invalid JSON response"
    else:
        # 下载成功，返回文件流
        pdf_bytes = response.content
        #print(type(response), ",", response)
        #content_str = response.content.decode('utf-8')
        with open('result_translate.pdf', 'wb') as f:
            f.write(pdf_bytes)
            full_path = os.path.abspath(f.name)
        return "translate document done," + full_path

def download_with_retry(flownumber, interval=2, retries=15):
    res = "download timeout after retry."
    for attempt in range(1, retries + 1):
        status = query(flownumber)
        print(f"第 {attempt} 次查询结果: {status}")
        if status == 4:
            res = download(flownumber)
            break
        if attempt < retries:
            time.sleep(interval)

    return res
    
def yddoc_process(filepath: str, langFrom: str, langTo: str):
    if langFrom == "zh":
        langFrom = "zh-CHS"
    if langTo == "zh":
        langTo = "zh-CHS"
        
    flowno = upload(filepath, langFrom, langTo)
    #print("flowno:" + flowno)
   
    #flowno = "63BA54F960CD4009A33B85A3A2399DDD"
    return download_with_retry(flowno)   
        
       