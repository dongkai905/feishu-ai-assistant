#!/usr/bin/env python3
"""
监控Docker安装状态
"""

import subprocess
import time
import os

def check_docker_installed():
    """检查Docker是否已安装"""
    try:
        # 检查docker命令
        result = subprocess.run(['which', 'docker'], capture_output=True, text=True)
        docker_installed = result.returncode == 0
        
        # 检查docker-compose命令
        result = subprocess.run(['which', 'docker-compose'], capture_output=True, text=True)
        docker_compose_installed = result.returncode == 0
        
        # 检查Docker Desktop应用
        docker_app_installed = os.path.exists('/Applications/Docker.app')
        
        return {
            'docker': docker_installed,
            'docker-compose': docker_compose_installed,
            'docker-app': docker_app_installed,
            'status': 'installed' if docker_installed else 'not-installed'
        }
    except Exception as e:
        return {'error': str(e), 'status': 'error'}

def check_brew_docker_status():
    """检查Homebrew Docker安装状态"""
    try:
        result = subprocess.run(['brew', 'list', '--cask'], capture_output=True, text=True)
        if 'docker' in result.stdout.lower():
            return True
        return False
    except:
        return False

def main():
    print("=" * 60)
    print("Docker安装状态监控")
    print("=" * 60)
    
    print("\n1. 检查当前Docker安装状态:")
    status = check_docker_installed()
    
    if 'error' in status:
        print(f"  检查失败: {status['error']}")
    else:
        print(f"  Docker命令: {'✅ 已安装' if status['docker'] else '❌ 未安装'}")
        print(f"  Docker Compose命令: {'✅ 已安装' if status['docker-compose'] else '❌ 未安装'}")
        print(f"  Docker Desktop应用: {'✅ 已安装' if status['docker-app'] else '❌ 未安装'}")
    
    print("\n2. 检查Homebrew Docker安装状态:")
    brew_status = check_brew_docker_status()
    print(f"  Homebrew Docker: {'✅ 已安装' if brew_status else '❌ 未安装'}")
    
    print("\n3. 系统信息:")
    try:
        # 检查系统架构
        result = subprocess.run(['uname', '-m'], capture_output=True, text=True)
        arch = result.stdout.strip()
        print(f"  系统架构: {arch}")
        
        # 检查macOS版本
        result = subprocess.run(['sw_vers', '-productVersion'], capture_output=True, text=True)
        os_version = result.stdout.strip()
        print(f"  macOS版本: {os_version}")
    except Exception as e:
        print(f"  系统信息获取失败: {e}")
    
    print("\n" + "=" * 60)
    
    # 给出建议
    if status.get('docker') and status.get('docker-compose'):
        print("🎉 Docker环境已准备就绪，可以开始生产部署！")
        return 0
    elif status.get('docker-app'):
        print("⚠️  Docker Desktop已安装，但命令行工具可能未配置")
        print("   请启动Docker Desktop应用，并完成初始配置")
        return 1
    else:
        print("❌  Docker未安装，需要继续安装过程")
        return 2

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)