import { useState } from 'react';
import { tripApi, type TripResponse } from '../api/client';
import Loading from '../components/Loading';

export default function Trip() {
  const [destination, setDestination] = useState('');
  const [days, setDays] = useState(3);
  const [startDate, setStartDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<TripResponse | null>(null);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!destination.trim() || !startDate) return;
    setLoading(true);
    setError('');
    setResult(null);
    setSaved(false);
    try {
      const data = await tripApi.generate({
        destination: destination.trim(),
        days,
        start_date: startDate,
      });
      setResult(data);
    } catch {
      setError('生成行程失败，请检查后端服务');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!result) return;
    setLoading(true);
    try {
      await tripApi.save(result.trip_id);
      setSaved(true);
    } catch {
      setError('保存失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page trip-page">
      <div className="page-header">
        <h2>🗺️ 行程规划</h2>
      </div>

      <form className="card form-card" onSubmit={handleGenerate}>
        <div className="form-row">
          <div className="form-group">
            <label>目的地</label>
            <input
              type="text"
              placeholder="如：杭州、成都、东京"
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label>天数</label>
            <input
              type="number"
              min={1}
              max={15}
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
            />
          </div>
          <div className="form-group">
            <label>出发日期</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              required
            />
          </div>
        </div>
        <button className="btn btn-primary" type="submit" disabled={loading}>
          {loading && !result ? '生成中...' : '🗺️ 生成行程'}
        </button>
      </form>

      {error && <div className="error-msg">{error}</div>}
      {loading && !result && <Loading text="AI 规划中..." />}

      {result && (
        <div className="trip-result">
          <div className="trip-header">
            <h3>📍 {result.destination} 行程</h3>
            {!saved ? (
              <button className="btn btn-success" onClick={handleSave} disabled={loading}>
                💾 保存行程
              </button>
            ) : (
              <span className="success-msg">已保存 ✓</span>
            )}
          </div>
          {result.days.map((day) => (
            <div key={day.day} className="card trip-day-card">
              <div className="day-title">
                Day {day.day} · {day.date}
              </div>
              <div className="activities">
                {day.activities.map((act, idx) => (
                  <div key={idx} className="activity-item">
                    <span className="activity-time">{act.time}</span>
                    <div className="activity-content">
                      <strong>{act.activity}</strong>
                      <span className="activity-location">📍 {act.location}</span>
                      {act.transportation && (
                        <span className="activity-transport">🚗 {act.transportation}</span>
                      )}
                      {act.outfit && (
                        <span className="activity-outfit">👔 {act.outfit}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              {day.outfit && (
                <div className="day-outfit">
                  <span>👔 今日穿搭：</span>{day.outfit}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
