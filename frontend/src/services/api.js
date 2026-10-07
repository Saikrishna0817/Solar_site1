// API service layer — toggles between mock data and live FastAPI backend
// Set USE_MOCK=true for development without backend, false for live data

import { enrichedSites } from '../data/mockSites';
import stateData from '../data/stateData';

const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false'; // Default: mock mode
// Live mode is opt-in: VITE_USE_MOCK=false (see .env.example).
export const isLive = !USE_MOCK;
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const delay = (ms = 300) => new Promise(resolve => setTimeout(resolve, ms));

// ─── Mock Implementations ─────────────────────────────────
const mockApi = {
  async getSites(filters = {}) {
    await delay(200);
    let sites = [...enrichedSites];
    if (filters.state) sites = sites.filter(s => s.state === filters.state);
    if (filters.minSuitability) sites = sites.filter(s => s.suitability >= filters.minSuitability);
    return { data: sites, total: sites.length };
  },

  async getSiteById(id) {
    await delay(150);
    const site = enrichedSites.find(s => s.id === Number(id));
    if (!site) throw new Error('Site not found');
    return { data: site };
  },

  async getStates() {
    await delay(100);
    return { data: stateData };
  },

  async analyzeSite(lat, lng) {
    await delay(500);
    const nearest = enrichedSites.reduce((best, site) => {
      const dist = Math.sqrt(Math.pow(site.lat - lat, 2) + Math.pow(site.lng - lng, 2));
      const bestDist = Math.sqrt(Math.pow(best.lat - lat, 2) + Math.pow(best.lng - lng, 2));
      return dist < bestDist ? site : best;
    });
    return { data: nearest };
  },

  // No trained model behind the mock backend — never invent attributions.
  async getSiteShap() {
    throw new Error('SHAP requires the live backend');
  },
};

// ─── Live API Implementations ─────────────────────────────
const liveApi = {
  async getSites(filters = {}) {
    const params = new URLSearchParams();
    if (filters.state) params.set('state', filters.state);
    if (filters.minSuitability) params.set('min_suitability', filters.minSuitability);
    if (filters.limit) params.set('limit', String(filters.limit || 200));
    if (filters.searchQuery) params.set('search', filters.searchQuery);
    const res = await fetch(`${API_BASE}/v1/sites?${params}`);
    if (!res.ok) throw new Error(`Failed to fetch sites: ${res.status}`);
    const data = await res.json();
    return { data, total: data.length };
  },

  async getSiteById(id) {
    const res = await fetch(`${API_BASE}/v1/sites/${encodeURIComponent(id)}`);
    if (!res.ok) throw new Error(`Site not found: ${res.status}`);
    return { data: await res.json() };
  },

  async getStates() {
    const res = await fetch(`${API_BASE}/v1/states`);
    if (!res.ok) throw new Error('Failed to fetch states');
    return { data: await res.json() };
  },

  async analyzeSite(lat, lng) {
    const res = await fetch(`${API_BASE}/v1/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ latitude: lat, longitude: lng }),
    });
    if (!res.ok) throw new Error(`Prediction failed: ${res.status}`);
    return { data: await res.json() };
  },

  // GET /v1/sites/{district}/shap → { district, model, kind, baseline, values }
  // 404/503 when the trained model is unavailable — surfaced as a rejected promise.
  async getSiteShap(district) {
    const res = await fetch(`${API_BASE}/v1/sites/${encodeURIComponent(district)}/shap`);
    if (!res.ok) throw new Error(`SHAP unavailable: ${res.status}`);
    return { data: await res.json() };
  },
};

const api = USE_MOCK ? mockApi : liveApi;
export default api;
