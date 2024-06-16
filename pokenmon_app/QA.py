# -*- coding:utf-8 -*-
import hashlib
import base64
import hmac
import time
import json
import websocket
import _thread as thread
import ssl


class Document_Q_And_A:


    def __init__(self, APPId, APISecret, TimeStamp, OriginUrl):
        self.appId = APPId
        self.apiSecret = APISecret
        self.timeStamp = TimeStamp
        self.originUrl = OriginUrl
        self._messages = []

    @property
    def messages(self):
        """
        问题消息getter

        :return: msgs
        """
        return self._messages

    @messages.setter
    def messages(self, value):
        """
        问题消息setter

        :param value: given msgs
        """
        self._messages = value

    def add_msg(self, content, role="user"):
        """
        构造一个问题消息，并将其加入问题消息列表

        :param content: 问题的内容
        :param role: 提问者的角色。默认为user
        """
        msg = {
            "role": role,
            "content": content
        }
        self._messages.append(msg)

    def get_origin_signature(self):
        m2 = hashlib.md5()
        data = bytes(self.appId + self.timeStamp, encoding="utf-8")
        m2.update(data)
        checkSum = m2.hexdigest()
        return checkSum

    def get_signature(self):
        # 获取原始签名
        signature_origin = self.get_origin_signature()
        # print(signature_origin)
        # 使用加密键加密文本
        signature = hmac.new(self.apiSecret.encode('utf-8'), signature_origin.encode('utf-8'),
                             digestmod=hashlib.sha1).digest()
        # base64密文编码
        signature = base64.b64encode(signature).decode(encoding='utf-8')
        # print(signature)
        return signature

    def get_header(self):
        signature = self.get_signature()
        header = {
            "Content-Type": "application/json",
            "appId": self.appId,
            "timestamp": self.timeStamp,
            "signature": signature
        }
        return header

    def get_url(self):
        signature = self.get_signature()
        header = {
            "appId": self.appId,
            "timestamp": self.timeStamp,
            "signature": signature
        }
        return self.originUrl + "?" + f'appId={self.appId}&timestamp={self.timeStamp}&signature={signature}'
        # 使用urlencode会导致签名乱码
        # return self.originUrl + "?" + urlencode(header)

    def get_body(self):
        """
        获取本次提问的参数信息

        :return: 提问信息
        """
        data = {
            # 非必要
            "chatExtends": {
                "wikiPromptTpl": "请将以下内容作为已知信息：\n<wikicontent>\n请根据以上内容回答用户的问题。\n问题:<wikiquestion>\n回答:",
                "wikiFilterScore": 0.83,
                "temperature": 0.5
            },
            # 必要
            "fileIds": [
                # 语言文件
                "ccde2112088f4a74bf94cacddb43d239",
                # 宝可梦编号、中文名、英文名映射文件
                "1e1962adba814fdf89c4e0d2ae246fa8"
            ],
            "messages": self._messages
        }
        return data


# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)


# 收到websocket关闭的处理
def on_close(ws, close_status_code, close_msg):
    print("### closed ###")
    print("关闭代码：", close_status_code)
    print("关闭原因：", close_msg)


# 收到websocket连接建立的处理
def on_open(ws):
    thread.start_new_thread(run, (ws,))


def run(ws, *args):
    data = json.dumps(ws.question)
    ws.send(data)

answer = []
is_complete = False
# 收到websocket消息的处理
def on_message(ws, message):
    """
    收到websocket消息时的处理。将消息结果塞到ws.message里

    :param ws: websocket连接对象
    :param message: 持续收到的消息
    """
    # print(message)
    global is_complete
    data = json.loads(message)
    code = data['code']
    if code != 0:
        print(f'请求错误: {code}, {data}')
        ws.close()
    else:
        answer.append(data["content"])
        status = data["status"]
        # print(f'status = {status}')
        print(answer, end='')
        # ws.messages.append(content)

        if status == 2:
            ws.close()


def getAnswer():
    return ''.join(answer)

def clearAnswer():
    global answer
    answer = []

