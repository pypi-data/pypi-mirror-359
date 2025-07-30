from setuptools import setup, find_packages

# 读取 README 作为长描述
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="xingkong-board",
    version="2.0.1",
    author="XingKong Team",
    author_email="xingkong@example.com",
    description="行空板双工通信与本地视觉控制库 - 支持手势识别、语音控制和传感器数据处理",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xingkong/xingkong-board",
    python_requires=">=3.7",
    install_requires=[
        "pyserial>=3.5",
        "opencv-python>=4.7.0",
        "mediapipe>=0.10.0",
        "pyttsx3>=2.90",
        "vosk>=0.3.45",
        "pyaudio>=0.2.13",
        "SpeechRecognition>=3.10.0",
    ],
    packages=find_packages(include=("*",)),
    py_modules=[
        "kid_serial", "kid_protocol", "kid_vision", "kid_speech",
        "kid_duplex_controller", "xingkong_board", "quickstart"
    ],
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Developers", 
        "Topic :: Education",
        "Topic :: System :: Hardware",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="xingkong board robot control vision speech gesture hardware education",
    license="MIT",
) 