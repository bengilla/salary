# PROJECT_LOCAL.md — 薪资计算系统本地文档

## 部署信息

**服务器平台**: Railway.app
**自动部署**: GitHub 推送后自动触发部署
**项目地址**: https://github.com/bengilla/salary
**线上域名**: https://tbros.my

### Railway 自定义域名配置

- 域名 `tbros.my` 在 Namecheap 购买
- DNS 配置：
  - TXT 记录：`_railway-verify` → Railway 提供的验证值
  - CNAME 记录：`www` → `cywc9rg7.up.railway.app`
- Railway 端口填 **5001**
- 状态变为 **Healthy** 后即可访问

## 本地开发环境

### 环境变量配置

在项目根目录创建 `.env` 文件：

```env
# MongoDB Atlas 连接字符串
DB_URL=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<database>

# Flask 密钥
SECRET_KEY=<your-secret-key>

# 登录凭证
LOGIN_USERNAME=your_username
LOGIN_PASSWORD=your_password
```

### 本地运行

```bash
# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 开发模式运行（端口 5001）
python main.py

# 或使用 gunicorn
gunicorn main:app
```

### 目录结构

```
salary/
├── main.py              # Flask 应用入口，所有路由
├── mongodb.py           # MongoDB 连接类
├── requirements.txt     # 依赖列表
├── .env                 # 环境变量（不上传）
├── .gitignore           # Git 忽略配置
├── emp/
│   └── emp_mongodb.py   # 员工信息 CRUD
├── excels/
│   ├── __init__.py      # 薪资计算编排类
│   └── excel_module.py  # Excel 读取、时间计算
├── forms/
│   └── form.py          # WTForms 表单
├── modules/
│   └── image.py         # 图片处理
├── static/              # 静态资源
└── templates/           # Jinja2 模板
```

### 代码质量

```bash
# 代码检查
pylint main.py mongodb.py emp/ excels/ forms/ modules/

# 导入排序
isort .
```

## 手机测试

手机和电脑需在同一 WiFi 下：
- 电脑 IP: `192.168.31.63`
- 手机访问: `http://192.168.31.63:5001`

## 注意事项

- `.env` 文件包含数据库凭证，**严禁提交到 Git**
- Railway 的环境变量在 Railway Dashboard 设置，不从 .env 读取
- Python 3.14.3 为必需版本
- Tailwind CSS 通过 CDN 加载，无需 npm 构建

## ⚠️ 暂停部署（2026年3月30日起约一周）

**暂时禁用 GitHub 推送触发 Railway 自动部署**

原因：需要整理代码，更新期间不希望触发 Railway 部署。

恢复方式：删除此注意事项或将 `RAILWAY_NO_DEPLOY` 环境变量设为 `false`
