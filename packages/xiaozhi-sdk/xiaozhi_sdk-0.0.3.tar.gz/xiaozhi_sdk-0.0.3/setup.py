import os
import re

from setuptools import find_packages, setup


# 读取版本号
def get_version():
    with open(os.path.join("xiaozhi_sdk", "__init__.py"), "r", encoding="utf-8") as f:
        content = f.read()
        match = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', content, re.M)
        if match:
            return match.group(1)
        raise RuntimeError("Unable to find version string.")


# 收集指定目录下的所有文件
def get_data_files(*directories):
    data_files = []
    for directory in directories:
        if os.path.exists(directory):
            for root, _, files in os.walk(directory):
                for file in files:
                    # 将相对于项目根目录的路径转换为相对于包的路径
                    rel_path = os.path.relpath(os.path.join(root, file), ".")
                    data_files.append(rel_path)
    return data_files


setup(
    name="xiaozhi-sdk",  # 包名
    version=get_version(),  # 版本号
    packages=find_packages(),  # 自动发现包
    package_data={
        "xiaozhi_sdk": ["../" + f for f in get_data_files("file")],  # 包含file目录下的所有文件
    },
    include_package_data=True,  # 使用MANIFEST.in文件包含额外文件
    install_requires=[  # 依赖
        "numpy",
        "websockets",
        "aiohttp",
        "av",
        "opuslib",
        "requests",
        "sounddevice",
        "python-socks",
    ],
    author="dairoot",
    author_email="623815825@qq.com",  # 作者邮箱
    description="一个用于连接和控制小智智能设备的Python SDK，支持实时音频通信、MCP工具集成和设备管理功能。",  # 简短描述
    long_description=open("README.md").read(),  # 详细描述（通常从 README 读取）
    long_description_content_type="text/markdown",  # README 文件格式
    url="https://github.com/dairoot/xiaozhi-sdk",  # 项目主页
    classifiers=[  # 分类元数据
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",  # 支持的 Python 版本
)
