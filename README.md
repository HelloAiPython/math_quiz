# 口算练习网站

一个基于Flask的现代化口算练习Web应用，提供用户系统、多种练习模式、统计分析和排行榜功能。

## 🌟 主要特性

### 核心功能
- **用户系统**: 注册、登录、个人资料管理
- **多种练习模式**: 加法、减法、乘法、除法、混合运算
- **难度分级**: 简单、中等、困难三个难度等级
- **实时统计**: 准确率、用时、得分等详细统计
- **练习历史**: 完整的练习记录和历史回顾
- **排行榜**: 用户排名和竞争机制

### 技术特性
- **响应式设计**: 支持桌面和移动设备
- **PWA支持**: 可安装为原生应用
- **离线功能**: Service Worker缓存支持
- **API接口**: RESTful API设计
- **数据导出**: CSV格式数据导出
- **错误处理**: 完善的错误处理和日志记录

## 功能特性

### 用户系统
- 用户注册和登录
- 密码安全存储（使用Werkzeug密码哈希）
- 用户会话管理

### 练习功能
- 支持四种运算类型：加法、减法、乘法、除法
- 三种难度等级：
  - 简单：1-10范围内的数字
  - 中等：1-20范围内的数字
  - 困难：1-100范围内的数字
- 可自定义题目数量（1-20题）
- 实时计时功能
- 自动评分系统

### 数据统计
- 练习历史记录
- 详细的练习结果展示
- 个人统计信息：
  - 总分数和练习次数
  - 按难度和运算类型的统计
  - 正确率分析
  - 练习时间统计
- 练习趋势分析

## 技术栈

- **后端**: Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF
- **数据库**: MySQL/MariaDB
- **前端**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Python包**: PyMySQL, email_validator, python-dotenv

## 安装和运行

### 1. 环境要求
- Python 3.7+
- MySQL/MariaDB 数据库

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 数据库配置
创建MySQL数据库和用户：
```sql
CREATE DATABASE math_quiz CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'mathuser'@'localhost' IDENTIFIED BY 'mathpass123';
GRANT ALL PRIVILEGES ON math_quiz.* TO 'mathuser'@'localhost';
FLUSH PRIVILEGES;
```

### 4. 环境变量配置
创建`.env`文件：
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=mysql+pymysql://mathuser:mathpass123@localhost/math_quiz
```

### 5. 运行应用
```bash
python app.py
```

应用将在 http://localhost:5000 启动。

## 项目结构

```
math_quiz/
├── app.py              # 主应用文件
├── models.py           # 数据库模型
├── forms.py            # WTF表单定义
├── config.py           # 配置文件
├── requirements.txt    # Python依赖
├── .env               # 环境变量（需要创建）
├── static/            # 静态文件
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
└── templates/         # HTML模板
    ├── base.html
    ├── index.html
    ├── login.html
    ├── register.html
    ├── quiz_settings.html
    ├── quiz.html
    ├── quiz_result.html
    ├── quiz_detail.html
    ├── history.html
    └── statistics.html
```

## 数据库模型

### User（用户表）
- id: 主键
- username: 用户名（唯一）
- email: 邮箱（唯一）
- password_hash: 密码哈希
- created_at: 创建时间

### QuizRecord（练习记录表）
- id: 主键
- user_id: 用户ID（外键）
- difficulty: 难度等级
- operation_type: 运算类型
- total_questions: 总题数
- correct_answers: 正确答案数
- score: 得分
- time_taken: 用时（秒）
- created_at: 创建时间

### Question（题目表）
- id: 主键
- quiz_record_id: 练习记录ID（外键）
- question_text: 题目文本
- correct_answer: 正确答案
- user_answer: 用户答案
- is_correct: 是否正确
- time_taken: 答题用时（秒）

## 特色功能

1. **智能题目生成**: 根据难度等级和运算类型自动生成合适的数学题目
2. **实时计时**: 记录每道题的答题时间和总用时
3. **详细统计**: 提供多维度的练习数据分析
4. **响应式设计**: 支持桌面和移动设备访问
5. **用户友好**: 简洁直观的界面设计

## 开发者

这是一个演示项目，展示了如何使用Flask和MySQL构建一个完整的Web应用程序。

## 许可证

MIT License