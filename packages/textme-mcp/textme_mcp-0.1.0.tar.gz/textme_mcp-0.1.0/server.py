# -*- coding: utf-8 -*-
from mcp.server.fastmcp import FastMCP
from pydantic import Field
import os
import logging
import httpx
from urllib.parse import quote


async def fetch(url: str, method: str, params: dict=None, data: dict=None, json: dict=None):
    async with httpx.AsyncClient() as client:
        if method == "get":
            response = await client.get(url=url, params=params)
        elif method == "post":
            try:
                response = await client.post(url=url, data=data, json=json)
            except Exception as e:
                return str(e)
        else:
            assert NotImplementedError()
        return response


log_level = os.getenv("LOG_LEVEL", "INFO")


logger = logging.getLogger('mcp')
settings = {
    'log_level': log_level
}
print(log_level)

# 初始化mcp服务
mcp = FastMCP('textme-mcp-server', log_level=log_level, settings=settings)


# 定义工具
@mcp.tool(name='信息发送工具', description="当用户表达发送给我的意图是，可通过本工具将内容发送给用户")
async def bark_notify(title: str, msg: str):
    base_url = os.getenv("TEXTME_BASE_URL")
    token = os.getenv("TEXTME_TOKEN")
    if base_url is None or token is None:
        return "Error, TEXTME_BASE_URL or TEXTME_TOKEN is None"

    data = {
        "title": title,
        "content": msg
    }
    url = f"{base_url}/webhook/{token}"
    print(data)
    response = await fetch(url, "post", json=data)
    return str(response.text)


def run():
    mcp.run(transport='stdio')

if __name__ == '__main__':
   print("running...")
   run()
