# 部署指南

本文档详细说明了如何在不同环境中部署口算练习网站。

## 🚀 快速部署

### 使用Docker Compose（推荐）

1. **克隆项目**
```bash
git clone <repository-url>
cd math_quiz
```

2. **配置环境变量**
```bash
cp .env.example .env
# 编辑.env文件，设置生产环境配置
```

3. **启动服务**
```bash
docker-compose up -d
```

4. **访问应用**
- 应用地址: http://localhost
- 管理界面: http://localhost:8080 (phpMyAdmin)

### 手动部署

#### 1. 环境准备

**系统要求:**
- Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- Python 3.8+
- MySQL 8.0+ / MariaDB 10.5+
- Nginx 1.18+
- Redis 6.0+ (可选)

**安装依赖:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv mysql-server nginx redis-server

# CentOS/RHEL
sudo yum install python3 python3-pip mysql-server nginx redis
```

#### 2. 数据库设置

```bash
# 启动MySQL服务
sudo systemctl start mysql
sudo systemctl enable mysql

# 创建数据库和用户
sudo mysql -u root -p
```

```sql
CREATE DATABASE mathquiz CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'mathuser'@'localhost' IDENTIFIED BY 'secure_password_here';
GRANT ALL PRIVILEGES ON mathquiz.* TO 'mathuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 3. 应用部署

```bash
# 创建应用目录
sudo mkdir -p /var/www/mathquiz
sudo chown $USER:$USER /var/www/mathquiz
cd /var/www/mathquiz

# 克隆代码
git clone <repository-url> .

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
nano .env
```

**环境变量配置 (.env):**
```env
FLASK_ENV=production
SECRET_KEY=your-very-secure-secret-key-here
DATABASE_URL=mysql://mathuser:secure_password_here@localhost/mathquiz
REDIS_URL=redis://localhost:6379/0
```

#### 4. 初始化数据库

```bash
python3 -c "
from app import create_app
from models import db
app = create_app('production')
with app.app_context():
    db.create_all()
    print('数据库初始化完成')
"
```

#### 5. 配置Gunicorn

创建Gunicorn配置文件:
```bash
nano gunicorn.conf.py
```

```python
# gunicorn.conf.py
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
user = "www-data"
group = "www-data"
```

#### 6. 配置Systemd服务

创建服务文件:
```bash
sudo nano /etc/systemd/system/mathquiz.service
```

```ini
[Unit]
Description=Math Quiz Web Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/mathquiz
Environment=PATH=/var/www/mathquiz/venv/bin
ExecStart=/var/www/mathquiz/venv/bin/gunicorn --config gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
sudo systemctl daemon-reload
sudo systemctl start mathquiz
sudo systemctl enable mathquiz
```

#### 7. 配置Nginx

创建Nginx配置:
```bash
sudo nano /etc/nginx/sites-available/mathquiz
```

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL配置
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    
    # 静态文件
    location /static {
        alias /var/www/mathquiz/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # 应用代理
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;
    }
}
```

启用站点:
```bash
sudo ln -s /etc/nginx/sites-available/mathquiz /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔧 配置优化

### 性能优化

1. **数据库优化**
```sql
-- 添加索引
ALTER TABLE quiz_records ADD INDEX idx_user_created (user_id, created_at);
ALTER TABLE questions ADD INDEX idx_quiz_record (quiz_record_id);
```

2. **Redis缓存配置**
```bash
# 编辑Redis配置
sudo nano /etc/redis/redis.conf

# 设置内存限制
maxmemory 256mb
maxmemory-policy allkeys-lru

# 启用持久化
save 900 1
save 300 10
save 60 10000
```

3. **Nginx缓存配置**
```nginx
# 在http块中添加
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=app_cache:10m max_size=1g inactive=60m use_temp_path=off;

# 在location /中添加
proxy_cache app_cache;
proxy_cache_valid 200 302 10m;
proxy_cache_valid 404 1m;
```

### 安全配置

1. **防火墙设置**
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

2. **SSL证书（Let's Encrypt）**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

3. **定期备份**
```bash
# 创建备份脚本
sudo nano /usr/local/bin/backup-mathquiz.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/mathquiz"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
mysqldump -u mathuser -p mathquiz > $BACKUP_DIR/db_$DATE.sql

# 备份应用文件
tar -czf $BACKUP_DIR/app_$DATE.tar.gz -C /var/www mathquiz

# 删除7天前的备份
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

添加到crontab:
```bash
sudo crontab -e
# 每天凌晨2点备份
0 2 * * * /usr/local/bin/backup-mathquiz.sh
```

## 📊 监控和日志

### 应用监控

1. **日志配置**
```python
# 在config.py中添加
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/mathquiz.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

2. **系统监控**
```bash
# 安装监控工具
sudo apt install htop iotop nethogs

# 监控应用状态
sudo systemctl status mathquiz
sudo journalctl -u mathquiz -f
```

### 性能监控

1. **Nginx访问日志分析**
```bash
# 安装GoAccess
sudo apt install goaccess

# 实时分析
sudo goaccess /var/log/nginx/access.log -o /var/www/html/report.html --real-time-html
```

2. **数据库性能监控**
```sql
-- 查看慢查询
SHOW VARIABLES LIKE 'slow_query_log';
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;
```

## 🔄 更新和维护

### 应用更新

```bash
# 停止服务
sudo systemctl stop mathquiz

# 备份当前版本
cp -r /var/www/mathquiz /var/www/mathquiz.backup

# 更新代码
cd /var/www/mathquiz
git pull origin main

# 更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 数据库迁移（如有需要）
python3 -c "
from app import create_app
from models import db
app = create_app('production')
with app.app_context():
    db.create_all()
"

# 重启服务
sudo systemctl start mathquiz
```

### 故障排除

1. **常见问题**
```bash
# 检查服务状态
sudo systemctl status mathquiz nginx mysql redis

# 查看日志
sudo journalctl -u mathquiz -n 50
sudo tail -f /var/log/nginx/error.log
sudo tail -f logs/mathquiz.log
```

2. **性能问题**
```bash
# 检查资源使用
htop
df -h
free -h

# 检查数据库连接
mysql -u mathuser -p -e "SHOW PROCESSLIST;"
```

## 📞 技术支持

如果在部署过程中遇到问题，请：

1. 检查日志文件
2. 确认所有服务正常运行
3. 验证网络连接和防火墙设置
4. 查看项目文档和FAQ

更多技术支持请访问项目GitHub页面。