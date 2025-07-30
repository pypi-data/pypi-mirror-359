from setuptools import setup, find_packages
import os

# 读取README.md文件作为长描述
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    # 包的名称
    name="flutter_widget_mcp_server",
    # 包的版本
    version="0.1.0",
    # 作者信息
    author="anquan9494",
    author_email="anquan9494@gmail.com",
    # 包的简短描述
    description="A Flutter Widget MCP server for AI-enhanced services",
    # 包的详细描述（通常是README.md的内容）
    long_description=long_description,
    long_description_content_type="text/markdown",
    # 项目主页
    # 自动发现和包含所有Python包
    packages=find_packages(),
    # 包的分类信息
    classifiers=[
    ],
    # 指定Python版本要求
    python_requires=">=3.7",
    # 指定依赖包
    install_requires=[
        "fastapi",
        "uvicorn",
        "fastapi-mcp",
        "pydantic",
        "starlette",
        "typing-extensions",
    ],
    # 包含非Python文件
    include_package_data=True,
    # 指定包含的数据文件
    package_data={
        "flutter_widget_mcp_server": ["data/*.json"],
    },
    # 定义命令行入口点
    entry_points={
        "console_scripts": [
            "flutter-widget-mcp-server=flutter_widget_mcp_server.core.main:run",
        ],
    },
)
