#!/bin/bash
# 项目设置脚本

set -e

echo "=== 口算练习网站项目设置 ==="

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "错误: 需要Python $required_version 或更高版本，当前版本: $python_version"
    exit 1
fi

echo "✓ Python版本检查通过: $python_version"

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
    echo "✓ 虚拟环境创建完成"
else
    echo "✓ 虚拟环境已存在"
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "升级pip..."
pip install --upgrade pip

# 安装依赖
echo "安装项目依赖..."
pip install -r requirements.txt

# 创建必要的目录
echo "创建必要的目录..."
mkdir -p logs
mkdir -p instance
mkdir -p static/uploads

# 设置环境变量文件
if [ ! -f ".env" ]; then
    echo "创建环境变量文件..."
    cat > .env << EOF
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=mysql://root:password@localhost/mathquiz
REDIS_URL=redis://localhost:6379/0
EOF
    echo "✓ .env文件创建完成"
else
    echo "✓ .env文件已存在"
fi

# 设置数据库
echo "设置数据库..."
python3 -c "
from app import create_app
from models import db
app = create_app('development')
with app.app_context():
    db.create_all()
    print('数据库表创建完成')
"

echo ""
echo "=== 设置完成 ==="
echo "启动开发服务器: python3 run.py"
echo "运行测试: python3 -m pytest tests/"
echo "Docker部署: docker-compose up -d"
echo ""