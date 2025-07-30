import os
import json
import time
from mcp.server.fastmcp import FastMCP
from alibabacloud_ice20201109.client import Client as ICE20201109Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_ice20201109 import models as ice20201109_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
import logging
import hashlib

logging.basicConfig(level=logging.INFO)


def create_client() -> ICE20201109Client:
    access_key_id = os.getenv('ALIYUN_ACCESS_KEY_ID')
    access_secret = os.getenv('ALIYUN_ACCESS_KEY_SECRET')
    region = os.getenv('ALIYUN_REGION')

    config = open_api_models.Config(
        access_key_id=access_key_id,
        access_key_secret=access_secret
    )

    config.endpoint = f'ice.{region}.aliyuncs.com'
    return ICE20201109Client(config)


def create_mcp_server():
    # Create an MCP server
    mcp = FastMCP("IMS Media Search MCP")

    ice_client = create_client()

    @mcp.tool()
    def media_search(text: str) -> str:
        """该工具主要是根据输入的搜索词text，搜索相应搜索库中有关的视频信息，并返回相关视频信息列表，包含MediaId和ClipInfo等。

        Args:
            text (string): 搜索词
        """
        result = search_media_by_hybrid(text)
        return result

    def search_media_by_hybrid(text: str) -> str:
        search_media_by_hybrid_request = ice20201109_models.SearchMediaByHybridRequest(
            text=text
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            resp = ice_client.search_media_by_hybrid_with_options(search_media_by_hybrid_request, runtime)
            print(resp.body)
            dict_list = [item.to_map() for item in resp.body.media_list]
            json_str = json.dumps(dict_list, ensure_ascii=False)
            return json_str
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)
        return "media search failed."
