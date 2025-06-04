#!/usr/bin/env python3
"""
应用启动脚本
支持不同环境的启动配置
"""

import os
import sys
from app import create_app
from models import db

def main():
    """主函数"""
    # 获取环境变量
    env = os.environ.get('FLASK_ENV', 'development')
    
    # 创建应用
    app = create_app(env)
    
    # 在应用上下文中创建数据库表
    with app.app_context():
        db.create_all()
        print(f"数据库表已创建/更新")
    
    # 获取启动参数
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = env == 'development'
    
    print(f"启动环境: {env}")
    print(f"访问地址: http://{host}:{port}")
    
    # 启动应用
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    main()