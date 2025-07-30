"""
智能BI助手 MCP - 修复版启动文件
专为业务设计的数据分析助手

这个版本集成了多种解决方案，确保服务器能够正常启动
"""

import warnings
import sys
import socket
from pathlib import Path

# 确保项目目录在Python路径中
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.server import create_mcp_server


def find_available_port(start_port=8000):
    """查找可用端口"""
    for port in range(start_port, start_port + 20):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return None


def run_with_uvicorn_h11(port=9000):
    try:
        import uvicorn
        
        print("🚀 启动智能BI助手 MCP服务器")
        print("📊 服务器提供7个核心BI分析工具")
        print(f"🌐 服务地址: http://127.0.0.1:{port}/mcp/")
        print("=" * 50)
        
        # 创建MCP服务器
        mcp = create_mcp_server("business_bi_assistant")
        http_app = mcp.http_app(path="/mcp")
        
        # 强制使用 h11 而不是 httptools
        uvicorn.run(
            http_app,
            host="0.0.0.0",
            port=port,
            http="h11",  # 这是关键！强制使用 h11 协议
            log_level="info",
            access_log=True
        )
        return True
    except ImportError:
        print("❌ uvicorn 未安装")
        return False
    except Exception as e:
        print(f"❌ uvicorn 启动失败: {e}")
        return False


def run_with_builtin_server(port=8000):
    """使用 FastMCP 内置服务器"""
    try:
        print("🚀 启动智能BI助手 MCP服务器 (内置服务器)")
        print("📊 服务器提供12个核心BI分析工具") 
        print(f"🌐 服务地址: http://127.0.0.1:{port}/mcp/")
        print("🔧 使用 FastMCP 内置服务器")
        print("=" * 50)
        
        # 创建MCP服务器
        mcp = create_mcp_server("business_bi_assistant")
        
        # 使用内置服务器
        mcp.run(
            transport="http",
            host="0.0.0.0",
            port=port,
            path="/mcp"
        )
        return True
    except Exception as e:
        print(f"❌ 内置服务器启动失败: {e}")
        return False




def main():
    """主函数：启动修复版服务器"""
    print("智能BI助手 MCP")
    print("=" * 50)
    
    # 查找可用端口
    available_port = find_available_port(9000)
    if available_port is None:
        print("❌ 无法找到可用端口 (8000-8019)")
        return
    
    print(f"✅ 找到可用端口: {available_port}")

    try:
        run_with_uvicorn_h11(available_port)
        return
    except KeyboardInterrupt:
        print("\n✅ 服务器已安全关闭")
        return
    except Exception as e:
        print(f"❌ 方案失败: {e}")
    
    


if __name__ == "__main__":
    main() 