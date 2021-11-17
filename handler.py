#!/usr/bin/env python
#-*- coding:utf8 -*-
# Powered by ZJ 2021-10-15 10:44:04

import web
from manage_msg import Msg_Mgr
from command import Operate


class Index():
    def GET(self):
        return 'Hello Index'

class RecvMsg():
    def GET(self):
        request_info = web.input()
        if not request_info:
            return 'param is null'
        recvmgr = Msg_Mgr()
        recvmgr.set_recvmsg(request_info)
        rs = recvmgr.recvmsg_open()
        return rs

    def POST(self):
        print('in post')
        request_data = web.data()
        request_info = web.input()
        recvmgr = Msg_Mgr()
        recvmgr.set_recvmsg(request_info, request_data)
        web.header('Content-Type', 'text/xml')
        msg = recvmgr.recvmsg_callback()
        return msg

class SendMsg():
    def GET(self):
        request_info = web.input()
        recvmgr = Msg_Mgr()
        rs = recvmgr.send_msg(request_info)
        return ''

class Command():
    def GET(self):
        request_info = web.input()
        com = Operate()
        command_ret = com.operate(request_info)
        return command_ret
