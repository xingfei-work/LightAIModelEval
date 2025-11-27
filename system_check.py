#!/usr/bin/env python3
"""
系统完整性检查脚本
用于验证系统是否具备运行的基本条件
"""

import sys
import os
import subprocess
import time

def check_python_version():
    """检查Python版本"""
    print("检查Python版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python版本 {version.major}.{version.minor}.{version.micro} 符合要求")
        return True
    else:
        print(f"❌ Python版本过低: {version.major}.{version.minor}.{version.micro}")
        print("   请使用Python 3.8或更高版本")
        return False

def check_required_packages():
    """检查必需的Python包"""
    print("\n检查必需的Python包...")
    required_packages = [
        "fastapi",
        "uvicorn", 
        "sqlalchemy",
        "cryptography",
        "requests",
        "minio"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"❌ {package} 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n💡 安装缺失的包:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_frontend_dependencies():
    """检查前端依赖"""
    print("\n检查前端依赖...")
    
    # 检查Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()} 已安装")
        else:
            print("❌ Node.js 未安装")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Node.js 未安装")
        return False
    
    # 检查npm (在某些系统上，npm可能与node一起安装)
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ npm {result.stdout.strip()} 已安装")
        else:
            # 尝试使用node附带的npm
            result = subprocess.run(["node", "-e", "console.log(typeof require !== 'undefined' ? 'npm available' : 'npm not available')"], 
                                  capture_output=True, text=True, timeout=10)
            if "available" in result.stdout:
                print("✅ npm 可用（通过Node.js）")
            else:
                print("⚠️  npm 未找到，但Node.js可用")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️  npm 未找到，但Node.js可用")
    
    # 检查前端依赖是否安装
    if os.path.exists("eval-ui/node_modules"):
        print("✅ 前端依赖已安装")
    else:
        print("⚠️  前端依赖未安装，需要运行: cd eval-ui && npm install")
    
    return True

def check_file_structure():
    """检查文件结构"""
    print("\n检查文件结构...")
    
    required_files = [
        "backend/main.py",
        "backend/database.py",
        "backend/storage.py",
        "services/api_config_service.py",
        "opencompass/models/unified_api.py",
        "eval-ui/src/App.vue",
        "eval-ui/package.json"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} 存在")
        else:
            print(f"❌ {file_path} 不存在")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def check_database_access():
    """检查数据库访问"""
    print("\n检查数据库访问...")
    
    try:
        from backend.database import DatabaseManager
        db_manager = DatabaseManager("sqlite:///./test.db")
        # 尝试创建表
        from backend.database import Base
        Base.metadata.create_all(bind=db_manager.engine)
        print("✅ 数据库访问正常")
        return True
    except Exception as e:
        print(f"❌ 数据库访问失败: {e}")
        return False

def main():
    """主检查函数"""
    print("=" * 50)
    print("LightAIModelEval 系统完整性检查")
    print("=" * 50)
    
    all_checks_passed = True
    
    # 执行各项检查
    all_checks_passed &= check_python_version()
    all_checks_passed &= check_required_packages()
    all_checks_passed &= check_frontend_dependencies()
    all_checks_passed &= check_file_structure()
    all_checks_passed &= check_database_access()
    
    print("\n" + "=" * 50)
    if all_checks_passed:
        print("🎉 系统检查通过！")
        print("系统已准备好运行。")
        print("\n🚀 启动系统:")
        print("   后端: cd backend && python main.py")
        print("   前端: cd eval-ui && npm run dev")
        print("\n💡 提示:")
        print("   如果前端依赖未安装，请先运行: cd eval-ui && npm install")
    else:
        print("⚠️  系统检查未完全通过！")
        print("请根据上面的提示修复问题后再试。")
    print("=" * 50)
    
    return 0 if all_checks_passed else 1

if __name__ == "__main__":
    sys.exit(main())