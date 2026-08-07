"""
MCP Server 极简演示（纯标准库版）—— 展示 MCP 协议到底在说什么

MCP (Model Context Protocol) 本质是 JSON-RPC 2.0 over stdio：
AI 应用(Host) 通过标准输入输出，和工具服务(Server) 用 JSON 消息通信。

本文件用纯 Python 标准库实现一个最简 MCP Server，暴露两个工具：
  - add(a, b)         加法计算器
  - get_weather(city) 模拟天气查询（真实场景里这里会调天气 API）

运行方式（不装任何依赖）：
  python server_min.py

然后手动喂它一条 JSON-RPC 消息测试：
  echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"add","arguments":{"a":2,"b":3}}}' | python server_min.py

你会看到它返回 {"result": 5} —— 这就是"AI 调用工具"的底层原理。
"""
import json
import sys

TOOLS = [
    {
        "name": "add",
        "description": "计算两个数字的和",
        "inputSchema": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "第一个数"},
                "b": {"type": "number", "description": "第二个数"},
            },
            "required": ["a", "b"],
        },
    },
    {
        "name": "get_weather",
        "description": "查询指定城市的天气（模拟）",
        "inputSchema": {
            "type": "object",
            "properties": {"city": {"type": "string", "description": "城市名"}},
            "required": ["city"],
        },
    },
]


def call_tool(name: str, args: dict):
    """实际执行工具的地方。真实场景里这里会查数据库/调 API。"""
    if name == "add":
        return {"result": args["a"] + args["b"]}
    if name == "get_weather":
        # 真实场景：requests.get(f"https://api.weather.com/{city}")
        return {"city": args["city"], "weather": "晴", "temp_c": 28}
    return {"error": f"未知工具: {name}"}


def handle_message(line: str) -> str | None:
    """处理一条 JSON-RPC 消息，返回需要回复的消息（或 None）。"""
    try:
        msg = json.loads(line)
    except json.JSONDecodeError:
        return None

    method = msg.get("method")
    msg_id = msg.get("id")

    if method == "initialize":
        # 握手：告诉 Host 我是谁、支持什么协议版本
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2025-03-26",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "panda-chef-min", "version": "0.1.0"},
            },
        }
    if method == "notifications/initialized":
        # Host 通知我已初始化完成，无需回复
        return None
    if method == "tools/list":
        # Host 问我有什么工具 → 返回工具清单（AI 就是靠这个"知道"能调用什么）
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}}
    if method == "tools/call":
        # Host 让我执行工具 → 执行并返回结果
        name = msg["params"]["name"]
        args = msg["params"].get("arguments", {})
        result = call_tool(name, args)
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]},
        }
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"不支持的方法: {method}"}}


def main():
    """从 stdin 逐行读取消息并响应（MCP 标准通信方式）。"""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        reply = handle_message(line)
        if reply is not None:
            print(json.dumps(reply, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
