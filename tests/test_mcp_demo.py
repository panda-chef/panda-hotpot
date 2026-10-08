"""MCP 菜品配套代码的协议测试与打包元信息校验。"""
from __future__ import annotations

import ast
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    tomllib = None  # type: ignore[assignment]

ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = ROOT / "dishes" / "2026-08-mcp-agent-standard" / "code"
sys.path.insert(0, str(ROOT))


def load_module(name: str, path: Path):
    """按文件路径加载模块（目录名含连字符，不能直接 import）。"""
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def defined_functions(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}


class MinServerProtocolTests(unittest.TestCase):
    """server_min.py：零依赖的 JSON-RPC 协议实现。"""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_module("server_min", CODE_DIR / "server_min.py")

    def call(self, payload: dict):
        return self.mod.handle_message(json.dumps(payload))

    def test_initialize_handshake(self):
        reply = self.call({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        self.assertEqual(reply["result"]["protocolVersion"], "2025-03-26")
        self.assertEqual(reply["result"]["serverInfo"]["name"], "panda-chef-min")
        self.assertIn("tools", reply["result"]["capabilities"])

    def test_tools_list_exposes_schemas(self):
        reply = self.call({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}})
        tools = {tool["name"]: tool for tool in reply["result"]["tools"]}
        self.assertEqual(set(tools), {"add", "get_weather"})
        self.assertEqual(tools["add"]["inputSchema"]["required"], ["a", "b"])

    def test_tools_call_add(self):
        reply = self.call(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "add", "arguments": {"a": 2, "b": 3}},
            }
        )
        self.assertEqual(json.loads(reply["result"]["content"][0]["text"]), {"result": 5})
        self.assertEqual(reply["result"]["content"][0]["type"], "text")

    def test_tools_call_unknown_tool(self):
        reply = self.call(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "not_exists", "arguments": {}},
            }
        )
        self.assertIn("error", json.loads(reply["result"]["content"][0]["text"]))

    def test_notification_returns_nothing(self):
        self.assertIsNone(self.call({"jsonrpc": "2.0", "method": "notifications/initialized"}))

    def test_unknown_method_returns_error(self):
        reply = self.call({"jsonrpc": "2.0", "id": 9, "method": "no/such", "params": {}})
        self.assertEqual(reply["error"]["code"], -32601)

    def test_invalid_json_is_ignored(self):
        self.assertIsNone(self.mod.handle_message("{不是 JSON"))

    def test_stdio_end_to_end(self):
        """按 README 里的用法喂一条 stdin 消息，验证真实可跑。"""
        request = json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "add", "arguments": {"a": 2, "b": 3}},
            }
        )
        proc = subprocess.run(
            [sys.executable, str(CODE_DIR / "server_min.py")],
            input=request + "\n",
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        reply = json.loads(proc.stdout.strip())
        self.assertEqual(reply["id"], 1)
        self.assertEqual(
            json.loads(reply["result"]["content"][0]["text"]), {"result": 5}
        )


@unittest.skipIf(tomllib is None, "tomllib 需要 Python 3.11+")
class PackagingTests(unittest.TestCase):
    """配套代码目录是可 pip 安装的，入口点必须真实存在。"""

    def setUp(self):
        self.pyproject = CODE_DIR / "pyproject.toml"
        if not self.pyproject.is_file():
            self.skipTest("code/ 目录还没有 pyproject.toml")

    def test_pyproject_is_valid_pep621(self):
        data = tomllib.loads(self.pyproject.read_text(encoding="utf-8"))
        project = data["project"]
        self.assertEqual(project["name"], "panda-mcp-demo")
        self.assertEqual(project["license"], "MIT")
        self.assertIn("mcp", " ".join(project.get("optional-dependencies", {}).get("sdk", [])))

    def test_entry_points_resolve(self):
        data = tomllib.loads(self.pyproject.read_text(encoding="utf-8"))
        entry_points = data["project"]["scripts"]
        self.assertEqual(
            set(entry_points), {"panda-mcp-min", "panda-mcp"}
        )
        for target in entry_points.values():
            module, func = target.split(":")
            path = CODE_DIR / f"{module}.py"
            self.assertTrue(path.is_file(), f"入口点模块不存在: {path}")
            self.assertIn(func, defined_functions(path), f"{path.name} 里没有 {func}()")

    def test_wheel_lists_both_modules(self):
        data = tomllib.loads(self.pyproject.read_text(encoding="utf-8"))
        py_modules = data["tool"]["hatch"]["build"]["targets"]["wheel"]["py-modules"]
        self.assertEqual(set(py_modules), {"server", "server_min"})


if __name__ == "__main__":
    unittest.main()
