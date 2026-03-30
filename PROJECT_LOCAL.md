# PROJECT_LOCAL.md — 薪资计算系统本地文档

## 部署信息

**服务器平台**: Railway.app
**自动部署**: GitHub 推送后自动触发部署（已禁用 `RAILWAY_NO_DEPLOY=true`）
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

# MongoDB 切换（本地开发用）
USE_LOCAL_DB=true   # true=本地 MongoDB，false=Atlas
```

### 本地运行

```bash
# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 本地开发模式运行（端口 5001）
USE_LOCAL_DB=true python main.py

# 或使用 gunicorn
gunicorn main:app
```

### 目录结构（重构后）

```
salary/
├── main.py              # Flask 应用入口
├── mongodb.py           # MongoDB 连接类（支持 USE_LOCAL_DB 切换）
├── config.json          # 工时配置（可调整工作时间、加班规则）
├── requirements.txt     # 依赖列表
├── .env                # 环境变量（不上传）
├── .gitignore           # Git 忽略配置
├── models/              # 数据模型
├── services/            # 业务逻辑
│   ├── employee_service.py   # 员工 CRUD
│   ├── salary_batch.py      # 薪资批次处理
│   ├── salary_calculator.py  # 薪资计算（新算法）
│   └── excel_reader.py      # Excel 读取
├── routes/              # Flask 路由
│   ├── auth.py          # 登录登出
│   ├── employees.py     # 员工管理
│   └── salary.py        # 薪资管理
├── forms/               # WTForms 表单
├── utils/               # 工具函数
│   └── image.py         # 图片处理
├── static/             # 静态资源
└── templates/           # Jinja2 模板
```

### 工时配置 (config.json)

```json
{
  "versions": {
    "v0800": {
      "start": "08:00",
      "end": "17:00",
      "overtime_start": "17:00",
      "max_time": "23:30"
    },
    "v0830": {
      "start": "08:30",
      "end": "17:30",
      "overtime_start": "17:30",
      "max_time": "24:00"
    }
  }
}
```

### 加班计算规则

**标准工时**: 08:00-17:00（8小时），午餐 12:00-13:00 不计入

**加班规则**:
- 17:00-18:30 = 2小时（如超过1.5小时）
- 18:30-20:30 = 2小时
- 20:30-21:30 = 2小时（需触发1830-2130条件）
- 21:30后 = 每1小时计1小时

**早到处理**: 08:00前到达不算，09:00后到达从10:00起算

## 手机测试

手机和电脑需在同一 WiFi 下：
- 电脑 IP: `192.168.31.63`
- 手机访问: `http://192.168.31.63:5001`

## MongoDB 本地数据

从 Atlas 导入本地：
```bash
# 导出
mongodump --uri="mongodb+srv://..." --out=/tmp/mongo_dump

# 导入
mongorestore --db TBROSVENTURESSDNBHD /tmp/mongo_dump/TBROSVENTURESSDNBHD
```

## 注意事项

- `.env` 文件包含数据库凭证，**严禁提交到 Git**
- Railway 的环境变量在 Railway Dashboard 设置，不从 .env 读取
- Python 3.14 为必需版本
- Tailwind CSS 通过 CDN 加载，无需 npm 构建
- `USE_LOCAL_DB=true` 时连接本地 MongoDB（127.0.0.1:27017）
