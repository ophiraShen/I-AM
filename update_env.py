import subprocess
import os
from datetime import datetime

def update_requirements():
    """更新环境依赖文件"""
    print("开始更新环境依赖...")
    
    # 更新 requirements.txt
    subprocess.run('pip freeze > requirements.txt', shell=True)
    print("✓ requirements.txt 已更新")
    
    # 更新 conda 环境文件
    subprocess.run('conda env export > environment.yml', shell=True)
    print("✓ environment.yml 已更新")
    
    print("\n更新完成！文件已保存：")
    print("- requirements.txt")
    print("- environment.yml")

if __name__ == "__main__":
    update_requirements(pip=True, conda=False)