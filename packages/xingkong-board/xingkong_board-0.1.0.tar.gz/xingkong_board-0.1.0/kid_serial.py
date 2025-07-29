"""kid_serial.py
================
SerialIO：简单串口通信类，兼容 Python 3.7+（不使用 | Union 运算符）。
"""

from __future__ import annotations

from typing import Optional, Union

import serial


class SerialIO:
    """简化的串口通信封装。"""

    def __init__(self, port: str = "COM3", baudrate: int = 9600, timeout: float = 0):
        """初始化串口

        Args:
            port: 串口号，如 "COM5" 或 "/dev/ttyUSB0"
            baudrate: 波特率
            timeout: 读超时，0 表示非阻塞
        """
        try:
            self.ser: Optional[serial.Serial] = serial.Serial(port, baudrate, timeout=timeout)
            print(f"串口已连接: {port} @ {baudrate}bps")
        except serial.SerialException as e:
            print(f"⚠️ 无法打开串口 {port}: {e}\n串口功能将被禁用。")
            self.ser = None

    def send(self, data: Union[str, bytes]):
        """发送字符串或字节到串口。"""
        if not self.ser:
            return
        if isinstance(data, str):
            data = data.encode()
        self.ser.write(data)

    def receive(self) -> str:
        """读取一行串口数据并返回字符串（非阻塞）。"""
        if not self.ser:
            return ""
        data = self.ser.readline()
        return data.decode(errors="ignore")

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.ser = None
            print("串口已关闭。")

    def __del__(self):
        self.close()