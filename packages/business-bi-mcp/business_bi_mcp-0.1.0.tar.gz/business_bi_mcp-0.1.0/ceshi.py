#!/usr/bin/env python3
"""
测试服务器创建和工具注册
"""

try:
    print("📦 开始导入core.server模块...")
    from core.server import create_mcp_server
    print("✅ core.server导入成功")
    
    print("🔧 开始创建MCP服务器...")
    mcp = create_mcp_server("test_server")
    print("✅ MCP服务器创建成功")
    
    print("🔍 检查工具注册情况...")
    tools = mcp.list_tools()
    print(f"✅ 已注册 {len(tools)} 个工具")
    
    print("\n📋 工具列表:")
    for i, tool in enumerate(tools, 1):
        print(f"  {i:2d}. {tool}")
    
    print("\n🎉 所有测试通过！智能BI助手MCP已经准备就绪。")
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
except Exception as e:
    print(f"❌ 运行错误: {e}")
    import traceback
    traceback.print_exc() 