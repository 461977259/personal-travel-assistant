# SPEC.md - Personal Travel Assistant

> 项目规格文档（飞书源：https://www.feishu.cn/docx/Y2MKdkDPdonkMcxEocwcDPkknth）

## 1. 项目概述

**一句话描述：** 打通「个人形象管理」与「旅行规划」的全链路智能体。

**核心价值：** 用户输入「目的地 + 天数」，系统自动输出每日穿搭（基于已有衣橱）+ 行程路径 + 交通方案 + 发布内容。

**适用场景：** 国内出行（境内旅游、商务出差、周边短途）

## 2. 技术栈

- 前端：React + TypeScript（Vite）
- 后端：Python FastAPI + SQLAlchemy + SQLite
- 测试：pytest
- CI：GitHub Actions

## 3. 数据模型

### 3.1 WardrobeItem（衣橱）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | PK |
| name | String | 衣物名称 |
| category | String | 类型：outerwear/top/bottom/shoes/accessory |
| color | String | 颜色 |
| thickness | String | 厚度：thin/medium/thick/extra_thick |
| scene | String | 场景：commute/casual/business/sports/formal/travel |
| image_url | Text | 照片URL |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### 3.2 UserPreference（用户偏好）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | PK |
| user_id | String | 用户ID（唯一） |
| body_type | String | 体型 |
| style_preference | String | 风格偏好 |
| color_preference | String | 颜色偏好 |
| clothing_size | String | 服装尺码 |
| common_scenes | String | 常用场景 |

### 3.3 Trip（行程）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | PK |
| user_id | String | 用户ID |
| destination | String | 目的地 |
| start_date | DateTime | 开始日期 |
| end_date | DateTime | 结束日期 |
| days | Integer | 天数 |
| itinerary | JSON | 每日行程结构 |
| weather_summary | JSON | 天气汇总 |
| transportation | JSON | 交通方案 |
| daily_outfits | JSON | 每日穿搭 |
| total_cost | Float | 总花费 |
| notes | Text | 备注 |

### 3.4 Content（内容）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | PK |
| user_id | String | 用户ID |
| trip_id | Integer | FK → Trip |
| content_type | String | 类型：vlog_script/social_post/photo_diary |
| title | String | 标题 |
| body | Text | 正文 |
| style | String | 风格 |
| tags | String | 标签 |
| photos | JSON | 照片列表 |
| vlog_timestamps | JSON | Vlog 时间戳 |
| exported_text | Text | 导出文本 |

## 4. 第三方集成

| 类型 | 方案 | 说明 |
|------|------|------|
| 天气 | 和风天气 | 免费版每天1000次 |
| 交通 | 飞猪AI开放平台 | 机票/火车票/酒店/门票 |
| 地图 | 高德地图 API | POI/路径规划 |
| 图片处理 | 腾讯云数据万象 CI | 图片分类/精修/超分 |

## 5. 开发进度

- [x] 项目初始化（目录结构 + CI）
- [x] 后端基础框架（FastAPI + /health）
- [x] 数据模型（4张表）
- [ ] 衣橱管理 API
- [ ] 用户偏好 API
- [ ] 行程管理 API
- [ ] 内容管理 API
- [ ] 第三方集成（天气/地图/交通）
- [ ] 前端基础框架
- [ ] 前端衣橱页面
- [ ] 前端行程规划页面
- [ ] 前端内容创作页面
