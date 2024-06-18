from threading import Thread

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
# from QA import QA
import time

from . import QA
# -*- coding:utf-8 -*-

from .QA import *


def websocket_thread(wsUrl, body, APPId):
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_open=on_open)
    ws.appid = APPId
    ws.question = body
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


def index(request):
    if request.method == 'POST':
        # 每次提问清空上次的回答
        clearAnswer()
        start()
        input_value = request.POST.get('input_value')
        print(input_value)
        APPId = "00d517ef"
        APISecret = "NGMxOTU4M2Q2Njg4M2Y3N2MwYTA0ZmY4"

        curTime = str(int(time.time()))
        OriginUrl = "wss://chatdoc.xfyun.cn/openapi/chat"
        document_Q_And_A = Document_Q_And_A(APPId, APISecret, curTime, OriginUrl)
        # 构造问题
        document_Q_And_A.add_msg(input_value)
        wsUrl = document_Q_And_A.get_url()
        body = document_Q_And_A.get_body()

        # 启动 WebSocket 线程
        thread = Thread(target=websocket_thread, args=(wsUrl, body, APPId))
        thread.start()

        return render(request, 'index.html')
    return render(request, 'index.html')


def get_result(request):
    print(QA.is_complete)
    return JsonResponse({'result': getAnswer(), 'stop': QA.is_complete})
