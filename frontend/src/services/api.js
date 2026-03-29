// API service layer with mock data toggle
// Set USE_MOCK=false in .env to switch to live API calls

import { enrichedSites } from '../data/mockSites';
import stateData from '../data/stateData';

const USE_MOCK = true; // Toggle for mock vs live API
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Simulated API delay
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
    // Find nearest mock site
    const nearest = enrichedSites.reduce((best, site) => {
      const dist = Math.sqrt(Math.pow(site.lat - lat, 2) + Math.pow(site.lng - lng, 2));
      const bestDist = Math.sqrt(Math.pow(best.lat - lat, 2) + Math.pow(best.lng - lng, 2));
      return dist < bestDist ? site : best;
    });
    return { data: nearest };
  },
};

// ─── Live API Implementations ─────────────────────────────
const liveApi = {
  async getSites(filters = {}) {
    const params = new URLSearchParams(filters);
    const res = await fetch(`${API_BASE}/utility/sites?${params}`);
    if (!res.ok) throw new Error('Failed to fetch sites');
    return res.json();
  },

  async getSiteById(id) {
    const res = await fetch(`${API_BASE}/utility/site/${id}`);
    if (!res.ok) throw new Error('Failed to fetch site');
    return res.json();
  },

  async getStates() {
    const res = await fetch(`${API_BASE}/states`);
    if (!res.ok) throw new Error('Failed to fetch states');
    return res.json();
  },

  async analyzeSite(lat, lng) {
    const res = await fetch(`${API_BASE}/utility/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ latitude: lat, longitude: lng }),
    });
    if (!res.ok) throw new Error('Failed to analyze site');
    return res.json();
  },
};

// Export the selected API implementation
const api = USE_MOCK ? mockApi : liveApi;
export default api;
