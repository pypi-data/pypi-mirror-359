#!/usr/bin/env python3
"""
简化版PyPI发布脚本
自动检查.pypirc -> uv build -> uv publish
"""

import os
import sys
import subprocess
import configparser
from pathlib import Path


def run_command(cmd, check=True):
    """运行命令并处理错误"""
    print(f"🔧 执行: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令失败: {e}")
        if e.stderr:
            print(f"错误: {e.stderr}")
        return e
    except Exception as e:
        print(f"❌ 执行异常: {e}")
        return None


def check_uv():
    """检查uv是否可用"""
    result = run_command("uv --version", check=False)
    if not result or result.returncode != 0:
        print("❌ uv不可用，请先安装uv")
        print("安装命令: https://docs.astral.sh/uv/getting-started/installation/")
        return False
    print("✅ uv可用")
    return True


def find_pypirc_token():
    """查找.pypirc文件中的token"""
    print("🔍 查找PyPI配置...")
    
    home_dir = Path.home()
    pypirc_path = home_dir / ".pypirc"
    
    if not pypirc_path.exists():
        print(f"❌ 未找到.pypirc文件: {pypirc_path}")
        return None, None
    
    print(f"✅ 找到.pypirc文件: {pypirc_path}")
    
    try:
        config = configparser.ConfigParser()
        config.read(pypirc_path, encoding='utf-8')
        
        # 查找PyPI token
        pypi_token = None
        testpypi_token = None
        
        if 'pypi' in config:
            pypi_password = config.get('pypi', 'password', fallback=None)
            if pypi_password and pypi_password.startswith('pypi-'):
                pypi_token = pypi_password
                print("✅ 找到PyPI token")
        
        if 'testpypi' in config:
            test_password = config.get('testpypi', 'password', fallback=None)
            if test_password and test_password.startswith('pypi-'):
                testpypi_token = test_password
                print("✅ 找到TestPyPI token")
        
        return pypi_token, testpypi_token
        
    except Exception as e:
        print(f"❌ 读取.pypirc失败: {e}")
        return None, None


def get_user_token():
    """获取用户输入的token"""
    print("\n🔐 请输入PyPI API token:")
    token = input("PyPI token (pypi-开头): ").strip()
    
    if not token.startswith("pypi-"):
        print("❌ token格式错误，应该以'pypi-'开头")
        return None
    
    return token


def uv_build():
    """使用uv构建包"""
    print("\n🏗️ 构建包...")
    result = run_command("uv build", check=False)
    
    if result and result.returncode == 0:
        print("✅ 构建成功")
        
        # 显示构建文件
        dist_files = list(Path("dist").glob("*"))
        if dist_files:
            print("📦 构建文件:")
            for file in dist_files:
                print(f"   {file}")
        return True
    else:
        print("❌ 构建失败")
        return False


def uv_publish(token, test_mode=False):
    """使用uv发布包"""
    if test_mode:
        print("\n🧪 发布到测试PyPI...")
        cmd = f"uv publish --repository testpypi --token {token}"
        success_msg = "✅ 发布到测试PyPI成功！"
        link = "https://test.pypi.org/project/business-bi-mcp/"
        install_cmd = "pip install --index-url https://test.pypi.org/simple/ business-bi-mcp"
    else:
        print("\n🚀 发布到正式PyPI...")
        cmd = f"uv publish --token {token}"
        success_msg = "🎉 发布到PyPI成功！"
        link = "https://pypi.org/project/business-bi-mcp/"
        install_cmd = "pip install business-bi-mcp"
    
    result = run_command(cmd, check=False)
    
    if result and result.returncode == 0:
        print(success_msg)
        print(f"🔗 项目链接: {link}")
        print(f"📋 安装命令: {install_cmd}")
        return True
    else:
        print("❌ 发布失败")
        if result and result.stderr:
            stderr = result.stderr.lower()
            if "invalid" in stderr and "token" in stderr:
                print("🔐 Token无效，需要重新输入")
                return "invalid_token"
            elif "already exists" in stderr:
                print("⚠️ 版本已存在，请更新版本号")
                return "version_exists"
        return False


def clean_dist():
    """清理dist目录"""
    import shutil
    dist_path = Path("dist")
    if dist_path.exists():
        print("🧹 清理旧的构建文件...")
        shutil.rmtree(dist_path)


def main():
    """主函数"""
    print("🚀 Business BI MCP - 简化发布工具")
    print("=" * 50)
    
    # 检查项目
    if not Path("pyproject.toml").exists():
        print("❌ 请在项目根目录运行此脚本")
        sys.exit(1)
    
    # 检查uv
    if not check_uv():
        sys.exit(1)
    
    # 清理旧文件
    clean_dist()
    
    # 查找token
    pypi_token, testpypi_token = find_pypirc_token()
    
    # 如果没有找到token，要求用户输入
    if not pypi_token:
        print("\n❌ 未找到PyPI token配置")
        pypi_token = get_user_token()
        if not pypi_token:
            print("❌ 无效token，退出")
            sys.exit(1)
    
    # 构建包
    if not uv_build():
        print("❌ 构建失败，退出")
        sys.exit(1)
    
    # 询问发布方式
    print("\n📋 选择发布方式:")
    print("1. 直接发布到正式PyPI")
    print("2. 先发布到测试PyPI，再发布到正式PyPI")
    
    choice = input("选择 (1-2): ").strip()
    
    current_token = pypi_token
    
    if choice == "2":
        # 先发布到测试PyPI
        if testpypi_token:
            print("📝 使用配置文件中的TestPyPI token")
            test_result = uv_publish(testpypi_token, test_mode=True)
        else:
            print("📝 使用PyPI token发布到测试环境")
            test_result = uv_publish(current_token, test_mode=True)
        
        if test_result == "invalid_token":
            print("🔐 TestPyPI token无效，请输入新token")
            new_token = get_user_token()
            if new_token:
                test_result = uv_publish(new_token, test_mode=True)
        
        if not test_result or test_result == "version_exists":
            print("❌ 测试发布失败，退出")
            sys.exit(1)
        
        # 询问是否继续正式发布
        confirm = input("\n✅ 测试发布成功！是否继续发布到正式PyPI？(y/N): ")
        if confirm.lower() != 'y':
            print("🛑 用户取消正式发布")
            sys.exit(0)
    
    # 发布到正式PyPI
    result = uv_publish(current_token, test_mode=False)
    
    # 处理token无效的情况
    retry_count = 0
    while result == "invalid_token" and retry_count < 3:
        retry_count += 1
        print(f"🔄 Token无效，重试 {retry_count}/3")
        new_token = get_user_token()
        if not new_token:
            break
        current_token = new_token
        result = uv_publish(current_token, test_mode=False)
    
    if result == True:
        print("\n🎉 发布完成！")
        print("✨ 您的包已成功发布到PyPI")
    elif result == "version_exists":
        print("\n⚠️ 版本已存在")
        print("💡 请更新pyproject.toml中的版本号后重试")
    else:
        print("\n❌ 发布失败")
        print("💡 请检查token和网络连接")


if __name__ == "__main__":
    main() 