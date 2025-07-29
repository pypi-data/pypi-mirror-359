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
from typing import Optional, Dict, Any, Callable

from kid_serial import SerialIO
from kid_speech import SpeechIO


class XingKongController:
    """行空板控制器 - JSON版本"""
    
    def __init__(self, port: str = "COM5"):
        # 通信组件
        self.serial = SerialIO(port, baudrate=9600)
        
        # 语音合成
        self.speech = SpeechIO()
        
        # 控制状态
        self.running = False
        self.receive_thread = None
        
        # 回调函数
        self._gesture_handler = None
        self._speech_handler = None
        self._sensor_handler = None
        self._raw_handler = None
    
    def send(self, device: str, value: str) -> bool:
        """发送控制命令
        
        Args:
            device: 设备名称 (LED/FAN/BUZZER等)
            value: 设备状态 (ON/OFF等)
        """
        try:
            msg = json.dumps({"message": f"{device}:{value}"}) + "\n"
            self.serial.send(msg)
            # 如果是TTS命令，使用本地语音合成
            if device == "TTS":
                self.speech.speak(value)
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
                        msg = json.loads(data)
                        content = msg.get("message", "")
                        
                        # 处理不同类型的消息
                        if "GESTURE:" in content:
                            gesture = content.split(":")[1]
                            if self._gesture_handler:
                                self._gesture_handler(gesture, "")
                        
                        elif "SPEECH:" in content:
                            text = content.split(":")[1]
                            if self._speech_handler:
                                self._speech_handler(text)
                        
                        elif any(key in content for key in ["TEMP:", "HUMI:", "LIGHT:"]):
                            # 解析传感器数据
                            sensor_data = {}
                            for pair in content.split("|"):
                                if ":" in pair:
                                    key, value = pair.split(":")
                                    try:
                                        sensor_data[key.lower()] = float(value)
                                    except ValueError:
                                        pass
                            if sensor_data and self._sensor_handler:
                                self._sensor_handler(sensor_data)
                    
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
    
    def stop(self):
        """停止控制器"""
        self.running = False
        if self.receive_thread:
            self.receive_thread.join(timeout=1.0)
        self.serial.close()
        if self.speech:
            self.speech.close()


# 创建全局实例
xingkong = XingKongController() 