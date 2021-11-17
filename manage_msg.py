#!/usr/bin/env python
#-*- coding:utf8 -*-
# Powered by ZJ 2021-10-15 11:05:20

from callback.WXBizMsgCrypt import WXBizMsgCrypt
import xml.etree.cElementTree as ET
import sys
import web
import urllib,urllib2
import requests
import json
import os
import logging
from logging import handlers
from config import *

ACCESS_TOKEN = ""
MSGID_LIST = []

rota_handler = handlers.RotatingFileHandler(
    filename = os.path.join(os.path.abspath(os.path.dirname(__file__)),'log/WXManager.log'),
    maxBytes = 50000000,
    backupCount = 7,
    encoding = 'utf-8'
)
rota_handler.setFormatter(
    logging.Formatter(
        fmt = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S'
    )
)

logprf = logging.Logger(name='自动化系统',level=logging.INFO)
logprf.addHandler(rota_handler)

class Content_Mgr():
    def __init__(self):
        self.touser = ''
        self.msgtype=  ''
        self.content = ''
        self.msg_data = {}
        self.msgid_list = []

    def set_touser(self,touser):
        self.touser = touser
    def set_msgtype(self,msgtype):
        self.msgtype = msgtype
    def set_content(self,content):
        self.content = content
    def set_msg_content(self):
        if not self.msgtype:
            logprf.error("Please set the msgtype")
            sys.exit(1)
        self.msg_data = {
            "touser": self.touser,
            "toparty": PARTY,
            "totag": TAG,
            "msgtype": self.msgtype,
            "agentid": AGENTID,
            self.msgtype: {
                "content": self.content
                },
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 120
            }
        if self.msgtype == "text":
            self.msg_data["safe"] = 0
            self.msg_data["enable_id_trans"] = 0
        return self.msg_data
        
    def get_msg_data(self):
        if not self.msg_data:
            self.set_msg_content()
        return self.msg_data


class Msg_Mgr():

    def __init__(self):
        self.recvmsg = None
        self.pdata = None
        self.order_list_get = None
        self.order_list_post = None
        self.access_token = ACCESS_TOKEN

    def set_recvmsg(self,recvmsg,pdata=None):
        self.recvmsg = recvmsg
        self.pdata = pdata

    def load_access_token(self):
        if self.access_token:
            return self.access_token
        url = ACCESS_TOKEN_URL
        url = url.format(ID=CORPID,SECRET=CORPSECRET)
        str_res = m_request_get(url)
        if not str_res:
            logprf.error("Get Access Token Failed")
            return ''
        str_res = json.loads(str_res)
        if str_res["errcode"] != 0:
            return str_res["errmsg"]
        self.access_token = str_res["access_token"]
        global ACCESS_TOKEN
        ACCESS_TOKEN = self.access_token
        logprf.info("Get Access Token Url: {}, Access Token: {}".format(url,ACCESS_TOKEN))
        return self.access_token
        
    def load_order_list(self):
        if not self.order_list_get:
            self.order_list_get = ORDER_LIST_GET

    def recvmsg_open(self):
        
        #准备参数
        req_msg_signature   = str(urllib.unquote(self.recvmsg['msg_signature']))    # 消息体签名
        req_timestamp       = str(urllib.unquote(self.recvmsg['timestamp']))        # 时间戳
        req_nonce           = str(urllib.unquote(self.recvmsg['nonce']))            # 随机字符串
        req_echostr         = str(urllib.unquote(self.recvmsg['echostr']))          # 加密字符串

        #校验
        token           = TOKEN
        encodingaeskey  = ENCODINGAESKEY
        corpid          = CORPID
        wxcpt=WXBizMsgCrypt(token,encodingaeskey,corpid)
        ret,echostr=wxcpt.VerifyURL(req_msg_signature,req_timestamp,req_nonce,req_echostr)
        if ret != 0:
            logprf.error("VerifyURL Fail! ERR: {}".format(str(ret)))
            sys.exit(1)
        logprf.info("VerifyURL Succeed")
        return echostr

    def recvmsg_callback(self):
        #准备参数
        req_msg_signature   = str(urllib.unquote(self.recvmsg['msg_signature']))    # 息体签名
        req_timestamp       = str(urllib.unquote(self.recvmsg['timestamp']))        # 时间戳
        req_nonce           = str(urllib.unquote(self.recvmsg['nonce']))            # 机字符串
        req_echostr         = str(urllib.unquote(self.pdata))                       # 加密字符串

        #校验,解密
        token           = TOKEN
        encodingaeskey  = ENCODINGAESKEY
        corpid          = CORPID
        wxcpt=WXBizMsgCrypt(token,encodingaeskey,corpid)
        ret,msg = wxcpt.DecryptMsg(req_echostr, req_msg_signature, req_timestamp, req_nonce)
        if ret != 0:
            logprf.error("DecryptMsg Failed ==> ret: {}".foramt(str(ret)))
            return ''
        logprf.info("DecryptMsg Succeed ==> msg: {}".format(msg))
        xml_tree = ET.fromstring(msg)
        content = xml_tree.find("Content").text
        msgid = xml_tree.find("MsgId").text
        content = content.encode("utf-8")
        logprf.info("Recvmsg Callback Info ==> Content: {}, MsgId: {}, MsgidList: {}".format(content,msgid,MSGID_LIST))
        #对比消息队列,判断是否重复
        if msgid in MSGID_LIST:
            logprf.error("Callback Error, msgid: {} is in progress".format(msgid))
            return ''
        else:
            MSGID_LIST.append(msgid)

        #获取指令列表
        self.load_order_list()

        #根据content执行回复以及操作
        if content in self.order_list_get.keys():
            order_info = self.order_list_get[content]
            if content == "-help":
                #order_info = self.order_list_get[content]
                msg = order_info.get("pre_msg")
                self.send_msg(msg)
                return ""
            msg = order_info.get("pre_msg")
            url = order_info.get("url")
            #发送消息
            self.send_msg(msg)
            logprf.info("Recvmsg Callback Exce Url ==> url:{}, msg: {}".format(url,msg))
            response = m_request_get(url)
            if not response:
                logprf.error("url: {} m_request_get get no response".format(url))
                return False
            if response.lower().count("worng") > 0 or response.lower().count("failed") > 0 or response.lower().count("false") > 0:
                msg = order_info.get("error_msg")
                self.send_msg(msg)
                return False
            msg = order_info.get("after_msg")
            self.send_msg(msg)
            #return True
        else:
            self.send_msg("No Such Command!")
        MSGID_LIST.remove(msgid)
        logprf.info("Recvmsg callback Over!")
        return ''


    def send_msg(self,content,touser='@all',msgtype='text'):
        """
        @description:   向企业微信推送消息.POST
        @param:         消息内容，接收者，消息类型
        @return:        response ==> response.text:{"errcode":0,"errmsg":"ok","invaliduser":""}, response.status_code:200
        """
        logprf.info("Send Msg Begin ==> Content: {}, touser: {}, msgtype: {}".format(content,touser,msgtype))

        #获取发送到企业微信的信息
        cm = Content_Mgr()
        cm.set_touser(touser)
        cm.set_msgtype(msgtype)
        if isinstance(content,str):
            cm.set_content(content)
        elif isinstance(content,web.utils.Storage):
            cm.set_content(content["msg"])
        msg_data = cm.get_msg_data()

        #拼接请求地址
        self.load_access_token()
        send_msg_url = SEND_MESSAGE_URL + self.access_token

        #发送消息
        str_result = m_request_post(send_msg_url,msg_data)
        if not str_result:
            return ""
        logprf.info("Send Message Response ==> result: {}".format(str_result.text))

        #判断令牌是否过期
        data_result = json.loads(str_result.text)
        if data_result["errcode"] in WXERROR:
            logprf.info("Access Token Is Expired")
            #重新发起请求
            self.access_token = None
            self.load_access_token()
            send_msg_url = SEND_MESSAGE_URL + self.access_token
            str_result = m_request_post(send_msg_url,msg_data)
            if not str_result:
                logprf.error("Send Msg Twice Failed!")
                return ""
            logprf.info("Second Times Send Msg Response ==> str_result: {}".format(str_result))
            data_result = json.loads(str_result)
        if data_result["errcode"] != 0:
            logprf.error("Send Msg Failed")
            return False
        logprf.info("Send Msg Secceed!")
        return str_result

def m_request_get(url):
    """
    @description:   GET请求
    @param：        url
    @return:        response ==> response.read():str({"errcode":0,"errmsg":"ok","invaliduser":""})
    """
    logprf.info("Send Http Get Request ==> url: {}".format(url))
    if not url:
        return ''
    request = urllib2.Request(url)
    try:
        response = urllib2.urlopen(request)
    except Exception as e:
        logprf.error("Send Http Get Request Failed ==> errmsg: {}".format(e))
        return ''
    result = response.read()
    logprf.info("Send Http Get Request Secceed, Response ==> resp: {}".format(result))
    return result

def m_request_post(url,data=None,auth=None):
    """
    @description:   POST请求
    @param：        url,data,auth
    @return:        response ==> response.text:{"errcode":0,"errmsg":"ok","invaliduser":""}, response.status_code:200
    """
    logprf.info("Send Http Post Request ==> url: {}".format(url))
    if not url:
        return ''
    if data:
        data = json.dumps(data)
    try:
        response = requests.post(url,data=data,auth=auth)
    except Exception as e:
        logprf.error("Send Http Post Request Failed ==> errmsg: {}".format(e))
        return ''
    logprf.info("Send Http Post Request Secceed, Response ==> resp: {}".format(response.text))
    return response
