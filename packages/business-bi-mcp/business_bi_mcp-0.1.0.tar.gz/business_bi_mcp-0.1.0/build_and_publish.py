#!/usr/bin/env python3
"""
自动化构建和发布脚本
用于将business-bi-mcp发布到PyPI
支持传统方式(build+twine)和现代方式(uv publish)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(cmd, check=True):
    """运行命令并处理错误"""
    print(f"🔧 执行命令: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令执行失败: {e}")
        if e.stderr:
            print(f"错误信息: {e.stderr}")
        return None


def check_uv_available():
    """检查uv是否可用"""
    result = run_command("uv --version", check=False)
    return result and result.returncode == 0


def check_publish_method():
    """检查可用的发布方法"""
    print("🔍 检查发布工具...")
    
    uv_available = check_uv_available()
    if uv_available:
        print("   ✅ uv 可用 - 推荐使用现代发布方式")
        return "uv"
    
    # 检查传统工具
    build_available = run_command("python -c 'import build'", check=False)
    twine_available = run_command("python -c 'import twine'", check=False)
    
    if build_available and build_available.returncode == 0 and twine_available and twine_available.returncode == 0:
        print("   ✅ build + twine 可用 - 使用传统发布方式")
        return "traditional"
    
    print("   ❌ 发布工具不完整")
    return None


def install_publish_tools():
    """安装发布工具"""
    print("📦 安装发布工具...")
    
    print("\n请选择安装方式:")
    print("1. 安装 uv (推荐 - 现代Python工具)")
    print("2. 安装 build + twine (传统方式)")
    
    choice = input("请选择 (1-2): ").strip()
    
    if choice == "1":
        print("🔧 安装uv...")
        print("请手动安装uv:")
        print("   Windows: https://docs.astral.sh/uv/getting-started/installation/")
        print("   或运行: powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\"")
        print("   安装完成后重新运行此脚本")
        return False
    
    elif choice == "2":
        print("🔧 安装 build + twine...")
        result = run_command("pip install build twine wheel")
        return result and result.returncode == 0
    
    return False


def get_api_token_input():
    """获取API令牌输入"""
    print("\n🔐 请提供PyPI API令牌:")
    pypi_token = input("PyPI API令牌 (pypi-开头): ").strip()
    
    if not pypi_token.startswith("pypi-"):
        print("❌ API令牌格式错误，应该以'pypi-'开头")
        return None, None
    
    testpypi_token = input("TestPyPI API令牌 (可选，按回车跳过): ").strip()
    if testpypi_token and not testpypi_token.startswith("pypi-"):
        print("⚠️  TestPyPI令牌格式错误，跳过")
        testpypi_token = None
    
    return pypi_token, testpypi_token


def uv_publish_to_test(token=None):
    """使用uv发布到测试PyPI"""
    print("🧪 使用uv发布到测试PyPI...")
    
    if not token:
        token = input("请输入TestPyPI API令牌: ").strip()
    
    cmd = f"uv publish --repository testpypi --token {token}"
    result = run_command(cmd, check=False)
    
    if result and result.returncode == 0:
        print("✅ 使用uv上传到测试PyPI成功！")
        print("🔗 测试链接: https://test.pypi.org/project/business-bi-mcp/")
        print("\n📋 测试安装命令:")
        print("   pip install --index-url https://test.pypi.org/simple/ business-bi-mcp")
        return True
    else:
        print("❌ uv上传到测试PyPI失败")
        if result and result.stderr:
            print(f"错误详情: {result.stderr}")
        return False


def uv_publish_to_pypi(token=None):
    """使用uv发布到正式PyPI"""
    print("🚀 使用uv发布到正式PyPI...")
    
    confirm = input("⚠️  确认要发布到正式PyPI吗？这个操作不可撤销！(yes/no): ")
    if confirm.lower() != "yes":
        print("❌ 用户取消发布")
        return False
    
    if not token:
        token = input("请输入PyPI API令牌: ").strip()
    
    cmd = f"uv publish --token {token}"
    result = run_command(cmd, check=False)
    
    if result and result.returncode == 0:
        print("🎉 使用uv发布到PyPI成功！")
        print("🔗 项目链接: https://pypi.org/project/business-bi-mcp/")
        print("\n📋 安装命令:")
        print("   pip install business-bi-mcp")
        return True
    else:
        print("❌ uv发布到PyPI失败")
        return False


def check_pypi_auth():
    """检查PyPI认证配置"""
    print("🔐 检查PyPI认证配置...")
    
    # 检查环境变量
    twine_username = os.getenv('TWINE_USERNAME')
    twine_password = os.getenv('TWINE_PASSWORD')
    
    if twine_username and twine_password:
        print("   ✅ 找到环境变量认证配置")
        if twine_username == "__token__" and twine_password.startswith("pypi-"):
            print("   ✅ API令牌格式正确")
            return True
        else:
            print("   ⚠️  环境变量格式可能不正确")
    
    # 检查.pypirc文件
    home_dir = Path.home()
    pypirc_path = home_dir / ".pypirc"
    
    if pypirc_path.exists():
        print(f"   ✅ 找到.pypirc文件: {pypirc_path}")
        try:
            content = pypirc_path.read_text(encoding='utf-8')
            if "__token__" in content and "pypi-" in content:
                print("   ✅ .pypirc文件包含API令牌配置")
                return True
            else:
                print("   ⚠️  .pypirc文件可能缺少API令牌配置")
        except Exception as e:
            print(f"   ❌ 读取.pypirc文件失败: {e}")
    
    # 如果都没有配置，提供配置指导
    print("   ❌ 未找到PyPI认证配置")
    print("\n🔧 配置PyPI认证的方法：")
    print("\n方法1：创建.pypirc文件")
    print(f"   在 {home_dir} 目录创建 .pypirc 文件，内容如下：")
    print("""
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
  username = __token__
  password = pypi-你的API令牌

[testpypi]
  repository = https://test.pypi.org/legacy/
  username = __token__
  password = pypi-你的TestPyPI令牌
""")
    
    print("\n方法2：设置环境变量")
    print("   export TWINE_USERNAME=__token__")
    print("   export TWINE_PASSWORD=pypi-你的API令牌")
    
    print("\n📋 获取API令牌的步骤：")
    print("   1. 访问 https://pypi.org/account/register/ 注册账号")
    print("   2. 登录后进入 Account settings > API tokens")
    print("   3. 点击 'Add API token'，选择 'Entire account' 权限")
    print("   4. 复制生成的令牌（以pypi-开头）")
    print("   5. 配置到.pypirc文件或环境变量中")
    
    print("\n⚠️  建议同时注册TestPyPI用于测试: https://test.pypi.org/account/register/")
    
    return False


def setup_pypirc_interactive():
    """交互式配置.pypirc文件"""
    print("🔧 交互式配置PyPI认证...")
    
    home_dir = Path.home()
    pypirc_path = home_dir / ".pypirc"
    
    print(f"将在 {pypirc_path} 创建配置文件")
    
    # 获取用户输入
    print("\n请提供PyPI API令牌信息：")
    pypi_token = input("PyPI API令牌 (pypi-开头): ").strip()
    
    if not pypi_token.startswith("pypi-"):
        print("❌ API令牌格式错误，应该以'pypi-'开头")
        return False
    
    testpypi_token = input("TestPyPI API令牌 (可选，按回车跳过): ").strip()
    
    # 生成配置文件内容
    config_content = f"""[distutils]
index-servers =
    pypi"""
    
    if testpypi_token:
        config_content += "\n    testpypi"
    
    config_content += f"""

[pypi]
  username = __token__
  password = {pypi_token}
"""
    
    if testpypi_token:
        config_content += f"""
[testpypi]
  repository = https://test.pypi.org/legacy/
  username = __token__
  password = {testpypi_token}
"""
    
    # 写入文件
    try:
        pypirc_path.write_text(config_content, encoding='utf-8')
        # 设置文件权限（仅所有者可读写）
        if hasattr(os, 'chmod'):
            os.chmod(pypirc_path, 0o600)
        print(f"✅ 配置文件创建成功: {pypirc_path}")
        return True
    except Exception as e:
        print(f"❌ 创建配置文件失败: {e}")
        return False


def clean_build_files():
    """清理构建文件"""
    print("🧹 清理构建文件...")
    
    dirs_to_remove = ["build", "dist", "*.egg-info"]
    for pattern in dirs_to_remove:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                print(f"   删除目录: {path}")
                shutil.rmtree(path)
            elif path.is_file():
                print(f"   删除文件: {path}")
                path.unlink()


def check_dependencies():
    """检查必要的依赖"""
    print("📦 检查发布依赖...")
    
    required_packages = ["build", "twine"]
    missing_packages = []
    
    for package in required_packages:
        result = run_command(f"python -c 'import {package}'", check=False)
        if result and result.returncode != 0:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"⚠️  缺少依赖: {', '.join(missing_packages)}")
        install_cmd = f"pip install {' '.join(missing_packages)}"
        print(f"🔧 安装命令: {install_cmd}")
        
        if input("是否现在安装？(y/N): ").lower() == 'y':
            run_command(install_cmd)
        else:
            print("❌ 请先安装必要依赖")
            return False
    
    print("✅ 所有依赖已满足")
    return True


def build_package():
    """构建包"""
    print("🏗️  构建Python包...")
    
    result = run_command("python -m build")
    if not result:
        return False
    
    # 检查构建结果
    dist_files = list(Path("dist").glob("*"))
    if not dist_files:
        print("❌ 构建失败：dist目录为空")
        return False
    
    print("✅ 包构建成功！")
    print("📦 构建文件:")
    for file in dist_files:
        print(f"   {file}")
    
    return True


def check_package():
    """检查包的质量"""
    print("🔍 检查包质量...")
    
    result = run_command("twine check dist/*")
    if not result:
        return False
    
    print("✅ 包质量检查通过")
    return True


def upload_to_test_pypi():
    """上传到测试PyPI"""
    print("🧪 上传到测试PyPI...")
    
    cmd = "twine upload --repository testpypi dist/*"
    print(f"执行命令: {cmd}")
    
    result = run_command(cmd, check=False)
    if result and result.returncode == 0:
        print("✅ 上传到测试PyPI成功！")
        print("🔗 测试链接: https://test.pypi.org/project/business-bi-mcp/")
        print("\n📋 测试安装命令:")
        print("   pip install --index-url https://test.pypi.org/simple/ business-bi-mcp")
        return True
    else:
        print("❌ 上传到测试PyPI失败")
        if result and result.stderr:
            print(f"错误详情: {result.stderr}")
        return False


def upload_to_pypi():
    """上传到正式PyPI"""
    print("🚀 上传到正式PyPI...")
    
    confirm = input("⚠️  确认要发布到正式PyPI吗？这个操作不可撤销！(yes/no): ")
    if confirm.lower() != "yes":
        print("❌ 用户取消发布")
        return False
    
    cmd = "twine upload dist/*"
    print(f"执行命令: {cmd}")
    
    result = run_command(cmd, check=False)
    if result and result.returncode == 0:
        print("🎉 发布到PyPI成功！")
        print("🔗 项目链接: https://pypi.org/project/business-bi-mcp/")
        print("\n📋 安装命令:")
        print("   pip install business-bi-mcp")
        return True
    else:
        print("❌ 发布到PyPI失败")
        if result and result.stderr:
            print(f"错误详情: {result.stderr}")
        return False


def uv_build_package():
    """使用uv构建包"""
    print("🏗️  使用uv构建Python包...")
    
    result = run_command("uv build", check=False)
    if result and result.returncode == 0:
        # 检查构建结果
        dist_files = list(Path("dist").glob("*"))
        if not dist_files:
            print("❌ 构建失败：dist目录为空")
            return False
        
        print("✅ uv包构建成功！")
        print("📦 构建文件:")
        for file in dist_files:
            print(f"   {file}")
        return True
    else:
        print("❌ uv构建失败")
        if result and result.stderr:
            print(f"错误详情: {result.stderr}")
        return False


def uv_check_package():
    """使用uv检查包"""
    print("🔍 使用uv检查包...")
    
    # uv没有直接的check命令，但可以用dry-run来验证
    result = run_command("uv publish --dry-run --token dummy", check=False)
    if result and result.returncode == 0:
        print("✅ 包检查通过")
        return True
    else:
        print("⚠️  包可能存在问题")
        return False


def main():
    """主函数"""
    print("🚀 Business BI MCP - PyPI发布工具")
    print("=" * 50)
    
    # 检查当前目录
    if not Path("pyproject.toml").exists():
        print("❌ 错误：请在项目根目录执行此脚本")
        sys.exit(1)
    
    # 检查发布方法
    publish_method = check_publish_method()
    
    if not publish_method:
        print("\n❌ 没有找到可用的发布工具")
        if install_publish_tools():
            publish_method = check_publish_method()
        else:
            print("请手动安装发布工具后重试")
            sys.exit(1)
    
    # 选择发布模式
    print("\n📋 发布选项:")
    if publish_method == "uv":
        print("1. 完整发布流程 (uv - 现代方式)")
        print("2. 仅构建包 (uv build)")
        print("3. 构建并检查包 (uv build + check)")
        print("4. 发布到测试PyPI (uv)")
        print("5. 发布到正式PyPI (uv)")
        print("6. 传统方式发布 (build + twine)")
        print("7. 清理构建文件")
        print("8. 配置PyPI认证")
        max_choice = 8
    else:
        print("1. 完整发布流程 (传统方式)")
        print("2. 仅构建和检查")
        print("3. 发布到测试PyPI")
        print("4. 发布到正式PyPI")
        print("5. 清理构建文件")
        print("6. 配置PyPI认证")
        max_choice = 6
    
    choice = input(f"\n请选择 (1-{max_choice}): ").strip()
    
    if (publish_method == "uv" and choice == "8") or (publish_method != "uv" and choice == "6"):
        # 配置认证
        if setup_pypirc_interactive():
            print("✅ PyPI认证配置完成！")
            print("现在可以使用其他选项进行发布了。")
        sys.exit(0)
    
    if choice == "1":
        # 完整流程
        if publish_method == "uv":
            print("🚀 使用现代方式发布 (uv)")
            pypi_token, testpypi_token = get_api_token_input()
            if not pypi_token:
                sys.exit(1)
            
            if testpypi_token and input("\n是否先发布到测试PyPI？(y/N): ").lower() == 'y':
                if uv_publish_to_test(testpypi_token):
                    if input("\n测试成功！是否发布到正式PyPI？(y/N): ").lower() == 'y':
                        uv_publish_to_pypi(pypi_token)
            else:
                uv_publish_to_pypi(pypi_token)
        else:
            print("🔧 使用传统方式发布 (build + twine)")
            clean_build_files()
            if not check_dependencies():
                sys.exit(1)
            if not check_pypi_auth():
                print("\n❌ PyPI认证未配置，请先选择选项6配置认证")
                sys.exit(1)
            if not build_package():
                sys.exit(1)
            if not check_package():
                sys.exit(1)
            
            if input("\n是否继续上传到测试PyPI？(y/N): ").lower() == 'y':
                if upload_to_test_pypi():
                    if input("\n测试成功！是否发布到正式PyPI？(y/N): ").lower() == 'y':
                        upload_to_pypi()
    
    elif choice == "2":
        if publish_method == "uv":
            # uv仅构建
            clean_build_files()
            uv_build_package()
        else:
            # 仅构建检查
            clean_build_files()
            if not check_dependencies():
                sys.exit(1)
            if not build_package():
                sys.exit(1)
            check_package()
    
    elif choice == "3":
        if publish_method == "uv":
            # uv构建并检查
            clean_build_files()
            if uv_build_package():
                uv_check_package()
        else:
            # 测试PyPI
            if not check_pypi_auth():
                print("\n❌ PyPI认证未配置，请先选择选项6配置认证")
                sys.exit(1)
            if not Path("dist").exists() or not list(Path("dist").glob("*")):
                print("⚠️  没有找到构建文件，先构建包...")
                if not build_package():
                    sys.exit(1)
            upload_to_test_pypi()
    
    elif choice == "4":
        if publish_method == "uv":
            testpypi_token = input("请输入TestPyPI API令牌: ").strip()
            uv_publish_to_test(testpypi_token)
        else:
            # 正式PyPI
            if not check_pypi_auth():
                print("\n❌ PyPI认证未配置，请先选择选项6配置认证")
                sys.exit(1)
            if not Path("dist").exists() or not list(Path("dist").glob("*")):
                print("⚠️  没有找到构建文件，先构建包...")
                if not build_package():
                    sys.exit(1)
            upload_to_pypi()
    
    elif choice == "5":
        if publish_method == "uv":
            pypi_token = input("请输入PyPI API令牌: ").strip()
            uv_publish_to_pypi(pypi_token)
        else:
            # 清理
            clean_build_files()
    
    elif choice == "6":
        if publish_method == "uv":
            print("🔧 切换到传统方式...")
            if not check_dependencies():
                sys.exit(1)
            if not check_pypi_auth():
                print("\n❌ PyPI认证未配置，请先选择选项6配置认证")
                sys.exit(1)
            clean_build_files()
            if not build_package():
                sys.exit(1)
            if not check_package():
                sys.exit(1)
            
            if input("\n是否继续上传到测试PyPI？(y/N): ").lower() == 'y':
                if upload_to_test_pypi():
                    if input("\n测试成功！是否发布到正式PyPI？(y/N): ").lower() == 'y':
                        upload_to_pypi()
        else:
            # 这里是传统方式的选项6，应该是配置认证，但已经在上面处理了
            pass
    
    elif choice == "7" and publish_method == "uv":
        # 清理（仅uv模式有此选项）
        clean_build_files()
    
    else:
        print("❌ 无效选择")
        sys.exit(1)
    
    print("\n✨ 操作完成！")


if __name__ == "__main__":
    main() 