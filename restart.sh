#!/bin/bash
set -u
pid=`ps -ef | grep gm_push | grep -v grep | awk '{print $2}'`
if [[ -z $pid ]];then
    echo -e '\033[1;32mprocess is not running... \033[0m'
    nohup python ./gm_push.py 8889 &
    echo -e '\033[1;32mstart done! \033[0m'
else
    kill -9 $pid
    nohup python ./gm_push.py 8889 &
    echo -e '\033[1;32mrestart done! \033[0m'
fi
