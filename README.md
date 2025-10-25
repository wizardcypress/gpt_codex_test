# US Market Dashboard

该项目提供一个简洁的 Web 服务，用于展示美股纳斯达克指数、标普 500 指数以及当日涨幅前 100 的股票信息。数据通过 Yahoo Finance 公共接口定期抓取并存储到本地数据库中，Web 端直接查询数据库展示最新结果。

## 功能特性

- 后台定时任务定期抓取美股指数和当日涨幅 Top 100 股票。
- 通过 SQLite 数据库存储历史快照。
- Flask Web 服务提供简洁的仪表盘页面。
- 提供独立脚本支持手动刷新数据。

## 环境准备

1. 创建虚拟环境并安装依赖：

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. 如需自定义数据库或刷新周期，可通过环境变量进行配置：

   - `DATABASE_URL`：数据库连接串，默认 `sqlite:///market_data.db`
   - `REFRESH_MINUTES`：Web 服务启动后定时任务的执行间隔（分钟），默认 `15`

## 获取数据快照

在启动 Web 服务前，可手动抓取一次数据以便页面展示：

```bash
python scripts/refresh_data.py
```

## 启动 Web 服务

使用 Flask 内置服务器启动：

```bash
flask --app wsgi run
```

启动后访问 [http://127.0.0.1:5000](http://127.0.0.1:5000) 查看页面。

> **提示**：在生产环境中请使用更可靠的 WSGI 服务器（如 gunicorn）托管应用。

## 项目结构

```
├── app
│   ├── __init__.py          # Flask 应用工厂
│   ├── database.py          # SQLAlchemy 会话和初始化
│   ├── fetcher.py           # 数据抓取与入库逻辑
│   ├── models.py            # 数据模型定义
│   ├── routes.py            # Web 路由
│   ├── scheduler.py         # 定时任务配置
│   ├── static
│   │   └── styles.css       # 自定义样式
│   └── templates
│       └── index.html       # 仪表盘模板
├── requirements.txt
├── scripts
│   └── refresh_data.py      # 手动刷新脚本
└── wsgi.py                  # 入口文件
```
