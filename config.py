#!/usr/bin/env python
#-*- coding:utf8 -*-
# Powered by ZJ 2021-10-15 11:48:32

ACCESS_TOKEN_URL = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={ID}&corpsecret={SECRET}"
SEND_MESSAGE_URL = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token="
AGENTID = 1000002   #应用的AgentId,在管理后台里可查
CORPSECRET = "scygiuNjF9qQ1C3DpgfS7n4A4JH48xs-9ITAR6yITw0"  #应用的Secret,在管理后台里可查
CORPID = "ww46a1dc62fdfebaf0"   #你的企业ID,在后台管理-->我的企业中可查
PARTY = "1" # 部门ID
TAG = "666" # 标签ID
TOKEN = "L5SaM7qM5P6CfwqqNTQVbfS7q"     #应用接收消息服务器中生成的Token
ENCODINGAESKEY = "CwbcWqn3C837RKticJdHnpWADvnuftxJTUV0jveBhEx"  #应用接收消息服务器中生成的加密编码
WXERROR = [42001,40014]
ORDER_LIST_GET = {
    "-help": {"pre_msg": "菜单栏: \n-启动251-1\n-关闭251-1"},
    "-启动251-1": {
        "pre_msg": "开始启动 251-1,请勿重复执行",
        "after_msg": "启动251-1 执行完成",
        "error_msg": "启动251-1 失败,请检查",
        "url": "http://192.168.0.83:8889/command?command_id=1"
        },
    "-关闭251-1": {
        "pre_msg": "开始关闭 251-1,请勿重复执行",
        "after_msg": "关闭251-1 执行完成",
        "error_msg": "关闭251-1 失败,请检查",
        "url": "http://192.168.0.83:8889/command?command_id=2"
        }

    }
ORDER_LIST_POST = {
}
COMMAND_LIST_GET = {
    1: {
        'port': 22,
        'user': 'root',
        'host': '192.168.0.251',
        'command': 'cd /data/gameapp/game1 && bash gen_server.sh start'
    },
    2: {
        'port': 22,
        'user': 'root',
        'host': '192.168.0.251',
        'command': 'cd /data/gameapp/game1 && bash gen_server.sh stop'
    }
}
