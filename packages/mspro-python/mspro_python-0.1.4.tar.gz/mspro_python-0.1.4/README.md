# MsPro - FastAPI 异步项目通用脚手架

MsPro 是一个基于 **FastAPI 异步框架**
的通用项目脚手架，旨在帮助开发者快速构建具备健壮架构和可扩展性的后端服务。它内置标准开发模块（CRUD、数据模型、路由、数据结构）与企业级最佳实践，让你从繁杂的基础构建中解放出来，专注于业务逻辑。

---

## ✨ 项目亮点

- 🚀 **异步架构**：基于 FastAPI 异步框架，支持高并发处理。
- 🧱 **模块化结构**：标准化目录，包含 `crud/`、`models/`、`routes/`、`schemas/` 等核心模块。
- 🔒 **JWT 鉴权体系**：内置安全的 Token 授权与用户认证机制。
- 🧬 **SQLModel 数据建模**：采用 SQLModel 统一 ORM 模型与 Pydantic Schema。
- 📦 **Pydantic V2.0 支持**：新一代数据校验体系，更快更强。
- 🔄 **全面强大的 CRUD 函数**：支持列表/分页/模糊查询（like/in/between等）及聚合（count/max/avg等）操作。
- 📊 **日志跟踪系统**：基于 Python `logging` 优化配置，便于调试和生产环境日志分析。
- ⚙️ **代码生成器**：基于模型定义，可一键生成整套 CRUD + Routes + Schemas。
- 🧰 **丰富的工具函数**：包含随机数、UUID、时间戳转换、统一格式响应等实用工具。
- ⏱️ **Celery 异步任务队列**：内建延迟任务处理机制，适用于邮件、通知等场景。
- 📧 **支持邮件发送**：集成邮件服务，可结合延迟队列实现定时/异步发送。
- 🛠️ **一键管理脚本**：集成本地测试、开发部署、依赖更新、日志查看等一键管理命令。
- 📂 **CI/CD支持**：基于Gitlab CI/CD的自动化部署脚本，支持一键部署到生产环境。

---

## 📂 项目结构总览

```
MsPro/
├── alembic/                # 数据库升级/迁移
├── app/
│   ├── crud/               # CURD 操作
│   ├── models/             # SQLModel 模型定义
│   ├── routes/             # 路由入口
│   ├── schemas/            # Pydantic 数据结构
│   ├── tasks/              # 异步任务调度
│   ├── utils/              # 工具函数
│   └── main.py             # FastAPI 应用入口
├── logs/                   # 日志目录
├── module_generator.py     # 模型生成脚本
├── manage.sh               # 本地/部署环境一键控制脚本
├── .gitlab-ci.yml          # Gitlab CI/CD 配置
├── .env                    # 环境变量配置
├── alembic.ini             # Alembic 配置文件
├── requirements.txt        # 依赖列表
└── README.md
```

---

## 📦 安装方式

### 方式一：通过 pip 安装并初始化项目

```bash
pip install mspro-python
mspro-init my_project
```

这将会在当前目录下生成名为 `my_project/` 的完整项目脚手架。

---

## 🔧 使用指南

1. 配置一键管理脚本manage.sh，.env及Gitlab CI/CD（可选）:
   1. 调整manage.sh配置
   ```bash
    # ==================== 配置区域 ====================
    SERVICE_NAME="service_name"  # systemd 服务名称
    APP_MODULE="app.main:app"   # FastAPI 应用模块:对象，比如 app/main.py -> app
    HOST="0.0.0.0"
    PORT="8030"
    WORKERS=4
    VENV_DIR="venv"             # 虚拟环境目录，相对路径
    RELOAD_DIR="app"            # 热重载监听的目录
    REQUIREMENTS_FILE="requirements.txt"  # 项目依赖组织文件名，相对路径
    CELERY_MODULE="app.tasks.celery_task"  # Celery 应用模块路径，未设置则跳过 Celery 控制
    # ==================================================
    ```
    2. 添加权限
    ```bash
    chmod +x manage.sh
    ```
    3. 查看脚本帮助
    ```bash
    ./manage.sh
    ```
    4. 将.env.example 重命名为 .env 并根据实际情况修改配置，本地开发使用
    5. 如果需要使用 Gitlab CI/CD 自动化部署，请确保 `.gitlab-ci.yml` 文件已正确配置。
    ```bash
    # 1. .gitlab-ci.yml.example重命名为 .gitlab-ci.yml 并根据实际情况修改配置
    # 2. 将.env文件内容配置到 Gitlab CI/CD 的环境变量ENV_FILE中，在CI/CD初始构建时会动态生成，用于生产环境
    ```

2. 安装依赖（本地环境）：

```bash
cd my_project
python -m venv venv
./manage.sh setup
```

3. 启动服务（本地环境）：

```bash
./manage.sh test
```

4. 使用 `module_generator.py` 自动生成模块：
    1. 创建对应数据模型app/models/Demo.py
    2. 执行命令生成模块文件
    ```bash
    # 2.执行命令生成模块文件
    python module_generator.py Demo
    ```

5. 生产环境部署/运维：
    1. 通过SFTP或CI/CD上传项目文件
    2. SFTP方式，文件上传后，使用如下指令
    ```bash
    # 部署
    ./manage.sh build
    # 运维
    ./manage.sh start/stop/restart/upgrade
    ```
    3. CI/CD方式，确保 `.gitlab-ci.yml` 文件已正确配置，提交代码后自动触发部署。

---

## 📚 未来规划（TODO）

- 增加部署 Dockerfile 支持
- 提供 PostgreSQL、SQLite、mongodb 切换配置

---

## 🧑‍💻 作者

由 [JENA] 设计与维护。欢迎提交 issue 与 PR 一起共建开源生态。

---

## 📄 License

本项目遵循 MIT License，详见 [LICENSE](LICENSE) 文件。
