import { useState } from 'react';
import { outfitApi, type OutfitRecommendResponse } from '../api/client';
import Loading from '../components/Loading';

const SCENES = ['日常', '工作', '旅行', '运动', '约会', '正式'];

export default function Outfit() {
  const [city, setCity] = useState('');
  const [scene, setScene] = useState('旅行');
  const [date, setDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<OutfitRecommendResponse | null>(null);
  const [confirmed, setConfirmed] = useState(false);
  const [error, setError] = useState('');

  const handleRecommend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!city.trim()) return;
    setLoading(true);
    setError('');
    setResult(null);
    setConfirmed(false);
    try {
      const data = await outfitApi.recommend({ city: city.trim(), scene, date: date || undefined });
      setResult(data);
    } catch (err) {
      setError('推荐失败，请检查后端服务');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async () => {
    if (!result) return;
    setLoading(true);
    try {
      await outfitApi.confirm({
        items: result.items.map((i) => i.id),
        city,
        scene,
      });
      setConfirmed(true);
    } catch {
      setError('确认失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page outfit-page">
      <div className="page-header">
        <h2>✨ 穿搭推荐</h2>
      </div>

      <form className="card form-card" onSubmit={handleRecommend}>
        <div className="form-row">
          <div className="form-group">
            <label>目的城市</label>
            <input
              type="text"
              placeholder="如：北京、上海、东京"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label>日期</label>
            <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
          </div>
          <div className="form-group">
            <label>场景</label>
            <select value={scene} onChange={(e) => setScene(e.target.value)}>
              {SCENES.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
        </div>
        <button className="btn btn-primary" type="submit" disabled={loading}>
          {loading && !result ? '推荐中...' : '🌟 推荐穿搭'}
        </button>
      </form>

      {error && <div className="error-msg">{error}</div>}

      {loading && !result && <Loading text="AI 搭配中..." />}

      {result && (
        <div className="card result-card">
          <h3>📋 推荐方案</h3>
          <p className="outfit-reason">{result.reason}</p>
          <div className="outfit-items">
            {result.items.map((item, idx) => (
              <div key={idx} className="outfit-item">
                <span className="outfit-item-icon">👔</span>
                <div>
                  <strong>{item.type}</strong>
                  <span> {item.color}</span>
                  <p className="outfit-item-reason">{item.reason}</p>
                </div>
              </div>
            ))}
          </div>
          {!confirmed ? (
            <button className="btn btn-success" onClick={handleConfirm} disabled={loading}>
              ✅ 确认穿搭
            </button>
          ) : (
            <div className="success-msg">✨ 穿搭已确认！</div>
          )}
        </div>
      )}
    </div>
  );
}
