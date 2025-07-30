#!/usr/bin/env python3
"""
智能BI助手 MCP - 完整启动脚本
基于 FastMCP 2.0 最佳实践

支持多种启动方式：
- STDIO 模式 (默认，适用于 Claude Desktop)
- HTTP 模式 (适用于 Web 客户端)
- 开发模式 (包含 MCP Inspector)

使用方法:
1. STDIO 模式: python start_mcp.py
2. HTTP 模式: python start_mcp.py --http
3. 开发模式: python start_mcp.py --dev
4. 自定义端口: python start_mcp.py --http --port 9000
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

# 确保项目目录在 Python 路径中
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入核心服务器
from core.server import create_mcp_server

# 配置日志系统
def setup_logging(debug: bool = False):
    """设置日志配置"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )
    
    # 控制第三方库日志级别
    logging.getLogger("fastmcp").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)

def print_banner():
    """打印启动横幅"""
    print("=" * 60)
    print("🤖 智能BI助手 MCP 服务器")
    print("📊 基于 FastMCP 2.0 构建")
    print("🔧 提供 7 个核心 BI 分析工具")
    print("=" * 60)

def print_usage_info(transport: str, host: str = "127.0.0.1", port: int = 8000, path: str = "/mcp"):
    """打印使用信息"""
    if transport == "stdio":
        print("\n📡 STDIO 模式启动成功")
        print("🔗 适用于 Claude Desktop 等客户端")
        print("\n📋 Claude Desktop 配置示例:")
        print("```json")
        print('{')
        print('  "mcpServers": {')
        print('    "business-bi-mcp": {')
        print('      "command": "uv",')
        print(f'      "args": ["run", "python", "{Path(__file__).absolute()}"]')
        print('    }')
        print('  }')
        print('}')
        print("```")
    elif transport == "http":
        print(f"\n🌐 HTTP 模式启动成功")
        print(f"📍 服务地址: http://{host}:{port}{path}")
        print(f"🔗 WebSocket 地址: ws://{host}:{port}{path}")
        print("\n📋 客户端连接示例:")
        print("```python")
        print("from fastmcp import Client")
        print(f'client = Client("http://{host}:{port}{path}")')
        print("```")

def run_stdio_mode(debug: bool = False):
    """运行 STDIO 模式"""
    setup_logging(debug)
    print_banner()
    print_usage_info("stdio")
    
    try:
        mcp = create_mcp_server("business_bi_assistant")
        
        # STDIO 是默认传输方式，最适合 Claude Desktop
        mcp.run(transport="stdio")
        
    except KeyboardInterrupt:
        logging.info("✅ 服务器已安全关闭")
    except Exception as e:
        logging.error(f"❌ STDIO 服务器启动失败: {e}")
        sys.exit(1)

def run_http_mode(host: str = "127.0.0.1", port: int = 8000, path: str = "/mcp", debug: bool = False):
    """运行 HTTP 模式"""
    setup_logging(debug)
    print_banner()
    print_usage_info("http", host, port, path)
    
    try:
        mcp = create_mcp_server("business_bi_assistant")
        
        # 使用 Streamable HTTP 传输 (FastMCP 2.0 推荐)
        mcp.run(
            transport="http",
            host=host,
            port=port,
            path=path,
            log_level="debug" if debug else "info"
        )
        
    except KeyboardInterrupt:
        logging.info("✅ 服务器已安全关闭")
    except Exception as e:
        logging.error(f"❌ HTTP 服务器启动失败: {e}")
        sys.exit(1)

def run_dev_mode(port: int = 8000, debug: bool = True):
    """运行开发模式 (包含 MCP Inspector)"""
    setup_logging(debug)
    print_banner()
    print(f"\n🔧 开发模式启动")
    print(f"📍 MCP 服务器: http://127.0.0.1:{port}/mcp")
    print(f"🔍 MCP Inspector: http://localhost:5173")
    print(f"💡 提示: 使用 'fastmcp dev {__file__}' 也可以启动开发模式")
    
    try:
        mcp = create_mcp_server("business_bi_assistant")
        
        # 开发模式使用 HTTP 传输
        mcp.run(
            transport="http",
            host="127.0.0.1",
            port=port,
            path="/mcp",
            log_level="debug"
        )
        
    except KeyboardInterrupt:
        logging.info("✅ 开发服务器已安全关闭")
    except Exception as e:
        logging.error(f"❌ 开发服务器启动失败: {e}")
        sys.exit(1)

def create_argument_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="智能BI助手 MCP 服务器启动脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python start_mcp.py                    # STDIO 模式 (默认)
  python start_mcp.py --http             # HTTP 模式
  python start_mcp.py --dev              # 开发模式
  python start_mcp.py --http --port 9000 # 自定义端口
  python start_mcp.py --stdio --debug    # 调试模式
        """
    )
    
    # 传输模式选项
    transport_group = parser.add_mutually_exclusive_group()
    transport_group.add_argument(
        "--stdio", 
        action="store_true", 
        help="使用 STDIO 传输 (默认，适用于 Claude Desktop)"
    )
    transport_group.add_argument(
        "--http", 
        action="store_true", 
        help="使用 HTTP 传输 (适用于 Web 客户端)"
    )
    transport_group.add_argument(
        "--dev", 
        action="store_true", 
        help="开发模式 (HTTP + 调试日志)"
    )
    
    # HTTP 模式选项
    parser.add_argument(
        "--host", 
        default="127.0.0.1", 
        help="HTTP 服务器主机地址 (默认: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="HTTP 服务器端口 (默认: 8000)"
    )
    parser.add_argument(
        "--path", 
        default="/mcp", 
        help="MCP 服务路径 (默认: /mcp)"
    )
    
    # 调试选项
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="启用调试模式"
    )
    
    return parser

def main():
    """主函数"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # 根据参数选择运行模式
    if args.dev:
        run_dev_mode(port=args.port, debug=True)
    elif args.http:
        run_http_mode(
            host=args.host, 
            port=args.port, 
            path=args.path, 
            debug=args.debug
        )
    else:
        # 默认使用 STDIO 模式
        run_stdio_mode(debug=args.debug)

# FastMCP 最佳实践：使用标准的 __name__ 保护
if __name__ == "__main__":
    main() 