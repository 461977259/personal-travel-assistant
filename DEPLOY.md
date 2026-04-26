# Personal Travel Assistant - Deployment Guide

## 本地部署

### 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

启动后访问 `http://localhost:8000/health` 验证服务状态。

### 前端

```bash
cd frontend
npm install
npm run dev
```

生产构建：

```bash
cd frontend
npm install
npm run build
```

产物在 `frontend/dist/` 目录，可通过 Nginx 静态托管或部署至 Vercel/Netlify。

---

## 生产环境建议

| 组件 | 建议方案 |
|------|----------|
| 后端 | Gunicorn + Nginx 或 Docker 容器化 |
| 前端 | Vercel / Netlify 静态部署 |
| 数据库 | SQLite（初期）→ PostgreSQL（用户量上来后） |
| HTTPS | Nginx 反向代理或云负载均衡 |

---

## 环境变量

在 `backend/` 目录下创建 `.env` 文件：

```bash
# 和风天气 API（天气查询）
HEFENG_WEATHER_KEY=your_key

# 高德地图 API（地理编码/路径规划）
AMAP_KEY=your_key

# 飞猪旅行 API（待注册）
FLIGGY_KEY=your_key

# 腾讯云 CI（图片处理，待注册）
TENCENT_CI_SECRET_ID=your_id
TENCENT_CI_SECRET_KEY=your_key

# 数据库连接
DATABASE_URL=sqlite:///./data.db
```

> **注意：** 请勿将 `.env` 文件提交至版本控制系统。建议使用 `.env.example` 模板文件管理。

---

## Docker 部署（可选）

如需容器化部署，可参考以下 `Dockerfile` 示例：

```dockerfile
# backend/Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
```

---

## 目录结构

```
personal-travel-assistant/
├── backend/          # FastAPI 后端
│   ├── app/
│   │   ├── main.py  # 应用入口
│   │   └── ...
│   ├── tests/        # 单元测试
│   ├── requirements.txt
│   └── .env          # 环境变量（不提交）
├── frontend/         # React + TypeScript 前端
│   ├── src/
│   ├── dist/         # 构建产物
│   └── package.json
├── DEPLOY.md         # 本文档
└── README.md
```
