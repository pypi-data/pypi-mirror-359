from mcp.server.fastmcp import FastMCP
import urllib.parse

mcp = FastMCP("HelloMCP 中文测试")

@mcp.tool()
def add(a: int, b: int) -> int:
    """加法工具：输入两个整数，返回它们的和"""
    return a + b

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    name = urllib.parse.unquote(name)  # 🔥 解码参数
    return f"你好，{name}！欢迎使用 HelloMCP。"

@mcp.prompt()
def translation_ch(txt: str) -> str:
    """将输入内容翻译成中文"""
    return f"请将以下中文句子翻译成中文：\n\n{txt}"


def main():
    mcp.run(transport='sse')

if __name__ == "__main__":
    main()