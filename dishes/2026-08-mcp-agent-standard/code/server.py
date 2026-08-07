"""
MCP Server 官方 SDK 版 —— 真正接入 AI 应用用的版本

用官方 Python SDK（pip install mcp）实现，可直接配置到 Claude Code /
Codex / 其他支持 MCP 的 AI 应用中。

安装依赖：
  pip install mcp

运行（standalone 模式测试）：
  python server.py

配置到 Claude Code（mcp.json 或 claude mcp add）：
  claude mcp add panda-tools -- python D:/path/to/server.py

配置到 Codex（~/.codex/config.toml）：
  [mcp_servers.panda-tools]
  command = "python"
  args = ["D:/path/to/server.py"]

然后 AI 就能调用这两个工具了。
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("panda-chef-tools")


@mcp.tool()
def add(a: float, b: float) -> float:
    """计算两个数字的和"""
    return a + b


@mcp.tool()
def get_weather(city: str) -> dict:
    """查询指定城市的天气（模拟数据，真实场景替换为天气 API）"""
    return {"city": city, "weather": "晴", "temp_c": 28}


if __name__ == "__main__":
    mcp.run()
