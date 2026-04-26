import { useState, useEffect, useRef } from 'react';
import { wardrobeApi, type WardrobeItem } from '../api/client';
import Loading from '../components/Loading';

const CLOTHING_TYPES = ['T恤', '衬衫', '外套', '裤子', '裙子', '鞋子', '配饰'];
const COLORS = ['白色', '黑色', '灰色', '蓝色', '红色', '绿色', '黄色', '粉色', '棕色', '其他'];
const THICKNESSES = ['薄款', '常规', '厚款'];
const SCENES = ['日常', '工作', '旅行', '运动', '约会', '正式'];

export default function Wardrobe() {
  const [items, setItems] = useState<WardrobeItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [filterType, setFilterType] = useState('');
  const [showForm, setShowForm] = useState(false);

  // Form state
  const [type, setType] = useState('T恤');
  const [color, setColor] = useState('白色');
  const [thickness, setThickness] = useState('常规');
  const [scene, setScene] = useState('日常');
  const [photo, setPhoto] = useState<File | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const fetchItems = async () => {
    setLoading(true);
    try {
      const data = await wardrobeApi.list();
      setItems(data);
    } catch {
      console.error('Failed to fetch wardrobe items');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('type', type);
      formData.append('color', color);
      formData.append('thickness', thickness);
      formData.append('scene', scene);
      if (photo) formData.append('photo', photo);
      await wardrobeApi.add(formData);
      setShowForm(false);
      setPhoto(null);
      if (fileRef.current) fileRef.current.value = '';
      fetchItems();
    } catch (err) {
      console.error('Failed to add item:', err);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await wardrobeApi.delete(id);
      fetchItems();
    } catch (err) {
      console.error('Failed to delete:', err);
    }
  };

  const filtered = filterType ? items.filter((i) => i.type === filterType) : items;

  return (
    <div className="page wardrobe-page">
      <div className="page-header">
        <h2>👔 智能衣橱</h2>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? '取消添加' : '+ 添加衣物'}
        </button>
      </div>

      {showForm && (
        <form className="card form-card" onSubmit={handleSubmit}>
          <h3>添加新衣物</h3>
          <div className="form-grid">
            <div className="form-group">
              <label>衣物照片</label>
              <input
                ref={fileRef}
                type="file"
                accept="image/*"
                onChange={(e) => setPhoto(e.target.files?.[0] || null)}
              />
            </div>
            <div className="form-group">
              <label>类型</label>
              <select value={type} onChange={(e) => setType(e.target.value)}>
                {CLOTHING_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>颜色</label>
              <select value={color} onChange={(e) => setColor(e.target.value)}>
                {COLORS.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>厚度</label>
              <select value={thickness} onChange={(e) => setThickness(e.target.value)}>
                {THICKNESSES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>场景</label>
              <select value={scene} onChange={(e) => setScene(e.target.value)}>
                {SCENES.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
          </div>
          <button className="btn btn-primary" type="submit" disabled={uploading}>
            {uploading ? '上传中...' : '确认添加'}
          </button>
        </form>
      )}

      <div className="filter-bar">
        <span>筛选：</span>
        <button
          className={`filter-chip ${filterType === '' ? 'active' : ''}`}
          onClick={() => setFilterType('')}
        >
          全部
        </button>
        {CLOTHING_TYPES.map((t) => (
          <button
            key={t}
            className={`filter-chip ${filterType === t ? 'active' : ''}`}
            onClick={() => setFilterType(t)}
          >
            {t}
          </button>
        ))}
      </div>

      {loading ? (
        <Loading text="加载衣橱中..." />
      ) : filtered.length === 0 ? (
        <div className="empty-state">
          <p>暂无衣物，快去添加吧！</p>
        </div>
      ) : (
        <div className="wardrobe-grid">
          {filtered.map((item) => (
            <div key={item.id} className="wardrobe-card card">
              {item.image_url ? (
                <img src={item.image_url} alt={item.type} className="wardrobe-img" />
              ) : (
                <div className="wardrobe-img-placeholder">👔</div>
              )}
              <div className="wardrobe-info">
                <div className="wardrobe-tags">
                  <span className="tag">{item.type}</span>
                  <span className="tag">{item.color}</span>
                  <span className="tag">{item.thickness}</span>
                  <span className="tag">{item.scene}</span>
                </div>
                {item.tags && item.tags.length > 0 && (
                  <div className="wardrobe-tags">
                    {item.tags.map((tag) => (
                      <span key={tag} className="tag tag-ai">{tag}</span>
                    ))}
                  </div>
                )}
              </div>
              <button className="btn btn-danger btn-sm" onClick={() => handleDelete(item.id)}>
                删除
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
