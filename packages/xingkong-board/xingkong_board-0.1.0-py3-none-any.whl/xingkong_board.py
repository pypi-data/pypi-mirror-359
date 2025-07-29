from __future__ import annotations

"""xingkong_board.py
====================
行空板学生 API

封装行空板常用功能，摒弃 "simple" 命名，更直观。

示例：
    from xingkong_board import XingKongBoard

    board = XingKongBoard("COM5")

    @board.on_gesture
    def handle_gesture(gesture, pose):
        if gesture == "one":
            board.send("LED", "ON")
        elif gesture == "five":
            board.send("LED", "OFF")

    board.enable_local_vision()  # 启用本地摄像头手势识别 (可选)
    board.start()
"""

import threading
from typing import Callable, Dict

import cv2

from kid_duplex_controller import xingkong as _default_ctrl, XingKongController
from kid_vision import KidVision


class XingKongBoard:
    """行空板学生友好封装。"""

    # ---------------- 构造 ---------------- #
    def __init__(self, port: str = "COM5", reuse_default: bool = True):
        if reuse_default and _default_ctrl and _default_ctrl.serial and _default_ctrl.serial.ser:
            if port != "COM5":
                print(f"⚠️ 已存在全局行空板实例，忽略端口参数 '{port}'，使用 COM5。")
            self._ctrl = _default_ctrl
        else:
            self._ctrl = XingKongController(port)

        # 视觉相关
        self._vision: KidVision | None = None
        self._vision_thread: threading.Thread | None = None
        self._vision_running = False

    # ---------------- 发送 ---------------- #
    def send(self, device: str, value: str):
        """发送单个设备指令"""
        return self._ctrl.send(device, value)

    def send_multi(self, **devices):
        """同时发送多个指令，如 send_multi(LED="ON", FAN="OFF")"""
        for dev, val in devices.items():
            self.send(dev, str(val))

    # ---------------- 事件注册装饰器 ---------------- #
    def on_gesture(self, func: Callable[[str, str], None]):
        self._ctrl.when_gesture(func)
        return func

    def on_speech(self, func: Callable[[str], None]):
        self._ctrl.when_speech(func)
        return func

    def on_sensor(self, func: Callable[[Dict[str, float]], None]):
        self._ctrl.when_sensor(func)
        return func

    def on_raw(self, func: Callable[[str], None]):
        self._ctrl.when_raw(func)
        return func

    # ---------------- 本地视觉 ---------------- #
    def enable_local_vision(self, camera_id: int = 0):
        """启用本地摄像头手势&姿态识别，自动触发 on_gesture 回调。"""
        if self._vision_running:
            print("⚠️ 本地视觉已在运行")
            return

        self._vision = KidVision()
        self._vision_running = True
        self._vision_thread = threading.Thread(target=self._vision_loop, args=(camera_id,))
        self._vision_thread.daemon = True
        self._vision_thread.start()

    def _vision_loop(self, camera_id: int):
        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            print("⚠️ 无法打开摄像头")
            self._vision_running = False
            return

        prev_gesture = None
        while self._vision_running:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            result = self._vision.recognize(frame)

            # 触发回调
            if result.gesture and result.gesture != prev_gesture:
                prev_gesture = result.gesture
                if self._ctrl._gesture_handler:  # pylint: disable=protected-access
                    self._ctrl._gesture_handler(result.gesture, result.pose or "")

            # 预览窗口
            self._vision._put_text(frame, f"G:{result.gesture}", (10, 20))  # type: ignore
            cv2.imshow("XingKongBoard Vision", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
        self._vision_running = False

    # ---------------- 生命周期 ---------------- #
    def start(self):
        self._ctrl.start()

    def stop(self):
        self._ctrl.stop()
        self._vision_running = False
        if self._vision_thread:
            self._vision_thread.join(timeout=1.0)

    # ---------------- 兼容旧 API ---------------- #
    def forward(self):
        self.send("MOVE", "FWD")

    def back(self):
        self.send("MOVE", "BACK")

    def left(self):
        self.send("MOVE", "LEFT")

    def right(self):
        self.send("MOVE", "RIGHT")

    def stop_move(self):
        self.send("MOVE", "STOP")

    def say(self, text: str):
        self.send("TTS", text) 