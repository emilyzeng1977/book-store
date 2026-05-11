brew install python@3.12

[//]: # (brew link --force --overwrite python@3.12)

[//]: # (python3 --version   # 确认是 3.12.x)

# 1. 创建虚拟环境（在当前目录下建一个 venv 文件夹）

[//]: # (python3 -m venv venv)
python3.12 -m venv venv
# 2. 激活虚拟环境
source venv/bin/activate   # macOS / Linux

# 3. 安装 requirements.txt
pip install --no-cache-dir -r requirements.txt

# 4. 验证安装
pip list