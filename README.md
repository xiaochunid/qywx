# qywx
企业微信二次开发
# 使用web.py构建的服务实现通过自建应用来执行内网的任意操作，并根据不同结果给予调用者信息反馈~
#### 启动服务
```
root@saier-zj-online-game-192:~/zj/gm_tools# ./restart.sh 
restart done! 
```
#### 执行方式
![图片](https://user-images.githubusercontent.com/32502063/142201341-278d7070-e0c6-4ec9-a12d-7fa35ba31bc4.png)

#### 执行的具体操作可以在command模块中定义
```
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
```
