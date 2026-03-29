// SolarSite-India Constants & Configuration

// ─── Color Scales ──────────────────────────────────────────
export const SUITABILITY_COLORS = {
  excellent: '#10B981',   // > 0.8
  good: '#F5A623',        // 0.6 - 0.8
  moderate: '#D97706',    // 0.4 - 0.6
  poor: '#EF4444',        // < 0.4
};

export const getSuitabilityColor = (score) => {
  if (score >= 0.8) return '#10B981';
  if (score >= 0.6) return '#F5A623';
  if (score >= 0.4) return '#D97706';
  return '#EF4444';
};

export const getSuitabilityLabel = (score) => {
  if (score >= 0.8) return 'Excellent';
  if (score >= 0.6) return 'Good';
  if (score >= 0.4) return 'Moderate';
  return 'Poor';
};

export const GHI_COLOR_SCALE = [
  { value: 3.5, color: '#1E3A5F' },
  { value: 4.0, color: '#2A6B9C' },
  { value: 4.5, color: '#F5A623' },
  { value: 5.0, color: '#E8590C' },
  { value: 5.5, color: '#DC2626' },
  { value: 6.0, color: '#FF0040' },
];

// ─── Feature Categories ────────────────────────────────────
export const FEATURE_CATEGORIES = [
  { key: 'solar', label: 'Solar Resource', icon: '☀️', color: '#F5A623', features: ['ghi', 'dni', 'sunshine_hours', 'solar_variability', 'peak_sun_hours'] },
  { key: 'terrain', label: 'Terrain', icon: '⛰️', color: '#14B8A6', features: ['slope', 'elevation', 'aspect', 'terrain_roughness', 'flood_risk'] },
  { key: 'land', label: 'Land Use', icon: '🏗️', color: '#8B5CF6', features: ['land_type', 'land_availability', 'soil_type', 'vegetation_index', 'land_cost'] },
  { key: 'infrastructure', label: 'Infrastructure', icon: '🔌', color: '#3B82F6', features: ['grid_distance', 'substation_capacity', 'road_distance', 'road_quality', 'water_distance'] },
  { key: 'climate', label: 'Climate', icon: '🌡️', color: '#06B6D4', features: ['temperature', 'humidity', 'wind_speed', 'rainfall', 'dust_index'] },
  { key: 'environmental', label: 'Environmental', icon: '🌿', color: '#10B981', features: ['protected_area', 'forest_cover', 'water_body', 'wildlife_corridor', 'environmental_sensitivity'] },
  { key: 'grid', label: 'Grid', icon: '⚡', color: '#E8590C', features: ['grid_stability', 'transmission_loss', 'demand_center_distance', 'grid_congestion', 'evacuation_capacity'] },
  { key: 'economic', label: 'Economic', icon: '💰', color: '#D97706', features: ['tariff_rate', 'policy_incentives', 'labor_availability', 'local_economy', 'investment_climate'] },
];

// ─── Chart Colors ──────────────────────────────────────────
export const CHART_COLORS = {
  primary: '#F5A623',
  secondary: '#06B6D4',
  tertiary: '#8B5CF6',
  quaternary: '#10B981',
  accent: '#E8590C',
  grid: 'rgba(30, 58, 82, 0.3)',
  text: '#8BA8BF',
  background: '#0D1B2A',
};

// ─── Map Config ────────────────────────────────────────────
export const MAP_CONFIG = {
  center: [20.5937, 78.9629], // India center
  zoom: 5,
  minZoom: 4,
  maxZoom: 18,
  tileUrl: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
  tileAttribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>',
};

// ─── States of India ───────────────────────────────────────
export const INDIAN_STATES = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
  'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand',
  'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
  'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
  'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
  'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
];

// ─── Land Types ────────────────────────────────────────────
export const LAND_TYPES = [
  'Barren', 'Wasteland', 'Agricultural (Fallow)', 'Semi-arid',
  'Desert', 'Scrubland', 'Industrial', 'Rocky',
];

// ─── Key Metrics ───────────────────────────────────────────
export const KEY_METRICS = {
  targetGW: 500,
  sitesAnalyzed: 30000,
  buildingsAssessed: 300000000,
  modelAccuracy: 0.88,
  mapeScore: 11.5,
  featuresUsed: 42,
  statesCovered: 28,
  trainingPlants: 127,
};

// ─── Ensemble Model Weights ───────────────────────────────
export const MODEL_WEIGHTS = {
  randomForest: 0.30,
  xgboost: 0.50,
  gradientBoosting: 0.20,
};

// ─── Navigation Links ─────────────────────────────────────
export const NAV_LINKS = [
  { path: '/', label: 'Home' },
  { path: '/dashboard', label: 'Dashboard' },
  { path: '/analyze', label: 'Analyze' },
  { path: '/methodology', label: 'Methodology' },
  { path: '/results', label: 'Results' },
  { path: '/about', label: 'About' },
];
