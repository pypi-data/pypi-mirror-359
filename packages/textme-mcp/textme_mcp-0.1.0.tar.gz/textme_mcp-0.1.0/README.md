## 用途

把生成的内容通过textme的服务推送给用户，textme支持多种渠道的自定义。

## 配置

参考如下

```json
{
  "mcpServers": {
    "textme-mcp-server": {
      "command": "/path/to/uv",
      "args": [
        "--directory",
        "/path/to/mcpserver-textme",
        "run",
        "server.py"
      ],
      "env": {
        "TEXTME_BASE_URL": "https://some-textme-url-here",
        "TEXTME_TOKEN": "some-webhook-token"
      },
      "autoApprove": [
        "信息发送工具"
      ]
    }
  }
}
```