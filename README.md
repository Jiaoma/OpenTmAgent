# OpenTmAgent

企业级项目管理和团队管理平台，支持Telegram Bot、Web界面和CLI三种访问方式。

## 功能特性

### 团队管理
- 人员档案管理
- 人员能力模型管理
- 小组管理
- 任务负载估算
- 关系图展示
- 能力雷达图

### 项目管理
- 版本管理
- 迭代管理
- 任务管理
- 任务依赖关系
- 甘特图展示
- 任务达成统计

### 架构档案
- 模块层级管理
- 功能层级管理
- 责任田管理
- Mermaid图表导出

## 技术栈

- **后端**: Python FastAPI
- **数据库**: SQLite
- **前端**: Vue3 + Element Plus
- **图表**: ECharts
- **LLM**: Ollama (可选)
- **部署**: Docker + Nginx

## 环境要求

- Python 3.9+
- Node.js 18+
- Docker & Docker Compose (可选)

## 快速开始

### 方式一：Docker部署（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/OpenTmAgent.git
cd OpenTmAgent

# 2. 创建环境变量文件
cp .env.example .env

# 3. 编辑.env文件，设置必要的配置
# 必须修改: JWT_SECRET_KEY
# 可选修改: TELEGRAM_BOT_TOKEN (如需使用Telegram Bot)

# 4. 启动服务
docker-compose up -d

# 5. 查看日志
docker-compose logs -f

# 6. 访问服务
# Web界面: http://localhost
# API文档: http://localhost:8000/docs
# 健康检查: http://localhost/health
```

### 方式二：本地开发

#### 1. 后端启动

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 或使用 pip3 (macOS/Linux)
pip3 install -r requirements.txt

# 创建数据和日志目录
mkdir -p data logs

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或使用 python3
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端启动后访问：
- API服务: http://localhost:8000
- Swagger文档: http://localhost:8000/docs
- ReDoc文档: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health

#### 2. 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

前端启动后访问: http://localhost:3000

#### 3. CLI启动

```bash
# 在项目根目录
cd cli

# 安装CLI依赖
pip install prompt-toolkit requests

# 启动CLI
python3 cli.py
```

CLI使用示例：
```
OpenTmAgent> help                          # 查看帮助
OpenTmAgent> login EMP001                  # 访客登录
OpenTmAgent> admin-login ADMIN001 mypass   # 管理员登录
OpenTmAgent> list persons                  # 查看人员列表
OpenTmAgent> add person                    # 添加人员
OpenTmAgent> list groups                   # 查看小组列表
OpenTmAgent> list versions                 # 查看版本列表
OpenTmAgent> export modules                # 导出模块Mermaid图
OpenTmAgent> exit                           # 退出
```

#### 4. Telegram Bot启动

```bash
# 1. 创建Telegram Bot
# 在Telegram中搜索 @BotFather
# 发送 /newbot 创建新Bot
# 获取Bot Token

# 2. 配置环境变量
# 编辑 .env 文件，添加:
TELEGRAM_BOT_TOKEN=your_bot_token_here

# 3. 启动Bot (在后端目录)
cd backend
python3 -m app.telegram_bot.bot
```

Bot可用命令：
- `/start` - 开始使用
- `/help` - 查看帮助
- `/login <工号>` - 访客登录
- `/admin_login <工号> <密码>` - 管理员登录
- `/list_persons` - 查看人员列表
- `/list_groups` - 查看小组列表
- `/list_versions` - 查看版本列表
- `/list_tasks` - 查看任务列表

## 配置说明

创建 `.env` 文件并配置以下环境变量：

```bash
# 数据库配置
DATABASE_URL=sqlite:///data/opentmagent.db

# JWT配置 (必须修改)
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_HOURS=24

# 管理员密码最小长度
ADMIN_PASSWORD_MIN_LENGTH=6

# Telegram Bot (可选)
TELEGRAM_BOT_TOKEN=

# Ollama LLM配置 (可选)
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# 日志配置
LOG_LEVEL=INFO
DEBUG=true
```

## 运行测试

```bash
# 进入后端目录
cd backend

# 安装测试依赖
pip install pytest pytest-asyncio httpx

# 运行所有测试
python3 -m pytest tests/ -v

# 运行特定测试
python3 -m pytest tests/test_api.py -v

# 查看测试覆盖率
pip install pytest-cov
python3 -m pytest tests/ --cov=app
```

## API文档

启动后端服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

主要API端点：

```
认证:
POST /api/v1/auth/admin-login      # 管理员登录
POST /api/v1/auth/visitor-login    # 访客登录
GET  /api/v1/auth/me               # 获取当前用户

团队管理:
GET    /api/v1/persons             # 获取人员列表
POST   /api/v1/persons             # 创建人员
GET    /api/v1/persons/{id}        # 获取人员详情
PUT    /api/v1/persons/{id}        # 更新人员
DELETE /api/v1/persons/{id}        # 删除人员

项目管理:
GET    /api/v1/versions            # 获取版本列表
POST   /api/v1/versions             # 创建版本
GET    /api/v1/tasks               # 获取任务列表
POST   /api/v1/tasks               # 创建任务
GET    /api/v1/tasks/graph         # 获取任务关系图

架构档案:
GET    /api/v1/modules             # 获取模块列表
POST   /api/v1/modules             # 创建模块
GET    /api/v1/modules/mermaid     # 导出Mermaid图
```

## 项目结构

```
OpenTmAgent/
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── main.py            # FastAPI入口
│   │   ├── config.py          # 配置文件
│   │   ├── models/            # 数据库模型
│   │   ├── schemas/           # Pydantic模型
│   │   ├── api/               # API路由
│   │   ├── services/          # 业务逻辑
│   │   └── telegram_bot/      # Telegram Bot
│   ├── tests/                 # 测试代码
│   └── requirements.txt
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── views/             # 页面组件
│   │   ├── router/            # 路由配置
│   │   └── main.js
│   └── package.json
├── cli/                        # CLI工具
│   └── cli.py
├── docker-compose.yml          # Docker编排
├── Dockerfile                  # Docker镜像
├── nginx.conf                  # Nginx配置
├── spec.md                     # 技术规格文档
└── README.md                   # 本文档
```

## 常见问题

### 1. 后端启动失败

```bash
# 检查Python版本
python3 --version  # 需要3.9+

# 重新安装依赖
pip3 install -r backend/requirements.txt --force-reinstall
```

### 2. 前端启动失败

```bash
# 检查Node.js版本
node --version  # 需要18+

# 清除缓存重新安装
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### 3. 数据库初始化

```bash
# 数据库会在首次启动时自动创建
# 如需重置，删除数据库文件
rm -f data/opentmagent.db
```

### 4. Docker部署问题

```bash
# 查看容器日志
docker-compose logs opentmagent

# 重新构建镜像
docker-compose build --no-cache
docker-compose up -d
```

## 许可证

MIT License
