# TBROS 薪资计算系统

员工薪资计算与管理 Web 应用，基于 Flask + MongoDB Atlas。

## 功能

- 员工信息管理（增删改查）
- Excel 工时表上传与解析
- 自动计算薪资（支持 08:00 和 08:30 两个版本）
- 月度工资单生成
- 用户认证系统

## 技术栈

- **后端**: Python 3.14, Flask 3.1, Flask-Login, Flask-WTF
- **数据库**: MongoDB Atlas (pymongo)
- **Excel 处理**: pandas, openpyxl, xlrd
- **图片处理**: Pillow
- **前端**: Jinja2 模板 + Tailwind CSS (CDN)

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/bengilla/salary
cd salary
```

### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

创建 `.env` 文件：

```env
DB_URL=<MongoDB Atlas 连接字符串>
SECRET_KEY=<Flask 密钥>
LOGIN_USERNAME=<登录用户名>
LOGIN_PASSWORD=<登录密码>
USE_LOCAL_DB=false
```

### 5. 运行应用

```bash
# 开发模式（本地 MongoDB）
USE_LOCAL_DB=true python main.py

# 生产模式
gunicorn main:app
```

访问 `http://localhost:5001` 登录使用。

## 项目结构

```
salary/
├── main.py              # Flask 应用入口
├── mongodb.py           # MongoDB 连接（支持本地/远程切换）
├── config.json          # 工时和加班规则配置
├── models/              # 数据模型
├── services/            # 业务逻辑
│   ├── employee_service.py   # 员工 CRUD
│   ├── salary_batch.py      # 薪资批次处理
│   ├── salary_calculator.py  # 薪资计算
│   └── excel_reader.py      # Excel 读取
├── routes/             # Flask 路由
├── forms/              # WTForms 表单
├── utils/              # 工具函数
├── static/             # 静态资源
└── templates/          # HTML 模板
```

## 加班计算规则

**标准工时**: 08:00-17:00（8小时），午餐 12:00-13:00 不计入

**加班规则**:
- 17:00-18:30 = 2小时（如超过1.5小时）
- 18:30-20:30 = 2小时
- 20:30-21:30 = 2小时（需触发1830-2130条件）
- 21:30后 = 每1小时计1小时

## 部署

项目已配置 Railway.app 自动部署。推送到 GitHub 后会自动触发部署。

## 开发命令

```bash
# 代码检查
pylint main.py mongodb.py models/ services/ routes/ forms/ utils/

# 导入排序
isort .
```
