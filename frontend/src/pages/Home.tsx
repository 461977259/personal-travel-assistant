import { Link } from 'react-router-dom';
import { healthApi } from '../api/client';
import { useEffect, useState } from 'react';

const features = [
  {
    path: '/wardrobe',
    icon: '👔',
    title: '智能衣橱',
    desc: '上传衣物照片，AI 自动打标签，管理你的每日穿搭',
    color: '#e8f4fd',
    accent: '#1976d2',
  },
  {
    path: '/outfit',
    icon: '✨',
    title: '穿搭推荐',
    desc: '根据目的地天气与场景，智能推荐当日穿搭方案',
    color: '#fdf3e8',
    accent: '#e65100',
  },
  {
    path: '/trip',
    icon: '🗺️',
    title: '行程规划',
    desc: '输入目的地与天数，一键生成完整旅行计划与穿搭建议',
    color: '#e8f5e9',
    accent: '#2e7d32',
  },
  {
    path: '/content',
    icon: '📸',
    title: '内容创作',
    desc: '上传旅行照片，AI 生成各平台风格的精美文案',
    color: '#f3e8fd',
    accent: '#7b1fa2',
  },
];

export default function Home() {
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    healthApi.check().then((r) => setStatus(r.status)).catch(() => setStatus('offline'));
  }, []);

  return (
    <div className="page home-page">
      <div className="home-header">
        <h1>🧳 个人形象旅行智能体</h1>
        <p className="home-subtitle">
          智能衣橱管理 · 穿搭推荐 · 行程规划 · 内容创作
        </p>
        <div className="status-badge">
          后端状态：
          <span className={`status-dot ${status === 'ok' ? 'online' : status === 'offline' ? 'offline' : 'checking'}`} />
          {status ?? '检测中'}
        </div>
      </div>

      <div className="feature-grid">
        {features.map((f) => (
          <Link key={f.path} to={f.path} className="feature-card" style={{ background: f.color }}>
            <div className="feature-icon">{f.icon}</div>
            <h3 style={{ color: f.accent }}>{f.title}</h3>
            <p>{f.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
