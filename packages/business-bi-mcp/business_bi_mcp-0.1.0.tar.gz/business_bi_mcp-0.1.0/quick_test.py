#!/usr/bin/env python3
"""快速测试包导入和构建"""

print("🔍 快速诊断测试")
print("=" * 40)

# 测试包导入
print("\n📦 测试包导入:")
modules = ["core.models", "core.server", "tools", "templates.problems"]

for module in modules:
    try:
        __import__(module)
        print(f"   ✅ {module}")
    except Exception as e:
        print(f"   ❌ {module} - {e}")

# 检查关键文件
print("\n📁 检查关键文件:")
from pathlib import Path

files = [
    "pyproject.toml",
    "main.py", 
    "core/__init__.py",
    "tools/__init__.py"
]

for file in files:
    exists = Path(file).exists()
    print(f"   {'✅' if exists else '❌'} {file}")

print("\n🎯 基础检查完成！")
print("\n💡 如果所有文件都存在且能导入，那么问题已修复")
print("   现在可以尝试运行: python build_and_publish.py") 