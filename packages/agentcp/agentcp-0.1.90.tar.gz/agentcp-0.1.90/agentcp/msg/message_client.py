# -*- coding: utf-8 -*-
# Copyright 2025 AgentUnion Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import queue
import ssl
import threading
import time

# from wss_binary_message import *
import websocket

from agentcp.base.auth_client import AuthClient
from agentcp.base.client import IClient
from agentcp.base.log import log_debug, log_error, log_exception, log_info

from ..context import ErrorContext, exceptions


class MessageClient(IClient):
    def __init__(
        self, agent_id: str, server_url: str, aid_path: str, seed_password: str, cache_auth_client: AuthClient
    ):
        self.agent_id = agent_id
        self.server_url = server_url
        self.agent_id = agent_id
        self.server_url = server_url
        if cache_auth_client == None:
            self.auth_client = AuthClient(agent_id, server_url, aid_path, seed_password)  # 使用AuthClient
        else:
            self.auth_client = cache_auth_client
        self.lock = threading.Lock()
        self.ws = None
        self.connected_event = threading.Event()
        self.queue = queue.Queue(maxsize=30)
        self.is_retrying = False
        self.message_handler = None

    def initialize(self):
        self.auth_client.sign_in()

    def sign_in(self) -> bool:
        return self.auth_client.sign_in() is not None

    def get_headers(self) -> dict:
        return {"User-Agent": f"AgentCP/{__import__('agentcp').__version__} (AuthClient; {self.agent_id})"}

    def sign_out(self):
        self.auth_client.sign_out()

    def set_message_handler(self, message_handler):
        """设置消息处理器"""
        self.message_handler = message_handler

    def start_websocket_client(self):
        if self.connected_event.is_set():
            return True

        # 确保URL格式正确
        ws_url = self.server_url.rstrip("/")  # 移除末尾斜杠
        ws_url = ws_url.replace("https://", "wss://").replace("http://", "ws://")
        ws_url = ws_url + f"/session?agent_id={self.agent_id}&signature={self.auth_client.signature}"

        log_debug(f"message Connecting to WebSocket URL: {ws_url}")  # 调试日志
        self.ws_url = ws_url
        self.ws_thread = threading.Thread(target=self.__ws_handler, daemon=True)
        self.ws_thread.start()
        wait = 0
        while not self.connected_event.is_set() and wait < 5:
            log_debug("WebSocket client is reconnect...")
            time.sleep(0.01)
            wait += 0.01
        return self.connected_event.is_set()

    def stop_websocket_client(self):
        if self.ws:
            self.ws.close()
        self.ws_thread = None
        self.ws = None
        self.ws_thread = None

    def send_msg(self, msg):
        retry_count = 0
        while not self.ws or not self.connected_event.is_set():
            self.start_websocket_client()
            log_debug("WebSocket client is not connected, trying to reconnect...")
            time.sleep(0.01)  # 等待1秒后重试连接
            if retry_count > 5 or self.connected_event.is_set():
                break
            retry_count += 1

        if not self.ws:
            return

        if not self.connected_event.is_set():
            log_error("WebSocket client is not connected, cannot send message. after 5 retry")
            if self.queue.full():
                self.queue.get()
                self.queue.task_done()

            self.queue.put(msg, timeout=1)
            return False

        try:
            if not isinstance(msg, str):
                msg = json.dumps(msg)
            self.ws.send(msg)
            log_info("send message success")
            return True
        except Exception as e:
            log_exception(f"send message: {msg}")
            trace_id = msg.get("trace_id", "") if isinstance(msg, dict) else ""
            ErrorContext.publish(exceptions.SendMsgError(message=f"Error send message: {e}", trace_id=trace_id))

    def on_error(self, ws, error):
        if self.is_retrying:
            return
        self.is_retrying = True
        ErrorContext.publish(exceptions.SDKError(f"websocket connection to remote host was lost: {self.ws_url}"))
        """连接发生错误时的处理函数"""
        log_error(f"连接错误: {error}")
        if "Connection to remote host was lost" == error:
            # todo 周一确认
            log_error("Connection to remote host was lost")
            self.is_retrying = False
            return
        # 增加断线重连逻辑
        retry_count = 0
        self.connected_event.clear()
        while retry_count < 1:  # 最多重试3次
            try:
                log_info(f"尝试重新连接，第 {retry_count + 1} 次")
                self.sign_in()
                self.start_websocket_client()
                if self.connected_event.is_set():
                    log_info("重新连接成功")
                    self.is_retrying = False
                    break
            except Exception as e:
                log_exception(f"重新连接失败: {e}")
            retry_count += 1
            time.sleep(4)  # 等待2秒后重试
        if retry_count >= 1:
            self.is_retrying
            log_error("重试次数已达上限，放弃重新连接")

    def on_close(self, ws, close_status_code, close_msg):
        """连接关闭时的处理函数"""
        log_info("WebSocket 连接已关闭")
        self.connected_event.clear()

    def on_open(self, ws):
        self.is_retrying = False
        self.connected_event.set()
        try:
            if self.message_handler and hasattr(self.message_handler, "on_open"):
                self.message_handler.on_open(ws)
            while True and not self.queue.empty():
                item = self.queue.get()
                if item is None:
                    break
                self.ws.send(item)
                self.queue.task_done()  # ✅ 处理完一个，立刻告诉队列
        except Exception:
            # 建立连接重发之前失败放在队列里的消息，错误可以忽略
            pass

    def on_ping(self, ws, message):
        """心跳检测函数"""
        log_debug(f"WebSocket received a ping message: {message}")
        self.connected_event.set()
        self.ws.sock.pong(message)  # 回复心跳消息

    def on_pong(self, ws, message):
        """心跳检测函数"""
        log_debug(f"WebSocket received a pong message: {message}")
        self.connected_event.set()

    def on_message(self, ws, message):
        try:
            """接收到消息时的处理函数"""
            log_info(f"WebSocket 连接已建立，收到消息: {message}")  # 打印消息到控制台，方便调试和监视
            self.connected_event.set()
            # 调用消息处理器的 on_message 方法
            if self.message_handler and hasattr(self.message_handler, "on_message"):
                self.message_handler.on_message(ws, message)
            else:
                log_error("Message handler does not have an on_message method.")
        except Exception as e:
            log_exception(f"Error processing message: {e}")
            ErrorContext.publish(
                exceptions.SDKError(message=f"Error processing message: {e}", trace_id=message.get("trace_id"))
            )

    # def on_message(self, ws,message):
    #     self.message_handler.on_message(ws, message)

    def __ws_handler(self):
        """
        WebSocket客户端定时发送消息函数
        :param url: WebSocket服务器URL（ws://或wss://开头）
        :param message: 要定时发送的消息内容
        :param interval: 发送间隔时间（秒），默认5秒
        """

        # 创建 WebSocket 客户端实例
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_ping=self.on_ping,
            on_pong=self.on_pong,
        )
        self.connected_event.clear()
        # 启动WebSocket连接（阻塞当前线程）
        self.ws.run_forever(
            ping_interval=5,
            sslopt={
                "cert_reqs": ssl.CERT_NONE,  # 禁用证书验证
                "check_hostname": False,  # 忽略主机名不匹配
            },
        )
