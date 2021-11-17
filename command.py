#!/usr/bin/env python
#-*- coding:utf8 -*-
# Powered by ZJ 2021-10-29 14:18:11

import subprocess
import sys
import os
import paramiko
import logging
from logging import handlers
from config import *
import warnings
warnings.filterwarnings("ignore")

#定义日志格式
rota_handler = handlers.RotatingFileHandler(
    filename = os.path.join(os.path.abspath(os.path.dirname(__file__)),'log/WXCommand.log'),
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

class Ssh_Excuter:
    """
    定义远程连接实现类
    """
    def __init__(self,user,port,host):
        self.host = host
        self.user = user
        self.port = port

    def execute(self,command):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pkey = paramiko.RSAKey.from_private_key_file('/root/zj/gm_tools/keys/all')
        try:
            logprf.info("Start connect to {}".format(self.host))
            ssh.connect(hostname=self.host,port=self.port,username=self.user,pkey=pkey)
            logprf.info("Connecting to {} success...".format(self.host))
            stdin,stdout,stderr = ssh.exec_command(command)
            status = stdout.channel.recv_exit_status()
            errt = stderr.read().lower()
            result = stdout.read().lower()
            if errt.count("error") > 0 or errt.count("failed") > 0:
                logprf.error("Command {} exec failed ==> ret: {}".format(command,errt))
                return False
            if status != 0:
                logprf.error("Command {} exit code is not 0 ==> ret: {}".format(command,result+'\n'+errt))
                return False
            logprf.info("Command {} exec success ==> ret: \n{}".format(command,result))
            return True
        except Exception as e:
            logprf.error("Command {} in {} exec failed ==> reason: {}".format(command,self.host,e))
            return False
        finally:
            ssh.close()


class Operate:
    """
    定义操作执行类
    """
    def operate(self,request_info):
        command_id = int(request_info["command_id"])
        if command_id not in COMMAND_LIST_GET:
            logprf.error("Command id {} is not found".foramt(command_id))
            return False
        #获取操作对象的连接信息以及指令
        port = COMMAND_LIST_GET[command_id]["port"]
        host = COMMAND_LIST_GET[command_id]["host"]
        user = COMMAND_LIST_GET[command_id]["user"]
        command = COMMAND_LIST_GET[command_id]["command"]
        try:
            logprf.info("Start connect to {} and exec command ==> command: {}".format(host,command))
            SSH = Ssh_Excuter(user,port,host)
            if not SSH.execute(command):
                logprf.error("Command {} exec ==> failed!".format(command))
                return False
            logprf.info("Command {} exec == > succeed!".format(command))
            return True
        except Exception as e:
            logprf.error("Command {} exec over, ret ==> failed! ret: {}".format(command,e))
            return False
