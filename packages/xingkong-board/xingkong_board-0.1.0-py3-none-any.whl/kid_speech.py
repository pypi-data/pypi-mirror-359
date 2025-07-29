"""kid_speech.py
================
SpeechIO：简单的语音合成（TTS）封装。

依赖：
    pip install pyttsx3

示例：
    from kid_speech import SpeechIO
    speech = SpeechIO()
    speech.speak("你好")
"""

from __future__ import annotations
import pyttsx3


class SpeechIO:
    """简化的语音合成接口。"""

    def __init__(self):
        try:
            self.engine = pyttsx3.init()
            # 设置中文语音
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if "chinese" in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
            # 设置语速
            self.engine.setProperty('rate', 150)
        except Exception as e:
            print(f"⚠️ 语音合成初始化失败: {e}")
            self.engine = None

    def speak(self, text: str):
        """朗读文字。"""
        if not self.engine:
            print("⚠️ 语音合成不可用")
            return
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"⚠️ 语音合成失败: {e}")

    def close(self):
        """关闭资源。"""
        if self.engine:
            self.engine.stop()
        self.engine = None

    def __del__(self):
        self.close() 