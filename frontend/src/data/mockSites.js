// DEMO DATA — 11 invented sites in Telangana + Andhra Pradesh (the project's
// only scope), used by the map, dashboard and results table. This file is NOT
// our dataset and NOT model output: the real training set is the 13 CEA plants
// with actual CUF in Telangana + Andhra Pradesh (KEY_METRICS in constants.js),
// which are never loaded here.
// Every per-site value below — suitability, confidence, lcoe, npv,
// paybackYears, ghi/dni, capacity, featureScores — is a hand-written or
// formula-derived display value for the UI, never a model prediction.

const generateMonthlyGeneration = (ghi, capacity) => {
  // Monthly solar generation profile for Indian locations (MWh)
  const monthlyFactors = [0.85, 0.90, 0.95, 1.00, 0.98, 0.75, 0.60, 0.65, 0.80, 0.92, 0.88, 0.82];
  const baseGeneration = ghi * capacity * 0.18 * 30; // simplified
  return monthlyFactors.map((f, i) => ({
    month: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][i],
    generation: Math.round(baseGeneration * f),
    irradiance: Math.round(ghi * f * 100) / 100,
  }));
};

const generateYearlyProjection = (initialGeneration, years = 25) => {
  const degradation = 0.005; // 0.5% annual degradation
  return Array.from({ length: years }, (_, i) => ({
    year: 2025 + i,
    generation: Math.round(initialGeneration * Math.pow(1 - degradation, i)),
    cumulative: Math.round(initialGeneration * ((1 - Math.pow(1 - degradation, i + 1)) / degradation)),
  }));
};

export const mockSites = [
  // Telangana
  { id: 11, name: 'Mahbubnagar Solar', state: 'Telangana', district: 'Mahbubnagar', lat: 16.7488, lng: 77.9855, suitability: 0.83, ghi: 5.38, dni: 5.08, capacity: 100, landType: 'Barren', elevation: 440, slope: 2.5, gridDistance: 10, roadDistance: 3.8, temperature: 28.0, humidity: 48, windSpeed: 2.5, rainfall: 620, lcoe: 2.42, npv: 510, paybackYears: 6.3, confidence: 0.85 },
  { id: 12, name: 'Adilabad Plateau', state: 'Telangana', district: 'Adilabad', lat: 19.6640, lng: 78.5320, suitability: 0.76, ghi: 5.18, dni: 4.85, capacity: 75, landType: 'Rocky', elevation: 380, slope: 3.5, gridDistance: 15, roadDistance: 6.0, temperature: 27.5, humidity: 52, windSpeed: 2.2, rainfall: 850, lcoe: 2.58, npv: 380, paybackYears: 7.2, confidence: 0.80 },
  { id: 13, name: 'Nalgonda Solar', state: 'Telangana', district: 'Nalgonda', lat: 17.0575, lng: 79.2672, suitability: 0.80, ghi: 5.30, dni: 5.00, capacity: 80, landType: 'Agricultural (Fallow)', elevation: 310, slope: 1.8, gridDistance: 8, roadDistance: 3.5, temperature: 28.2, humidity: 50, windSpeed: 2.4, rainfall: 680, lcoe: 2.48, npv: 450, paybackYears: 6.8, confidence: 0.83 },
  { id: 14, name: 'Medak Solar Hub', state: 'Telangana', district: 'Medak', lat: 18.0462, lng: 78.2624, suitability: 0.78, ghi: 5.22, dni: 4.92, capacity: 60, landType: 'Scrubland', elevation: 520, slope: 2.2, gridDistance: 12, roadDistance: 4.5, temperature: 27.0, humidity: 55, windSpeed: 2.0, rainfall: 750, lcoe: 2.55, npv: 400, paybackYears: 7.0, confidence: 0.82 },
  { id: 15, name: 'Warangal East', state: 'Telangana', district: 'Warangal', lat: 17.9784, lng: 79.5941, suitability: 0.74, ghi: 5.12, dni: 4.78, capacity: 50, landType: 'Agricultural (Fallow)', elevation: 280, slope: 2.8, gridDistance: 14, roadDistance: 5.5, temperature: 28.5, humidity: 58, windSpeed: 2.1, rainfall: 900, lcoe: 2.62, npv: 350, paybackYears: 7.5, confidence: 0.78 },
  { id: 41, name: 'Karimnagar Solar', state: 'Telangana', district: 'Karimnagar', lat: 18.4386, lng: 79.1288, suitability: 0.77, ghi: 5.20, dni: 4.88, capacity: 65, landType: 'Scrubland', elevation: 260, slope: 2.0, gridDistance: 11, roadDistance: 4.5, temperature: 28.0, humidity: 55, windSpeed: 2.2, rainfall: 820, lcoe: 2.56, npv: 390, paybackYears: 7.0, confidence: 0.81 },
  { id: 42, name: 'Nizamabad Solar', state: 'Telangana', district: 'Nizamabad', lat: 18.6725, lng: 78.0940, suitability: 0.75, ghi: 5.15, dni: 4.82, capacity: 55, landType: 'Agricultural (Fallow)', elevation: 380, slope: 2.5, gridDistance: 13, roadDistance: 5.0, temperature: 27.5, humidity: 52, windSpeed: 2.0, rainfall: 880, lcoe: 2.60, npv: 360, paybackYears: 7.3, confidence: 0.79 },

  // Andhra Pradesh
  { id: 19, name: 'Kurnool Ultra Mega', state: 'Andhra Pradesh', district: 'Kurnool', lat: 15.8281, lng: 78.0373, suitability: 0.90, ghi: 5.62, dni: 5.32, capacity: 1000, landType: 'Barren', elevation: 350, slope: 1.0, gridDistance: 4, roadDistance: 2.0, temperature: 28.5, humidity: 42, windSpeed: 3.0, rainfall: 550, lcoe: 2.20, npv: 780, paybackYears: 5.5, confidence: 0.90 },
  { id: 20, name: 'Anantapur Solar', state: 'Andhra Pradesh', district: 'Anantapur', lat: 14.6819, lng: 77.6006, suitability: 0.87, ghi: 5.55, dni: 5.25, capacity: 200, landType: 'Semi-arid', elevation: 340, slope: 1.5, gridDistance: 9, roadDistance: 3.5, temperature: 28.2, humidity: 40, windSpeed: 2.8, rainfall: 520, lcoe: 2.30, npv: 650, paybackYears: 5.8, confidence: 0.88 },
  { id: 21, name: 'Kadapa Solar Zone', state: 'Andhra Pradesh', district: 'Kadapa', lat: 14.4747, lng: 78.8242, suitability: 0.82, ghi: 5.35, dni: 5.05, capacity: 120, landType: 'Rocky', elevation: 280, slope: 2.5, gridDistance: 12, roadDistance: 5.0, temperature: 28.8, humidity: 45, windSpeed: 2.5, rainfall: 650, lcoe: 2.44, npv: 500, paybackYears: 6.4, confidence: 0.85 },
  { id: 39, name: 'NP Kunta Solar', state: 'Andhra Pradesh', district: 'Anantapur', lat: 14.8700, lng: 77.4500, suitability: 0.89, ghi: 5.58, dni: 5.28, capacity: 1500, landType: 'Barren', elevation: 320, slope: 0.8, gridDistance: 5, roadDistance: 2.5, temperature: 28.0, humidity: 38, windSpeed: 3.0, rainfall: 480, lcoe: 2.22, npv: 760, paybackYears: 5.4, confidence: 0.89 },
];

// Enrich sites with computed data
// ponytail: featureScores are mock display heuristics (formulas over the mock
// site fields), not model output — the environmental axis used to be
// Math.random(), so the radar changed on every reload; it is now deterministic
// in rainfall like its siblings. Upgrade path: read real per-category scores
// from the backend (/v1/sites/{district}) and drop this block.
export const enrichedSites = mockSites.map(site => ({
  ...site,
  annualGeneration: Math.round(site.ghi * site.capacity * 0.18 * 365),
  monthlyGeneration: generateMonthlyGeneration(site.ghi, site.capacity),
  yearlyProjection: generateYearlyProjection(Math.round(site.ghi * site.capacity * 0.18 * 365)),
  featureScores: {
    solar: Math.min(1, site.ghi / 5.8),
    terrain: Math.max(0, 1 - site.slope / 8),
    land: site.landType === 'Desert' || site.landType === 'Barren' ? 0.9 : site.landType === 'Wasteland' ? 0.8 : 0.6,
    infrastructure: Math.max(0, 1 - site.gridDistance / 30),
    climate: Math.max(0, 1 - (site.humidity - 20) / 80),
    environmental: Math.max(0, 1 - site.rainfall / 4000),
    grid: Math.max(0, 1 - site.gridDistance / 25),
    economic: Math.min(1, 3.0 / site.lcoe),
  },
}));

export default enrichedSites;
