#!/usr/bin/env python3
"""
智能BI助手 MCP - STDIO启动脚本
基于 FastMCP 最佳实践

使用方法:
1. 直接运行: python main.py
2. 使用 fastmcp: fastmcp run main.py
3. 使用项目脚本: business-bi-mcp
4. Claude Desktop 配置: 使用 uv run python main.py
"""

import sys
import logging
from pathlib import Path

# 确保项目目录在 Python 路径中
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入核心服务器
from core.server import create_mcp_server

# 配置日志 - 遵循 FastMCP 最佳实践
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 降低 FastMCP 内部日志级别，避免过多输出
logging.getLogger("fastmcp").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

def main():
    """
    主函数：创建并启动 MCP 服务器
    
    遵循 FastMCP 最佳实践：
    - 使用 if __name__ == "__main__": 保护
    - 默认使用 STDIO 传输
    - 提供清晰的服务器信息
    """
    try:
        # 创建 MCP 服务器实例
        mcp = create_mcp_server("business_bi_assistant")
        
        # 启动服务器 - 默认使用 STDIO 传输
        # 这是 Claude Desktop 等客户端的标准连接方式
        mcp.run(transport="stdio")
        
    except KeyboardInterrupt:
        logging.info("✅ 服务器已安全关闭")
    except Exception as e:
        logging.error(f"❌ 服务器启动失败: {e}")
        sys.exit(1)

# FastMCP 最佳实践：使用标准的 __name__ 保护
if __name__ == "__main__":
    main() 