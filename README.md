# Personal Travel Assistant - 个人形象旅行智能体

打通「个人形象管理」与「旅行规划」的全链路智能体——从衣橱管理、行程规划到内容创作，形成闭环。

## 技术栈

- **前端**：React + TypeScript（Vite）
- **后端**：Python FastAPI + SQLAlchemy + SQLite
- **测试**：pytest
- **CI**：GitHub Actions

## 项目结构

```
/
├── backend/           # FastAPI 后端
│   ├── app/
│   │   ├── main.py    # FastAPI 入口
│   │   ├── config.py  # 配置
│   │   ├── models/    # 数据模型
│   │   └── api/       # API 路由
│   └── tests/          # 测试
├── frontend/          # React 前端
│   └── src/
└── .github/
    └── workflows/
        └── ci.yml     # CI 配置
```

## 快速开始

### 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## 模块

1. **衣橱 + 天气穿搭**：衣物管理、AI 穿搭推荐
2. **旅行规划 + 交通**：行程生成、交通比价、每日穿搭
3. **虚拟形象 + 内容**：照片精修、文案模板、Vlog 脚本
