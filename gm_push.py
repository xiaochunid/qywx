#!/usr/bin/env python
#-*- coding:utf8 -*-
# Powered by ZJ 2021-10-15 10:45:01

import web
from urls import urls
from handler import *


if __name__ == '__main__':
    app = web.application(urls,globals())
    app.run()
