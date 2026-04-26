import { useState, useEffect } from 'react';
import { copywritingApi } from '../api/client';
import Loading from '../components/Loading';

const STYLES = ['文艺', '活泼', '简约', '攻略型'];
const PLATFORMS = [
  { value: '朋友圈', label: '朋友圈' },
  { value: '小红书', label: '小红书' },
  { value: '抖音', label: '抖音' },
];

export default function Content() {
  const [photoUrl, setPhotoUrl] = useState('');
  const [style, setStyle] = useState('文艺');
  const [platform, setPlatform] = useState('朋友圈');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState('');
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    copywritingApi.getStyles().then((r) => {
      if (r.styles && r.styles.length > 0) setStyle(r.styles[0]);
    }).catch(() => {});
  }, []);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult('');
    setCopied(false);
    try {
      const data = await copywritingApi.generate({
        photo_url: photoUrl.trim() || undefined,
        style,
        platform,
      });
      setResult(data.content);
    } catch {
      setError('生成失败，请检查后端服务');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(result).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="page content-page">
      <div className="page-header">
        <h2>📸 内容创作</h2>
      </div>

      <form className="card form-card" onSubmit={handleGenerate}>
        <div className="form-group">
          <label>照片链接（可选）</label>
          <input
            type="url"
            placeholder="https://example.com/photo.jpg"
            value={photoUrl}
            onChange={(e) => setPhotoUrl(e.target.value)}
          />
        </div>
        <div className="form-row">
          <div className="form-group">
            <label>文案风格</label>
            <select value={style} onChange={(e) => setStyle(e.target.value)}>
              {STYLES.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>发布平台</label>
            <select value={platform} onChange={(e) => setPlatform(e.target.value)}>
              {PLATFORMS.map((p) => (
                <option key={p.value} value={p.value}>{p.label}</option>
              ))}
            </select>
          </div>
        </div>
        <button className="btn btn-primary" type="submit" disabled={loading}>
          {loading ? '生成中...' : '✍️ 生成文案'}
        </button>
      </form>

      {error && <div className="error-msg">{error}</div>}
      {loading && !result && <Loading text="AI 创作中..." />}

      {result && (
        <div className="card result-card">
          <div className="result-header">
            <h3>✍️ 生成结果</h3>
            <button className={`btn btn-sm ${copied ? 'btn-success' : 'btn-secondary'}`} onClick={handleCopy}>
              {copied ? '已复制 ✓' : '📋 一键复制'}
            </button>
          </div>
          <div className="copywriting-content">{result}</div>
        </div>
      )}
    </div>
  );
}
