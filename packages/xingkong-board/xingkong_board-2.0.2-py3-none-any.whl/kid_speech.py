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

# 语音合成（可选依赖）
from __future__ import annotations
try:
    import pyttsx3
except ImportError:  # pragma: no cover
    pyttsx3 = None

# 语音识别：可选依赖
try:
    import speech_recognition as sr
except ImportError:  # pragma: no cover
    sr = None

# Vosk 离线识别：可选依赖
try:
    from vosk import Model, KaldiRecognizer
    import pyaudio
except ImportError:  # pragma: no cover
    Model = None
    KaldiRecognizer = None


class SpeechIO:
    """简化的语音合成接口。"""

    def __init__(self):
        if pyttsx3 is None:
            print("⚠️ 未安装 pyttsx3，TTS 功能不可用。\n   pip install pyttsx3")
            self.engine = None
            return

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


# ===================== 语音识别 =====================


class SpeechRecognizer:
    """简单的语音识别包装（基于 speech_recognition）。

    使用麦克风进行连续识别，将文本传递给回调函数。依赖 `speech_recognition` 与 `pyaudio`。

    示例：
        >>> from kid_speech import SpeechRecognizer
        >>> rec = SpeechRecognizer(lambda txt: print("识别到:", txt))
        >>> rec.start()
    """

    def __init__(self, callback, phrase_time_limit: int = 5):
        """创建识别器

        Args:
            callback: 识别到文本后的回调函数。形如 `callback(text: str)`
            phrase_time_limit: 单次语音片段最长持续时间（秒）
        """
        self.callback = callback
        self.phrase_time_limit = phrase_time_limit
        self._running = False
        self._thread = None

        if sr is None:
            print("⚠️ 未安装 speech_recognition，语音识别功能不可用。\n"\
                  "   pip install SpeechRecognition pyaudio")

    # ------------------ 公共接口 ------------------

    def start(self):
        """启动识别线程"""
        if sr is None:
            return
        if self._running:
            return
        self._running = True

        import threading

        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """停止识别线程"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)

    # ------------------ 内部 ------------------

    def _listen_loop(self):
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()

        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            print("🎤 语音识别已开启 (按 Ctrl+C 终止)")

        while self._running:
            try:
                with microphone as source:
                    audio = recognizer.listen(source, phrase_time_limit=self.phrase_time_limit)
                try:
                    text = recognizer.recognize_google(audio, language="zh-CN")
                    if text and self.callback:
                        self.callback(text)
                except sr.UnknownValueError:
                    # 未识别到语音
                    continue
                except sr.RequestError as e:
                    print(f"⚠️ 语音识别服务错误: {e}")
            except Exception as e:
                print(f"⚠️ 语音识别线程异常: {e}")
                continue


# ===================== 离线语音识别（Vosk） =====================


class OfflineSpeechRecognizer:
    """离线语音识别包装（基于 Vosk）。

    依赖：vosk、pyaudio
    模型：默认在 `models/vosk-<lang>` 目录加载，可自行指定 `model_path`。
    官方中文小模型下载：
        https://alphacephei.com/vosk/models  (如 vosk-model-small-cn-0.22)

    示例：
        from kid_speech import OfflineSpeechRecognizer
        rec = OfflineSpeechRecognizer(lambda t: print("离线识别:", t))
        rec.start()
    """

    def __init__(self, callback, model_path: str | None = None, sample_rate: int = 16000):
        self.callback = callback
        self.model_path = model_path
        self.sample_rate = sample_rate
        self._running = False
        self._thread = None

        if Model is None:
            print("⚠️ 未安装 vosk 或 pyaudio，离线语音识别不可用。\n"\
                  "   pip install vosk pyaudio")
            return

        import os, tempfile, zipfile, shutil

        # 若未指定模型路径，或路径不存在，则尝试使用打包在 xingkong_board_data 内的模型 zip
        if model_path is None or not os.path.exists(model_path):
            try:
                from xingkong_board_data import get_vosk_model_zip  # type: ignore
                internal_zip = get_vosk_model_zip()
                if os.path.isfile(internal_zip):
                    self.model_path = internal_zip
            except Exception:
                # 资源包可能不存在
                pass

        model_path = self.model_path

        actual_path = model_path

        # 若给的是 zip 文件，则先解压到临时缓存
        if os.path.isfile(model_path) and model_path.lower().endswith(".zip"):
            cache_dir = os.path.join(tempfile.gettempdir(), "vosk_cached_model")
            if not os.path.isdir(cache_dir):
                print("⏳ 正在首次解压 Vosk 模型，请稍候...")
                try:
                    with zipfile.ZipFile(model_path, 'r') as zf:
                        zf.extractall(cache_dir)
                except Exception as e:
                    print(f"⚠️ 模型解压失败: {e}")
            # 取解压后的第一个子目录作为模型根
            subdirs = [os.path.join(cache_dir, d) for d in os.listdir(cache_dir)]
            subdirs = [d for d in subdirs if os.path.isdir(d)]
            if subdirs:
                actual_path = subdirs[0]

        try:
            self.model = Model(actual_path)
        except Exception as e:
            print(f"⚠️ 无法加载 Vosk 模型: {e}\n"\
                  f"   请确认模型目录或 zip 文件有效: {actual_path}")
            self.model = None

    # ------------------ 公共接口 ------------------

    def start(self):
        if Model is None or self.model is None:
            return
        if self._running:
            return
        self._running = True

        import threading
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)

    # ------------------ 内部 ------------------

    def _listen_loop(self):
        recognizer = KaldiRecognizer(self.model, self.sample_rate)

        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16, channels=1, rate=self.sample_rate,
                        input=True, frames_per_buffer=4000)
        stream.start_stream()

        print("🎤 离线语音识别已开启 (Ctrl+C 终止)")

        import json as _json

        while self._running:
            try:
                data = stream.read(4000, exception_on_overflow=False)
                if recognizer.AcceptWaveform(data):
                    res = _json.loads(recognizer.Result())
                    text = res.get("text", "").strip()
                    if text and self.callback:
                        self.callback(text)
            except Exception as e:
                print(f"⚠️ 离线语音识别异常: {e}")
                continue

        stream.stop_stream()
        stream.close()
        pa.terminate() 