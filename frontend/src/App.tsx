import { useState, useEffect } from 'react'

interface HealthResponse {
  status: string
}

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null)

  useEffect(() => {
    fetch('/api/health')
      .then(res => res.json())
      .then(data => setHealth(data))
      .catch(() => setHealth({ status: 'error' }))
  }, [])

  return (
    <div style={{ padding: '2rem', fontFamily: 'system-ui, sans-serif' }}>
      <h1>🧳 个人形象旅行智能体</h1>
      <p>Personal Travel Assistant - MVP</p>
      <div style={{ marginTop: '1rem', padding: '1rem', background: '#f5f5f5', borderRadius: '8px' }}>
        <strong>后端状态：</strong>
        {health ? (
          <span style={{ color: health.status === 'ok' ? 'green' : 'red' }}>
            {health.status}
          </span>
        ) : (
          <span>检查中...</span>
        )}
      </div>
      <div style={{ marginTop: '2rem' }}>
        <h2>模块概览</h2>
        <ul>
          <li>👔 模块1：衣橱 + 天气穿搭推荐</li>
          <li>🗺️ 模块2：旅行规划 + 交通 + 穿搭</li>
          <li>📸 模块3：虚拟形象 + 内容模板</li>
        </ul>
      </div>
    </div>
  )
}

export default App
