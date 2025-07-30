"""kid_duplex_controller.py
==========================
行空板双工通信控制器 - JSON版本

为学生提供简单的双向通信框架：
1. 使用JSON格式通信
2. 提供简单的发送和接收接口
3. 支持语音合成功能
"""

from __future__ import annotations

import json
import threading
import time
from typing import Dict, Callable, Optional

from kid_serial import SerialIO
from kid_speech import SpeechIO, SpeechRecognizer, OfflineSpeechRecognizer


class XingKongController:
    """行空板控制器 - JSON版本

    Args:
        port: 串口号
        offline_speech: 是否使用离线语音识别（Vosk）。False 时使用 online SpeechRecognition。
    """
    
    def __init__(self, port: str = "COM5", offline_speech: bool = True):
        # 通信组件
        self.serial = SerialIO(port, baudrate=9600)
        
        # 语音合成 & 识别
        self.speech = SpeechIO()
        # 根据 offline_speech 选择识别器类型
        self.offline_speech = offline_speech
        self._speech_recognizer: Optional[object] = None
        
        # 控制状态
        self.running = False
        self.receive_thread = None
        
        # 回调函数
        self._gesture_handler = None
        self._speech_handler = None
        self._sensor_handler = None
        self._raw_handler = None
    
    # ------------------ 发送 ------------------

    def send(self, device: str, value) -> bool:
        """发送单个设备控制命令 (会自动转为 JSON)。"""
        return self.send_multi(**{device: value})

    def send_multi(self, **devices) -> bool:
        """发送多个设备控制命令，例如::

            xingkong.send_multi(LED="ON", FAN="OFF")
        """
        try:
            msg = json.dumps(devices) + "\n"
            self.serial.send(msg)

            # 本地处理 TTS
            if "TTS" in devices:
                self.speech.speak(str(devices["TTS"]))
            return True
        except Exception as e:
            print(f"发送失败: {e}")
            return False
    
    def when_gesture(self, handler: Callable[[str, str], None]) -> XingKongController:
        """设置手势识别回调
        
        Args:
            handler: 处理函数，接收 (gesture, pose) 参数
        """
        self._gesture_handler = handler
        return self
    
    def when_speech(self, handler: Callable[[str], None]) -> XingKongController:
        """设置语音识别回调
        
        Args:
            handler: 处理函数，接收识别文本
        """
        self._speech_handler = handler
        return self
    
    def when_sensor(self, handler: Callable[[Dict[str, float]], None]) -> XingKongController:
        """设置传感器数据回调
        
        Args:
            handler: 处理函数，接收传感器数据字典
        """
        self._sensor_handler = handler
        return self
    
    def when_raw(self, handler: Callable[[str], None]) -> XingKongController:
        """设置原始数据回调
        
        Args:
            handler: 处理函数，接收原始消息
        """
        self._raw_handler = handler
        return self
    
    def _receive_loop(self):
        """接收数据循环"""
        while self.running:
            try:
                data = self.serial.receive()
                if data:
                    # 处理原始数据
                    if self._raw_handler:
                        self._raw_handler(data)
                    
                    # 尝试解析JSON
                    try:
                        msg = json.loads(data.strip())

                        # ========= 手势 / 姿态 =========
                        if self._gesture_handler and (
                            "GESTURE" in msg or "POSE" in msg):
                            gesture = msg.get("GESTURE") or msg.get("gesture")
                            pose = msg.get("POSE") or msg.get("pose")
                            self._gesture_handler(gesture, pose)
                        
                        # ========= 语音 =========
                        if self._speech_handler and (
                            "SPEECH" in msg or "speech" in msg):
                            text = msg.get("SPEECH") or msg.get("speech")
                            self._speech_handler(text)
                        
                        # ========= 传感器 =========
                        sensor_keys = {k.lower() for k in ["temp", "humi", "light", "dist"]}
                        sensors = {k.lower(): v for k, v in msg.items() if k.lower() in sensor_keys}
                        if sensors and self._sensor_handler:
                            self._sensor_handler(sensors)
                    
                    except json.JSONDecodeError:
                        pass  # 忽略非JSON数据
                    
            except Exception as e:
                print(f"接收数据错误: {e}")
                time.sleep(0.1)
    
    def start(self):
        """启动控制器"""
        if self.running:
            return
        
        print("启动行空板控制器...")
        self.running = True
        
        # 启动接收线程
        self.receive_thread = threading.Thread(target=self._receive_loop)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        # 启动本地语音识别（若已设置 handler 且依赖可用）
        if self._speech_handler:
            try:
                if self.offline_speech and OfflineSpeechRecognizer is not None:
                    # 使用正确的模型路径
                    self._speech_recognizer = OfflineSpeechRecognizer(
                        self._speech_handler, 
                        model_path="models/vosk-model-small-cn-0.22"
                    )
                    self._speech_recognizer.start()
                elif SpeechRecognizer is not None:
                    self._speech_recognizer = SpeechRecognizer(self._speech_handler)
                    self._speech_recognizer.start()
            except Exception as e:
                print(f"⚠️ 无法启动语音识别: {e}")
    
    def stop(self):
        """停止控制器"""
        self.running = False
        if self.receive_thread:
            self.receive_thread.join(timeout=1.0)
        self.serial.close()
        if self.speech:
            self.speech.close()
        if self._speech_recognizer:
            self._speech_recognizer.stop()


# 全局实例（延迟初始化，避免自动打开串口）
xingkong = None

def get_default_controller(port: str = "COM5", **kwargs) -> XingKongController:
    """获取默认控制器实例（单例模式）"""
    global xingkong
    if xingkong is None:
        xingkong = XingKongController(port=port, **kwargs)
    return xingkong 