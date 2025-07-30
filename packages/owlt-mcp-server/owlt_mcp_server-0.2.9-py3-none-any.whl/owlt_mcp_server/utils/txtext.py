# -*- coding: utf-8 -*-

import os
import json
import types
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models

def abc_download(text, target):
    try:
        
        cred = credential.Credential("AKIDKWUN3UgdLq68wVotkmiYDh3ED2g9RYTD", "g9QXTCk5KNG2f8PWSEqxwkNp6C9wqcDc")
        # 使用临时密钥示例
        # cred = credential.Credential("SecretId", "SecretKey", "Token")
        # 实例化一个http选项，可选的，没有特殊需求可以跳过
        httpProfile = HttpProfile()
        httpProfile.endpoint = "tmt.tencentcloudapi.com"

        # 实例化一个client选项，可选的，没有特殊需求可以跳过
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        # 实例化要请求产品的client对象,clientProfile是可选的
        client = tmt_client.TmtClient(cred, "ap-chengdu", clientProfile)

        # 实例化一个请求对象,每个接口都会对应一个request对象
        req = models.TextTranslateRequest()
        params = {
            "SourceText": text,
            "Source": "auto",
            "Target": target,
            "ProjectId": 0,
            "TermRepoIDList": [ "716e4819574c11f0a236f0f8aa23793b" ]
        }
        req.from_json_string(json.dumps(params))

        # 返回的resp是一个TextTranslateResponse的实例，与请求对象对应
        resp = client.TextTranslate(req)
        # 输出json格式的字符串回包
        #print(resp.to_json_string())
        data = json.loads(resp.to_json_string())

        # 获取 TargetText 字段的值
        target_text = data["TargetText"]

    except TencentCloudSDKException as err:
        #print(err)
        target_text = ""
        
    return target_text


#print(abc_download("什么是应用程序接口", "en"))