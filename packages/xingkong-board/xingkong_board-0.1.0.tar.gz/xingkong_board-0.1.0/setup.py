from setuptools import setup, find_packages

# 读取 README 作为长描述
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="xingkong-board",
    version="0.1.0",
    author="XingKong Team",
    author_email="xingkong@example.com",
    description="行空板双工通信与本地视觉控制库",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xingkong/xingkong-board",
    python_requires=">=3.7",
    install_requires=[
        "pyserial>=3.5",
        "opencv-python>=4.7.0",
        "mediapipe>=0.10.0",
        "pyttsx3>=2.90",
    ],
    packages=find_packages(exclude=("tests",)),
    py_modules=[
        "kid_serial", "kid_protocol", "kid_vision", "kid_speech",
        "kid_duplex_controller", "xingkong_board"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
) 