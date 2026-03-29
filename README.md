# TBROS 薪资计算系统

员工薪资计算与管理 Web 应用，基于 Flask + MongoDB Atlas。

## 功能

- 员工信息管理（增删改查）
- Excel 工时表上传与解析
- 自动计算薪资
- 月度工资单生成
- 用户认证系统

## 技术栈

- **后端**: Python 3.14.3, Flask 3.1.3, Flask-Login, Flask-WTF
- **数据库**: MongoDB Atlas (pymongo 4.16.0)
- **Excel 处理**: pandas, openpyxl, xlrd
- **图片处理**: Pillow, opencv-python
- **前端**: Jinja2 模板 + Tailwind CSS (CDN)

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
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
```

### 5. 运行应用

```bash
# 开发模式
python main.py

# 生产模式
gunicorn main:app
```

访问 `http://localhost:5000` 登录使用。

## 部署

项目已配置 Railway.app 自动部署。推送到 GitHub 后会自动触发部署。

## 项目结构

```
salary/
├── main.py              # Flask 路由
├── mongodb.py           # MongoDB 连接
├── emp/emp_mongodb.py   # 员工 CRUD
├── excels/              # Excel 处理
├── forms/form.py        # 表单定义
├── modules/image.py     # 图片处理
├── static/              # 静态资源
└── templates/           # HTML 模板
```

## 开发命令

```bash
# 代码检查
pylint main.py mongodb.py emp/ excels/ forms/ modules/

# 导入排序
isort .
```
