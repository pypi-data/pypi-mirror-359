# 提供内部资源定位工具
"""xingkong_board_data 包含随发行版打包的额外数据文件（如 Vosk 中文模型）。

函数:
    get_vosk_model_zip() -> str: 返回模型 zip 文件的绝对路径。
"""
from importlib import resources as _resources
from pathlib import Path

__all__ = ["get_vosk_model_zip"]


def get_vosk_model_zip() -> str:
    """返回打包在内的中文 Vosk 模型 zip 路径"""
    return str(Path(_resources.files(__name__) / "vosk-model-small-cn-0.22.zip")) 