// Mock Solar Sites Data — 50 representative sites across India
// Each site has realistic feature values derived from the 42-feature schema

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

const generateSHAPValues = () => {
  const features = [
    { feature: 'GHI (kWh/m²/day)', value: (Math.random() * 0.3 + 0.1).toFixed(3) },
    { feature: 'Grid Distance (km)', value: (Math.random() * 0.2 - 0.1).toFixed(3) },
    { feature: 'Slope (°)', value: -(Math.random() * 0.15).toFixed(3) },
    { feature: 'Land Availability', value: (Math.random() * 0.18 + 0.02).toFixed(3) },
    { feature: 'Temperature (°C)', value: -(Math.random() * 0.08).toFixed(3) },
    { feature: 'Road Distance (km)', value: -(Math.random() * 0.12).toFixed(3) },
    { feature: 'DNI (kWh/m²/day)', value: (Math.random() * 0.22 + 0.05).toFixed(3) },
    { feature: 'Sunshine Hours', value: (Math.random() * 0.16 + 0.04).toFixed(3) },
    { feature: 'Substation Capacity', value: (Math.random() * 0.14).toFixed(3) },
    { feature: 'Policy Incentives', value: (Math.random() * 0.1 + 0.02).toFixed(3) },
    { feature: 'Dust Index', value: -(Math.random() * 0.07).toFixed(3) },
    { feature: 'Humidity (%)', value: -(Math.random() * 0.06).toFixed(3) },
  ];
  return features.sort((a, b) => Math.abs(b.value) - Math.abs(a.value));
};

export const mockSites = [
  // Rajasthan — Premier solar belt
  { id: 1, name: 'Bhadla Solar Park', state: 'Rajasthan', district: 'Jodhpur', lat: 27.5394, lng: 71.9101, suitability: 0.94, ghi: 5.72, dni: 5.45, capacity: 250, landType: 'Desert', elevation: 220, slope: 1.2, gridDistance: 8, roadDistance: 3.5, temperature: 28.5, humidity: 25, windSpeed: 4.2, rainfall: 280, lcoe: 2.15, npv: 850, paybackYears: 5.2, confidence: 0.92 },
  { id: 2, name: 'Jaisalmer West', state: 'Rajasthan', district: 'Jaisalmer', lat: 26.9157, lng: 70.9083, suitability: 0.91, ghi: 5.65, dni: 5.38, capacity: 180, landType: 'Desert', elevation: 225, slope: 0.8, gridDistance: 12, roadDistance: 5.0, temperature: 29.1, humidity: 22, windSpeed: 4.5, rainfall: 210, lcoe: 2.22, npv: 720, paybackYears: 5.5, confidence: 0.90 },
  { id: 3, name: 'Barmer Solar Zone', state: 'Rajasthan', district: 'Barmer', lat: 25.7521, lng: 71.3967, suitability: 0.89, ghi: 5.58, dni: 5.30, capacity: 200, landType: 'Desert', elevation: 190, slope: 1.5, gridDistance: 15, roadDistance: 6.2, temperature: 29.8, humidity: 28, windSpeed: 3.8, rainfall: 250, lcoe: 2.28, npv: 680, paybackYears: 5.8, confidence: 0.88 },
  { id: 4, name: 'Bikaner North', state: 'Rajasthan', district: 'Bikaner', lat: 28.0229, lng: 73.3119, suitability: 0.87, ghi: 5.50, dni: 5.22, capacity: 150, landType: 'Semi-arid', elevation: 242, slope: 1.0, gridDistance: 10, roadDistance: 4.0, temperature: 27.8, humidity: 30, windSpeed: 3.5, rainfall: 300, lcoe: 2.35, npv: 620, paybackYears: 6.0, confidence: 0.87 },
  { id: 5, name: 'Fatehgarh Solar', state: 'Rajasthan', district: 'Jaisalmer', lat: 27.3584, lng: 71.0324, suitability: 0.92, ghi: 5.68, dni: 5.42, capacity: 300, landType: 'Desert', elevation: 208, slope: 0.6, gridDistance: 6, roadDistance: 2.8, temperature: 28.9, humidity: 24, windSpeed: 4.0, rainfall: 220, lcoe: 2.18, npv: 810, paybackYears: 5.3, confidence: 0.91 },

  // Gujarat — Strong solar state
  { id: 6, name: 'Charanka Solar Park', state: 'Gujarat', district: 'Patan', lat: 23.8991, lng: 71.2005, suitability: 0.88, ghi: 5.52, dni: 5.18, capacity: 345, landType: 'Wasteland', elevation: 58, slope: 0.5, gridDistance: 5, roadDistance: 2.0, temperature: 27.2, humidity: 35, windSpeed: 3.2, rainfall: 450, lcoe: 2.32, npv: 750, paybackYears: 5.6, confidence: 0.89 },
  { id: 7, name: 'Kutch Solar Zone', state: 'Gujarat', district: 'Kutch', lat: 23.7337, lng: 69.8597, suitability: 0.90, ghi: 5.60, dni: 5.35, capacity: 200, landType: 'Barren', elevation: 45, slope: 0.3, gridDistance: 18, roadDistance: 8.5, temperature: 27.8, humidity: 30, windSpeed: 5.1, rainfall: 350, lcoe: 2.25, npv: 690, paybackYears: 5.7, confidence: 0.88 },
  { id: 8, name: 'Banaskantha Solar', state: 'Gujarat', district: 'Banaskantha', lat: 24.1705, lng: 72.4367, suitability: 0.82, ghi: 5.35, dni: 5.05, capacity: 120, landType: 'Semi-arid', elevation: 130, slope: 1.8, gridDistance: 12, roadDistance: 4.5, temperature: 26.5, humidity: 38, windSpeed: 2.8, rainfall: 520, lcoe: 2.45, npv: 480, paybackYears: 6.5, confidence: 0.85 },
  { id: 9, name: 'Rajkot West', state: 'Gujarat', district: 'Rajkot', lat: 22.3039, lng: 70.8022, suitability: 0.79, ghi: 5.28, dni: 4.95, capacity: 100, landType: 'Wasteland', elevation: 128, slope: 2.0, gridDistance: 8, roadDistance: 3.0, temperature: 27.0, humidity: 42, windSpeed: 3.0, rainfall: 580, lcoe: 2.52, npv: 420, paybackYears: 6.8, confidence: 0.83 },
  { id: 10, name: 'Dholera SIR Solar', state: 'Gujarat', district: 'Ahmedabad', lat: 22.2481, lng: 72.1930, suitability: 0.85, ghi: 5.42, dni: 5.12, capacity: 500, landType: 'Industrial', elevation: 5, slope: 0.2, gridDistance: 3, roadDistance: 1.5, temperature: 27.5, humidity: 45, windSpeed: 4.5, rainfall: 650, lcoe: 2.38, npv: 580, paybackYears: 6.2, confidence: 0.86 },

  // Telangana — Target study area
  { id: 11, name: 'Mahbubnagar Solar', state: 'Telangana', district: 'Mahbubnagar', lat: 16.7488, lng: 77.9855, suitability: 0.83, ghi: 5.38, dni: 5.08, capacity: 100, landType: 'Barren', elevation: 440, slope: 2.5, gridDistance: 10, roadDistance: 3.8, temperature: 28.0, humidity: 48, windSpeed: 2.5, rainfall: 620, lcoe: 2.42, npv: 510, paybackYears: 6.3, confidence: 0.85 },
  { id: 12, name: 'Adilabad Plateau', state: 'Telangana', district: 'Adilabad', lat: 19.6640, lng: 78.5320, suitability: 0.76, ghi: 5.18, dni: 4.85, capacity: 75, landType: 'Rocky', elevation: 380, slope: 3.5, gridDistance: 15, roadDistance: 6.0, temperature: 27.5, humidity: 52, windSpeed: 2.2, rainfall: 850, lcoe: 2.58, npv: 380, paybackYears: 7.2, confidence: 0.80 },
  { id: 13, name: 'Nalgonda Solar', state: 'Telangana', district: 'Nalgonda', lat: 17.0575, lng: 79.2672, suitability: 0.80, ghi: 5.30, dni: 5.00, capacity: 80, landType: 'Agricultural (Fallow)', elevation: 310, slope: 1.8, gridDistance: 8, roadDistance: 3.5, temperature: 28.2, humidity: 50, windSpeed: 2.4, rainfall: 680, lcoe: 2.48, npv: 450, paybackYears: 6.8, confidence: 0.83 },
  { id: 14, name: 'Medak Solar Hub', state: 'Telangana', district: 'Medak', lat: 18.0462, lng: 78.2624, suitability: 0.78, ghi: 5.22, dni: 4.92, capacity: 60, landType: 'Scrubland', elevation: 520, slope: 2.2, gridDistance: 12, roadDistance: 4.5, temperature: 27.0, humidity: 55, windSpeed: 2.0, rainfall: 750, lcoe: 2.55, npv: 400, paybackYears: 7.0, confidence: 0.82 },
  { id: 15, name: 'Warangal East', state: 'Telangana', district: 'Warangal', lat: 17.9784, lng: 79.5941, suitability: 0.74, ghi: 5.12, dni: 4.78, capacity: 50, landType: 'Agricultural (Fallow)', elevation: 280, slope: 2.8, gridDistance: 14, roadDistance: 5.5, temperature: 28.5, humidity: 58, windSpeed: 2.1, rainfall: 900, lcoe: 2.62, npv: 350, paybackYears: 7.5, confidence: 0.78 },

  // Tamil Nadu
  { id: 16, name: 'Ramanathapuram Solar', state: 'Tamil Nadu', district: 'Ramanathapuram', lat: 9.3762, lng: 78.8308, suitability: 0.86, ghi: 5.48, dni: 5.15, capacity: 150, landType: 'Wasteland', elevation: 15, slope: 0.5, gridDistance: 6, roadDistance: 2.5, temperature: 29.0, humidity: 55, windSpeed: 5.5, rainfall: 850, lcoe: 2.35, npv: 600, paybackYears: 6.0, confidence: 0.87 },
  { id: 17, name: 'Sivaganga Solar', state: 'Tamil Nadu', district: 'Sivaganga', lat: 10.1263, lng: 78.5093, suitability: 0.81, ghi: 5.32, dni: 5.02, capacity: 100, landType: 'Barren', elevation: 105, slope: 1.5, gridDistance: 10, roadDistance: 4.0, temperature: 28.5, humidity: 52, windSpeed: 3.5, rainfall: 920, lcoe: 2.45, npv: 470, paybackYears: 6.5, confidence: 0.84 },
  { id: 18, name: 'Tirunelveli Solar', state: 'Tamil Nadu', district: 'Tirunelveli', lat: 8.7139, lng: 77.7567, suitability: 0.84, ghi: 5.40, dni: 5.10, capacity: 120, landType: 'Semi-arid', elevation: 85, slope: 1.2, gridDistance: 7, roadDistance: 3.0, temperature: 28.8, humidity: 50, windSpeed: 4.8, rainfall: 780, lcoe: 2.40, npv: 540, paybackYears: 6.2, confidence: 0.86 },

  // Andhra Pradesh
  { id: 19, name: 'Kurnool Ultra Mega', state: 'Andhra Pradesh', district: 'Kurnool', lat: 15.8281, lng: 78.0373, suitability: 0.90, ghi: 5.62, dni: 5.32, capacity: 1000, landType: 'Barren', elevation: 350, slope: 1.0, gridDistance: 4, roadDistance: 2.0, temperature: 28.5, humidity: 42, windSpeed: 3.0, rainfall: 550, lcoe: 2.20, npv: 780, paybackYears: 5.5, confidence: 0.90 },
  { id: 20, name: 'Anantapur Solar', state: 'Andhra Pradesh', district: 'Anantapur', lat: 14.6819, lng: 77.6006, suitability: 0.87, ghi: 5.55, dni: 5.25, capacity: 200, landType: 'Semi-arid', elevation: 340, slope: 1.5, gridDistance: 9, roadDistance: 3.5, temperature: 28.2, humidity: 40, windSpeed: 2.8, rainfall: 520, lcoe: 2.30, npv: 650, paybackYears: 5.8, confidence: 0.88 },
  { id: 21, name: 'Kadapa Solar Zone', state: 'Andhra Pradesh', district: 'Kadapa', lat: 14.4747, lng: 78.8242, suitability: 0.82, ghi: 5.35, dni: 5.05, capacity: 120, landType: 'Rocky', elevation: 280, slope: 2.5, gridDistance: 12, roadDistance: 5.0, temperature: 28.8, humidity: 45, windSpeed: 2.5, rainfall: 650, lcoe: 2.44, npv: 500, paybackYears: 6.4, confidence: 0.85 },

  // Karnataka
  { id: 22, name: 'Pavagada Solar Park', state: 'Karnataka', district: 'Tumkur', lat: 14.1014, lng: 77.2810, suitability: 0.88, ghi: 5.50, dni: 5.20, capacity: 2050, landType: 'Barren', elevation: 550, slope: 0.8, gridDistance: 5, roadDistance: 2.5, temperature: 26.5, humidity: 38, windSpeed: 3.2, rainfall: 480, lcoe: 2.28, npv: 720, paybackYears: 5.6, confidence: 0.89 },
  { id: 23, name: 'Bellary Solar', state: 'Karnataka', district: 'Bellary', lat: 15.1394, lng: 76.9214, suitability: 0.84, ghi: 5.42, dni: 5.12, capacity: 150, landType: 'Wasteland', elevation: 450, slope: 1.5, gridDistance: 8, roadDistance: 3.5, temperature: 27.5, humidity: 42, windSpeed: 2.8, rainfall: 550, lcoe: 2.38, npv: 580, paybackYears: 6.1, confidence: 0.86 },

  // Madhya Pradesh
  { id: 24, name: 'Rewa Ultra Mega', state: 'Madhya Pradesh', district: 'Rewa', lat: 24.5362, lng: 81.3037, suitability: 0.85, ghi: 5.45, dni: 5.15, capacity: 750, landType: 'Wasteland', elevation: 280, slope: 1.2, gridDistance: 6, roadDistance: 3.0, temperature: 26.0, humidity: 45, windSpeed: 2.5, rainfall: 1050, lcoe: 2.36, npv: 610, paybackYears: 6.0, confidence: 0.87 },
  { id: 25, name: 'Neemuch Solar', state: 'Madhya Pradesh', district: 'Neemuch', lat: 24.4735, lng: 74.8707, suitability: 0.83, ghi: 5.38, dni: 5.08, capacity: 200, landType: 'Semi-arid', elevation: 490, slope: 1.8, gridDistance: 14, roadDistance: 5.5, temperature: 25.5, humidity: 40, windSpeed: 2.2, rainfall: 850, lcoe: 2.42, npv: 520, paybackYears: 6.3, confidence: 0.85 },

  // Maharashtra
  { id: 26, name: 'Sakri Solar Park', state: 'Maharashtra', district: 'Dhule', lat: 20.9874, lng: 73.9930, suitability: 0.81, ghi: 5.30, dni: 5.00, capacity: 150, landType: 'Barren', elevation: 320, slope: 2.0, gridDistance: 10, roadDistance: 4.0, temperature: 27.0, humidity: 48, windSpeed: 2.5, rainfall: 650, lcoe: 2.48, npv: 460, paybackYears: 6.6, confidence: 0.84 },
  { id: 27, name: 'Latur Solar Zone', state: 'Maharashtra', district: 'Latur', lat: 18.4088, lng: 76.5604, suitability: 0.79, ghi: 5.25, dni: 4.95, capacity: 100, landType: 'Agricultural (Fallow)', elevation: 570, slope: 1.5, gridDistance: 12, roadDistance: 4.5, temperature: 27.5, humidity: 45, windSpeed: 2.2, rainfall: 750, lcoe: 2.52, npv: 420, paybackYears: 6.8, confidence: 0.82 },

  // Uttar Pradesh
  { id: 28, name: 'Mirzapur Solar', state: 'Uttar Pradesh', district: 'Mirzapur', lat: 25.1460, lng: 82.5690, suitability: 0.77, ghi: 5.20, dni: 4.88, capacity: 80, landType: 'Wasteland', elevation: 210, slope: 2.5, gridDistance: 15, roadDistance: 6.0, temperature: 26.5, humidity: 55, windSpeed: 2.0, rainfall: 1020, lcoe: 2.56, npv: 390, paybackYears: 7.0, confidence: 0.80 },
  { id: 29, name: 'Bundelkhand Solar', state: 'Uttar Pradesh', district: 'Jhansi', lat: 25.4484, lng: 78.5685, suitability: 0.78, ghi: 5.22, dni: 4.90, capacity: 120, landType: 'Barren', elevation: 248, slope: 1.8, gridDistance: 11, roadDistance: 4.8, temperature: 27.0, humidity: 50, windSpeed: 2.3, rainfall: 900, lcoe: 2.54, npv: 410, paybackYears: 6.9, confidence: 0.81 },

  // Punjab & Haryana
  { id: 30, name: 'Bathinda Solar', state: 'Punjab', district: 'Bathinda', lat: 30.2110, lng: 74.9455, suitability: 0.75, ghi: 5.15, dni: 4.82, capacity: 60, landType: 'Agricultural (Fallow)', elevation: 210, slope: 0.5, gridDistance: 8, roadDistance: 2.5, temperature: 25.0, humidity: 50, windSpeed: 2.5, rainfall: 450, lcoe: 2.60, npv: 360, paybackYears: 7.2, confidence: 0.79 },
  { id: 31, name: 'Hisar Solar Park', state: 'Haryana', district: 'Hisar', lat: 29.1492, lng: 75.7217, suitability: 0.76, ghi: 5.18, dni: 4.85, capacity: 80, landType: 'Semi-arid', elevation: 215, slope: 0.8, gridDistance: 7, roadDistance: 3.0, temperature: 25.5, humidity: 45, windSpeed: 3.0, rainfall: 400, lcoe: 2.58, npv: 380, paybackYears: 7.1, confidence: 0.80 },

  // Odisha
  { id: 32, name: 'Kalahandi Solar', state: 'Odisha', district: 'Kalahandi', lat: 19.9069, lng: 83.1763, suitability: 0.72, ghi: 5.05, dni: 4.72, capacity: 50, landType: 'Wasteland', elevation: 360, slope: 3.0, gridDistance: 18, roadDistance: 7.5, temperature: 27.0, humidity: 60, windSpeed: 2.0, rainfall: 1350, lcoe: 2.68, npv: 310, paybackYears: 7.8, confidence: 0.76 },

  // Chhattisgarh
  { id: 33, name: 'Korba Solar Zone', state: 'Chhattisgarh', district: 'Korba', lat: 22.3595, lng: 82.7501, suitability: 0.70, ghi: 4.98, dni: 4.65, capacity: 40, landType: 'Scrubland', elevation: 290, slope: 2.8, gridDistance: 16, roadDistance: 6.5, temperature: 27.5, humidity: 62, windSpeed: 1.8, rainfall: 1200, lcoe: 2.72, npv: 280, paybackYears: 8.0, confidence: 0.75 },

  // Jharkhand
  { id: 34, name: 'Hazaribagh Solar', state: 'Jharkhand', district: 'Hazaribagh', lat: 23.9926, lng: 85.3637, suitability: 0.68, ghi: 4.92, dni: 4.58, capacity: 35, landType: 'Rocky', elevation: 615, slope: 3.5, gridDistance: 20, roadDistance: 8.0, temperature: 25.0, humidity: 58, windSpeed: 2.2, rainfall: 1250, lcoe: 2.78, npv: 250, paybackYears: 8.5, confidence: 0.73 },

  // Bihar
  { id: 35, name: 'Nawada Solar', state: 'Bihar', district: 'Nawada', lat: 24.8868, lng: 85.5413, suitability: 0.65, ghi: 4.85, dni: 4.50, capacity: 30, landType: 'Agricultural (Fallow)', elevation: 72, slope: 0.5, gridDistance: 22, roadDistance: 9.0, temperature: 26.0, humidity: 65, windSpeed: 1.5, rainfall: 1100, lcoe: 2.85, npv: 220, paybackYears: 9.0, confidence: 0.70 },

  // Additional Rajasthan sites
  { id: 36, name: 'Pokhran Solar', state: 'Rajasthan', district: 'Jaisalmer', lat: 26.9200, lng: 71.9200, suitability: 0.93, ghi: 5.70, dni: 5.44, capacity: 280, landType: 'Desert', elevation: 280, slope: 0.5, gridDistance: 7, roadDistance: 3.0, temperature: 29.5, humidity: 20, windSpeed: 4.8, rainfall: 190, lcoe: 2.16, npv: 840, paybackYears: 5.2, confidence: 0.91 },
  { id: 37, name: 'Sam Solar Zone', state: 'Rajasthan', district: 'Jaisalmer', lat: 26.8800, lng: 70.5600, suitability: 0.90, ghi: 5.62, dni: 5.36, capacity: 150, landType: 'Desert', elevation: 200, slope: 0.8, gridDistance: 20, roadDistance: 10.0, temperature: 30.0, humidity: 18, windSpeed: 5.2, rainfall: 180, lcoe: 2.25, npv: 700, paybackYears: 5.7, confidence: 0.89 },

  // Additional Gujarat
  { id: 38, name: 'Bhuj Solar Park', state: 'Gujarat', district: 'Kutch', lat: 23.2494, lng: 69.6669, suitability: 0.86, ghi: 5.48, dni: 5.18, capacity: 200, landType: 'Barren', elevation: 75, slope: 0.5, gridDistance: 10, roadDistance: 4.0, temperature: 28.0, humidity: 32, windSpeed: 5.0, rainfall: 380, lcoe: 2.35, npv: 610, paybackYears: 5.9, confidence: 0.87 },

  // Additional AP
  { id: 39, name: 'NP Kunta Solar', state: 'Andhra Pradesh', district: 'Anantapur', lat: 14.8700, lng: 77.4500, suitability: 0.89, ghi: 5.58, dni: 5.28, capacity: 1500, landType: 'Barren', elevation: 320, slope: 0.8, gridDistance: 5, roadDistance: 2.5, temperature: 28.0, humidity: 38, windSpeed: 3.0, rainfall: 480, lcoe: 2.22, npv: 760, paybackYears: 5.4, confidence: 0.89 },

  // Additional Karnataka
  { id: 40, name: 'Raichur Solar', state: 'Karnataka', district: 'Raichur', lat: 16.2120, lng: 77.3439, suitability: 0.82, ghi: 5.35, dni: 5.05, capacity: 100, landType: 'Wasteland', elevation: 380, slope: 1.5, gridDistance: 9, roadDistance: 3.5, temperature: 28.0, humidity: 45, windSpeed: 2.5, rainfall: 600, lcoe: 2.44, npv: 490, paybackYears: 6.4, confidence: 0.85 },

  // Additional Telangana
  { id: 41, name: 'Karimnagar Solar', state: 'Telangana', district: 'Karimnagar', lat: 18.4386, lng: 79.1288, suitability: 0.77, ghi: 5.20, dni: 4.88, capacity: 65, landType: 'Scrubland', elevation: 260, slope: 2.0, gridDistance: 11, roadDistance: 4.5, temperature: 28.0, humidity: 55, windSpeed: 2.2, rainfall: 820, lcoe: 2.56, npv: 390, paybackYears: 7.0, confidence: 0.81 },
  { id: 42, name: 'Nizamabad Solar', state: 'Telangana', district: 'Nizamabad', lat: 18.6725, lng: 78.0940, suitability: 0.75, ghi: 5.15, dni: 4.82, capacity: 55, landType: 'Agricultural (Fallow)', elevation: 380, slope: 2.5, gridDistance: 13, roadDistance: 5.0, temperature: 27.5, humidity: 52, windSpeed: 2.0, rainfall: 880, lcoe: 2.60, npv: 360, paybackYears: 7.3, confidence: 0.79 },

  // Additional MP
  { id: 43, name: 'Shajapur Solar', state: 'Madhya Pradesh', district: 'Shajapur', lat: 23.4328, lng: 76.2770, suitability: 0.80, ghi: 5.28, dni: 4.98, capacity: 150, landType: 'Barren', elevation: 435, slope: 1.5, gridDistance: 10, roadDistance: 4.0, temperature: 26.0, humidity: 42, windSpeed: 2.5, rainfall: 900, lcoe: 2.50, npv: 440, paybackYears: 6.7, confidence: 0.83 },

  // Additional Tamil Nadu
  { id: 44, name: 'Thoothukudi Solar', state: 'Tamil Nadu', district: 'Thoothukudi', lat: 8.7642, lng: 78.1348, suitability: 0.85, ghi: 5.45, dni: 5.12, capacity: 180, landType: 'Semi-arid', elevation: 10, slope: 0.3, gridDistance: 5, roadDistance: 2.0, temperature: 29.5, humidity: 58, windSpeed: 6.0, rainfall: 650, lcoe: 2.36, npv: 560, paybackYears: 6.1, confidence: 0.86 },

  // Additional Maharashtra
  { id: 45, name: 'Solapur Solar', state: 'Maharashtra', district: 'Solapur', lat: 17.6599, lng: 75.9064, suitability: 0.80, ghi: 5.28, dni: 4.98, capacity: 80, landType: 'Semi-arid', elevation: 480, slope: 1.2, gridDistance: 8, roadDistance: 3.5, temperature: 28.0, humidity: 42, windSpeed: 2.8, rainfall: 580, lcoe: 2.50, npv: 440, paybackYears: 6.7, confidence: 0.83 },

  // West Bengal (low solar but included for coverage)
  { id: 46, name: 'Purulia Solar', state: 'West Bengal', district: 'Purulia', lat: 23.3337, lng: 86.3650, suitability: 0.62, ghi: 4.78, dni: 4.42, capacity: 25, landType: 'Rocky', elevation: 250, slope: 3.0, gridDistance: 20, roadDistance: 8.0, temperature: 26.0, humidity: 65, windSpeed: 2.0, rainfall: 1350, lcoe: 2.92, npv: 190, paybackYears: 9.5, confidence: 0.68 },

  // Kerala (coastal, limited)
  { id: 47, name: 'Kasaragod Solar', state: 'Kerala', district: 'Kasaragod', lat: 12.4996, lng: 74.9869, suitability: 0.58, ghi: 4.65, dni: 4.30, capacity: 20, landType: 'Agricultural (Fallow)', elevation: 30, slope: 2.5, gridDistance: 15, roadDistance: 5.0, temperature: 28.0, humidity: 75, windSpeed: 3.5, rainfall: 3500, lcoe: 3.05, npv: 150, paybackYears: 10.0, confidence: 0.65 },

  // Uttarakhand (hilly)
  { id: 48, name: 'Dehradun Solar', state: 'Uttarakhand', district: 'Dehradun', lat: 30.3165, lng: 78.0322, suitability: 0.55, ghi: 4.55, dni: 4.20, capacity: 15, landType: 'Rocky', elevation: 640, slope: 5.0, gridDistance: 12, roadDistance: 4.0, temperature: 22.0, humidity: 60, windSpeed: 2.5, rainfall: 2050, lcoe: 3.15, npv: 120, paybackYears: 11.0, confidence: 0.62 },

  // Himachal Pradesh
  { id: 49, name: 'Spiti Valley Solar', state: 'Himachal Pradesh', district: 'Lahaul Spiti', lat: 32.5790, lng: 78.0350, suitability: 0.72, ghi: 5.08, dni: 4.95, capacity: 10, landType: 'Barren', elevation: 3860, slope: 4.0, gridDistance: 35, roadDistance: 15.0, temperature: 5.0, humidity: 25, windSpeed: 4.0, rainfall: 450, lcoe: 2.70, npv: 300, paybackYears: 7.8, confidence: 0.75 },

  // Assam (NE India)
  { id: 50, name: 'Guwahati Solar', state: 'Assam', district: 'Kamrup', lat: 26.1445, lng: 91.7362, suitability: 0.52, ghi: 4.42, dni: 4.05, capacity: 15, landType: 'Agricultural (Fallow)', elevation: 55, slope: 1.5, gridDistance: 10, roadDistance: 3.0, temperature: 25.0, humidity: 78, windSpeed: 1.5, rainfall: 1700, lcoe: 3.25, npv: 100, paybackYears: 12.0, confidence: 0.60 },
];

// Enrich sites with computed data
export const enrichedSites = mockSites.map(site => ({
  ...site,
  annualGeneration: Math.round(site.ghi * site.capacity * 0.18 * 365),
  monthlyGeneration: generateMonthlyGeneration(site.ghi, site.capacity),
  yearlyProjection: generateYearlyProjection(Math.round(site.ghi * site.capacity * 0.18 * 365)),
  shapValues: generateSHAPValues(),
  featureScores: {
    solar: Math.min(1, site.ghi / 5.8),
    terrain: Math.max(0, 1 - site.slope / 8),
    land: site.landType === 'Desert' || site.landType === 'Barren' ? 0.9 : site.landType === 'Wasteland' ? 0.8 : 0.6,
    infrastructure: Math.max(0, 1 - site.gridDistance / 30),
    climate: Math.max(0, 1 - (site.humidity - 20) / 80),
    environmental: 0.7 + Math.random() * 0.25,
    grid: Math.max(0, 1 - site.gridDistance / 25),
    economic: Math.min(1, 3.0 / site.lcoe),
  },
}));

export default enrichedSites;
