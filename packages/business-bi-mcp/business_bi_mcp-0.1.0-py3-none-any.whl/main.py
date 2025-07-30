"""
智能BI助手 MCP - 主入口文件
专为业务小白设计的数据分析助手
"""

from core.server import create_mcp_server

# 创建并配置MCP服务器作为全局变量
# 这样MCP CLI工具就能识别到服务器对象
mcp = create_mcp_server("business_bi_assistant")


def main():
    """主函数：启动MCP服务器"""
    # 启动服务器
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()