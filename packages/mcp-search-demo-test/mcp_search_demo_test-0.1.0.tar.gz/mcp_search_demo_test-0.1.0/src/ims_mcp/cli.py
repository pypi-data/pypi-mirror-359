#!/usr/bin/env python3
# coding:utf-8

from ims_mcp.mcp_server import create_mcp_server
from dotenv import load_dotenv
import asyncio
import sys


def main():
    """命令行入口点，用于启动 IMS Video Editing MCP 服务器"""
    # 加载环境变量
    load_dotenv()

    try:
        # 创建MCP服务器
        mcp = create_mcp_server()
        asyncio.run(mcp.run())
    except Exception as e:
        print(f"启动服务器时出错: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
