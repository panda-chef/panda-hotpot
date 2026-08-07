# 🔌 MCP 30 分钟上手：代码目录

两道菜配套的可运行代码。看完就能自己写一个 MCP Server 并接入 AI。

## 文件说明

| 文件 | 依赖 | 用途 |
|------|------|------|
| `server_min.py` | 纯标准库 | **协议原理演示**：手写 JSON-RPC 通信，理解 MCP 底层在干什么 |
| `server.py` | `pip install mcp` | **官方 SDK 正式版**：可直接配置进 Claude Code / Codex |

## 快速体验（3 分钟）

```bash
# 1. 跑起极简版 server
python server_min.py

# 2. 另开终端，模拟 AI 应用"问它有什么工具"
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python server_min.py

# 3. 模拟 AI"调用工具"
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"add","arguments":{"a":2,"b":3}}}' | python server_min.py
# → {"jsonrpc":"2.0","id":2,"result":{"content":[{"type":"text","text":"{\"result\": 5}"}]}}
```

看完这三条消息，你就理解了 MCP 的全部核心：**AI 通过标准协议发现工具、调用工具、拿结果**。

## 接入真实 AI 应用（30 分钟）

### 方式一：接入 Claude Code

```bash
# 在项目目录执行（server.py 换成你的绝对路径）
claude mcp add panda-tools -- python D:/your/path/server.py

# 验证
claude mcp list
```

然后让 Claude 做："用 panda-tools 帮我算 12345 × 6789"——它会自动调用 `add` 工具。

### 方式二：接入 Codex CLI

编辑 `~/.codex/config.toml`：

```toml
[mcp_servers.panda-tools]
command = "python"
args = ["D:/your/path/server.py"]
```

### 方式三：自己写一个真正的工具

把 `get_weather` 里的模拟数据换成真实 API 调用：

```python
import urllib.request, json

@mcp.tool()
def get_weather(city: str) -> dict:
    """查询真实天气"""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid=你的KEY"
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read())
```

## 原理图解

```
你的 AI 应用 (Host)              MCP Server (本目录代码)
     │  "你有什么工具？"   ──────▶  tools/list
     │  "我有 add, get_weather" ◀──────┘
     │  "帮我算 2+3"      ──────▶  tools/call {name: add, args: {a:2, b:3}}
     │  "结果是 5"        ◀──────┘
```

这就是"AI 会干活"的底层机制——文章里说的 Agentic 能力，代码层面就是这个协议。
