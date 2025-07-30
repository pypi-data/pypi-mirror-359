#!/usr/bin/env python3
"""
测试business-bi-mcp包的基本功能
用于验证安装和导入是否正常
"""

import sys
import traceback
from pathlib import Path


def test_imports():
    """测试所有核心模块的导入"""
    print("📦 测试模块导入...")
    
    modules_to_test = [
        ("core.models", "基础数据模型"),
        ("core.server", "MCP服务器"),
        ("tools", "工具模块"),
        ("templates.problems", "问题模板"),
    ]
    
    failed_imports = []
    
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"   ✅ {module_name} ({description})")
        except ImportError as e:
            print(f"   ❌ {module_name} ({description}) - {e}")
            failed_imports.append((module_name, str(e)))
        except Exception as e:
            print(f"   ⚠️  {module_name} ({description}) - 其他错误: {e}")
            failed_imports.append((module_name, str(e)))
    
    return failed_imports


def test_tools_loading():
    """测试工具加载"""
    print("\n🔧 测试工具加载...")
    
    try:
        from tools import (
            business_problem_analyzer,
            question_guide,
            kpi_identifier,
            analysis_method_recommender,
            chart_type_advisor,
            simple_analysis_planner,
            data_collection_guide,
            result_interpreter,
            insight_generator,
            action_recommender,
            follow_up_questions,
            data_story_builder
        )
        
        tools = [
            (business_problem_analyzer, "业务问题分析器"),
            (question_guide, "问题引导助手"),
            (kpi_identifier, "KPI识别器"),
            (analysis_method_recommender, "分析方法推荐器"),
            (chart_type_advisor, "图表类型顾问"),
            (simple_analysis_planner, "简化分析规划器"),
            (data_collection_guide, "数据收集指南"),
            (result_interpreter, "结果解释器"),
            (insight_generator, "洞察生成器"),
            (action_recommender, "行动建议器"),
            (follow_up_questions, "后续问题生成器"),
            (data_story_builder, "数据故事构建器")
        ]
        
        for tool_func, name in tools:
            if callable(tool_func):
                print(f"   ✅ {name}")
            else:
                print(f"   ❌ {name} - 不是可调用对象")
                return False
        
        print(f"   📊 总共加载了 {len(tools)} 个工具")
        return True
        
    except ImportError as e:
        print(f"   ❌ 工具导入失败: {e}")
        return False
    except Exception as e:
        print(f"   ⚠️  工具加载异常: {e}")
        traceback.print_exc()
        return False


def test_server_creation():
    """测试MCP服务器创建"""
    print("\n🖥️  测试MCP服务器创建...")
    
    try:
        from core.server import create_server
        
        # 尝试创建服务器实例
        server = create_server()
        
        if server is not None:
            print("   ✅ MCP服务器创建成功")
            
            # 检查工具注册
            if hasattr(server, '_handlers') or hasattr(server, 'tools'):
                print("   ✅ 服务器工具注册正常")
            
            return True
        else:
            print("   ❌ MCP服务器创建失败")
            return False
            
    except Exception as e:
        print(f"   ❌ 服务器创建异常: {e}")
        traceback.print_exc()
        return False


def test_data_models():
    """测试数据模型"""
    print("\n📋 测试数据模型...")
    
    try:
        from core.models import (
            BaseResponse,
            BusinessInsight,
            AnalysisMethod,
            ChartRecommendation,
            ActionItem
        )
        
        # 测试基础响应模型
        response = BaseResponse(
            success=True,
            message="测试成功",
            data={"test": "data"}
        )
        print("   ✅ BaseResponse 模型")
        
        # 测试业务洞察模型
        insight = BusinessInsight(
            title="测试洞察",
            description="这是一个测试洞察",
            category="test",
            impact_level="high"
        )
        print("   ✅ BusinessInsight 模型")
        
        print("   📊 数据模型验证通过")
        return True
        
    except Exception as e:
        print(f"   ❌ 数据模型测试失败: {e}")
        traceback.print_exc()
        return False


def test_command_line_entry():
    """测试命令行入口"""
    print("\n⌨️  测试命令行入口...")
    
    try:
        import main
        
        if hasattr(main, 'main') and callable(main.main):
            print("   ✅ main() 函数存在")
        else:
            print("   ❌ main() 函数不存在或不可调用")
            return False
        
        if hasattr(main, 'mcp'):
            print("   ✅ MCP实例已定义")
        else:
            print("   ⚠️  MCP实例未找到（可能需要在main()中创建）")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 命令行入口测试失败: {e}")
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("🧪 Business BI MCP - 包测试工具")
    print("=" * 50)
    
    # 检查当前环境
    print(f"🐍 Python版本: {sys.version}")
    print(f"📁 当前目录: {Path.cwd()}")
    
    # 运行测试
    tests = [
        ("模块导入", test_imports),
        ("工具加载", test_tools_loading),
        ("服务器创建", test_server_creation),
        ("数据模型", test_data_models),
        ("命令行入口", test_command_line_entry),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_name == "模块导入":
                # 对于导入测试，返回失败列表
                failed = test_func()
                success = len(failed) == 0
                if not success:
                    print(f"\n❌ 失败的导入: {len(failed)}")
                    for module, error in failed:
                        print(f"   - {module}: {error}")
            else:
                success = test_func()
            
            results.append((test_name, success))
            
        except Exception as e:
            print(f"❌ 测试 '{test_name}' 执行失败: {e}")
            traceback.print_exc()
            results.append((test_name, False))
    
    # 总结
    print(f"\n{'='*50}")
    print("📊 测试结果总结:")
    
    passed = 0
    failed = 0
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"   {test_name}: {status}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📈 统计: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有测试通过！包已准备好发布。")
        return 0
    else:
        print("⚠️  存在测试失败，请修复后再发布。")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 