#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 直接定义依赖，不依赖外部文件
requirements = [
    "pika>=1.2.0",
    "pymysql>=1.0.2",
    "requests>=2.25.1",
    "pyyaml>=6.0",
    "python-dotenv>=0.19.0",
]

# 如果存在requirements.txt文件，则尝试从中读取依赖
if os.path.exists("requirements.txt"):
    try:
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            file_requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
            if file_requirements:
                requirements = file_requirements
    except Exception as e:
        print(f"读取requirements.txt失败，使用默认依赖: {e}")

setup(
    name="grid-async-task",
    version="1.0.3",
    author="grid",
    author_email="grid@example.com",
    description="一个通用的异步任务处理插件，支持RabbitMQ队列监听、任务重试、进度通知等功能",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/shenzhen-grid/grid-async-task-plugin",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "grid-task=grid_async_task.cli:main",
        ],
    },
    package_data={
        "grid_async_task": ["sql/*.sql"],
    },
    include_package_data=True,
) 