const BASE_URL = 'http://localhost:8000';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

// Wardrobe
export interface WardrobeItem {
  id: number;
  image_url?: string;
  type: string;
  color: string;
  thickness: string;
  scene: string;
  tags?: string[];
  created_at?: string;
}

export const wardrobeApi = {
  list: () => request<WardrobeItem[]>('/api/wardrobe/items'),
  add: (data: FormData) =>
    fetch(`${BASE_URL}/api/wardrobe/items`, { method: 'POST', body: data }),
  delete: (id: number) =>
    request<void>(`/api/wardrobe/items/${id}`, { method: 'DELETE' }),
};

// Outfit
export interface OutfitRecommendParams {
  city: string;
  scene: string;
  date?: string;
}

export interface OutfitRecommendResponse {
  recommendation_id?: string;
  items: Array<{
    id: number;
    type: string;
    color: string;
    reason: string;
  }>;
  reason: string;
}

export const outfitApi = {
  recommend: (params: OutfitRecommendParams) =>
    request<OutfitRecommendResponse>(
      `/api/outfit/recommend?city=${encodeURIComponent(params.city)}&scene=${encodeURIComponent(params.scene)}${params.date ? `&date=${params.date}` : ''}`
    ),
  confirm: (data: { recommendation_id?: string; items: number[]; city: string; scene: string }) =>
    request<{ success: boolean }>('/api/outfit/confirm', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};

// Trip
export interface TripGenerateParams {
  destination: string;
  days: number;
  start_date: string;
}

export interface TripDay {
  day: number;
  date: string;
  activities: Array<{
    time: string;
    activity: string;
    location: string;
    transportation?: string;
    outfit?: string;
  }>;
  outfit: string;
}

export interface TripResponse {
  trip_id: string;
  destination: string;
  days: TripDay[];
}

export const tripApi = {
  generate: (data: TripGenerateParams) =>
    request<TripResponse>('/api/trip/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  get: (id: string) => request<TripResponse>(`/api/trip/${id}`),
  save: (id: string) =>
    request<{ success: boolean }>(`/api/trip/${id}/save`, { method: 'POST' }),
};

// Copywriting
export interface CopywritingGenerateParams {
  photo_url?: string;
  style: string;
  platform: string;
}

export interface CopywritingResponse {
  content: string;
}

export const copywritingApi = {
  generate: (data: CopywritingGenerateParams) =>
    request<CopywritingResponse>('/api/copywriting/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  getStyles: () => request<{ styles: string[] }>('/api/copywriting/styles'),
};

// Health
export const healthApi = {
  check: () => request<{ status: string }>('/health'),
};
