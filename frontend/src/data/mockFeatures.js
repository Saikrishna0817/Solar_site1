// Illustrative feature catalog for the Methodology explorer — NOT the training
// schema. The trained model uses KEY_METRICS.featuresUsed (43) engineered
// columns from the processed feature table (avg_ghi_kwh_m2_day, elevation_m,
// dist_nearest_road_km, ...). The `importance` and `weight` fields below are
// hand-assigned display values, not model-derived importances.
// ponytail: catalog and training columns are maintained by hand in two places;
// ceiling = they drift apart silently. Upgrade path = generate this file from
// the feature table's header row in scripts/update_frontend_metrics.py.
export const featureDefinitions = [
  // Solar Resource (5)
  { id: 1, name: 'GHI', fullName: 'Global Horizontal Irradiance', unit: 'kWh/m²/day', category: 'solar', description: 'Total solar radiation on a horizontal surface', range: '3.5 - 6.0', importance: 'Critical', weight: 0.15 },
  { id: 2, name: 'DNI', fullName: 'Direct Normal Irradiance', unit: 'kWh/m²/day', category: 'solar', description: 'Direct beam radiation perpendicular to sun', range: '3.0 - 5.5', importance: 'Critical', weight: 0.12 },
  { id: 3, name: 'Sunshine Hours', fullName: 'Daily Sunshine Duration', unit: 'hours/day', category: 'solar', description: 'Average daily sunshine hours', range: '5 - 10', importance: 'High', weight: 0.08 },
  { id: 4, name: 'Solar Variability', fullName: 'Inter-annual Solar Variability', unit: '%', category: 'solar', description: 'Year-to-year variation in solar resource', range: '3 - 12', importance: 'Medium', weight: 0.04 },
  { id: 5, name: 'Peak Sun Hours', fullName: 'Peak Sun Hours', unit: 'hours', category: 'solar', description: 'Equivalent hours of peak sunshine (1000 W/m²)', range: '4 - 7', importance: 'High', weight: 0.06 },

  // Terrain (5)
  { id: 6, name: 'Slope', fullName: 'Terrain Slope', unit: '°', category: 'terrain', description: 'Ground slope angle', range: '0 - 15', importance: 'High', weight: 0.07 },
  { id: 7, name: 'Elevation', fullName: 'Elevation Above Sea Level', unit: 'm', category: 'terrain', description: 'Height above mean sea level', range: '0 - 4000', importance: 'Medium', weight: 0.03 },
  { id: 8, name: 'Aspect', fullName: 'Terrain Aspect', unit: '°', category: 'terrain', description: 'Direction the slope faces (south-facing preferred)', range: '0 - 360', importance: 'Medium', weight: 0.04 },
  { id: 9, name: 'Terrain Roughness', fullName: 'Surface Roughness Index', unit: 'index', category: 'terrain', description: 'Measure of terrain irregularity', range: '0 - 1', importance: 'Low', weight: 0.02 },
  { id: 10, name: 'Flood Risk', fullName: 'Flood Risk Assessment', unit: 'score', category: 'terrain', description: 'Risk of flooding at the site', range: '0 - 1', importance: 'High', weight: 0.05 },

  // Land Use (5)
  { id: 11, name: 'Land Type', fullName: 'Land Use Classification', unit: 'category', category: 'land', description: 'Primary land use type', range: '8 categories', importance: 'Critical', weight: 0.10 },
  { id: 12, name: 'Land Availability', fullName: 'Contiguous Land Area', unit: 'hectares', category: 'land', description: 'Available contiguous land for development', range: '5 - 5000', importance: 'High', weight: 0.08 },
  { id: 13, name: 'Soil Type', fullName: 'Foundation Soil Classification', unit: 'category', category: 'land', description: 'Soil bearing capacity for foundations', range: '6 types', importance: 'Medium', weight: 0.03 },
  { id: 14, name: 'Vegetation Index', fullName: 'NDVI Vegetation Index', unit: 'index', category: 'land', description: 'Normalized vegetation density', range: '0 - 0.8', importance: 'Medium', weight: 0.03 },
  { id: 15, name: 'Land Cost', fullName: 'Land Acquisition Cost', unit: '₹/hectare', category: 'land', description: 'Estimated land cost per hectare', range: '50K - 50L', importance: 'High', weight: 0.05 },

  // Infrastructure (5+2)
  { id: 16, name: 'Grid Distance', fullName: 'Distance to Nearest Grid', unit: 'km', category: 'infrastructure', description: 'Distance to nearest transmission line', range: '0 - 50', importance: 'Critical', weight: 0.09 },
  { id: 17, name: 'Substation Capacity', fullName: 'Nearest Substation Capacity', unit: 'MVA', category: 'infrastructure', description: 'Available capacity at nearest substation', range: '10 - 500', importance: 'High', weight: 0.06 },
  { id: 18, name: 'Road Distance', fullName: 'Distance to Nearest Road', unit: 'km', category: 'infrastructure', description: 'Distance to nearest paved road', range: '0 - 20', importance: 'Medium', weight: 0.04 },
  { id: 19, name: 'Road Quality', fullName: 'Access Road Quality', unit: 'score', category: 'infrastructure', description: 'Quality rating of access routes', range: '1 - 5', importance: 'Low', weight: 0.02 },
  { id: 20, name: 'Water Distance', fullName: 'Distance to Water Source', unit: 'km', category: 'infrastructure', description: 'Distance to water for panel cleaning', range: '0 - 15', importance: 'Medium', weight: 0.03 },
  { id: 21, name: 'Airport Distance', fullName: 'Distance to Nearest Airport', unit: 'km', category: 'infrastructure', description: 'Distance to nearest airport/airstrip', range: '0 - 200', importance: 'Low', weight: 0.01 },
  { id: 22, name: 'Port Distance', fullName: 'Distance to Nearest Port', unit: 'km', category: 'infrastructure', description: 'Distance for equipment import logistics', range: '0 - 500', importance: 'Low', weight: 0.01 },

  // Climate (5)
  { id: 23, name: 'Temperature', fullName: 'Mean Annual Temperature', unit: '°C', category: 'climate', description: 'Average annual temperature (affects panel efficiency)', range: '5 - 35', importance: 'High', weight: 0.05 },
  { id: 24, name: 'Humidity', fullName: 'Relative Humidity', unit: '%', category: 'climate', description: 'Average relative humidity (affects soiling)', range: '15 - 85', importance: 'Medium', weight: 0.03 },
  { id: 25, name: 'Wind Speed', fullName: 'Average Wind Speed', unit: 'm/s', category: 'climate', description: 'Average wind speed at 10m height', range: '1 - 8', importance: 'Medium', weight: 0.03 },
  { id: 26, name: 'Rainfall', fullName: 'Annual Rainfall', unit: 'mm', category: 'climate', description: 'Total annual precipitation', range: '150 - 4000', importance: 'Medium', weight: 0.04 },
  { id: 27, name: 'Dust Index', fullName: 'Atmospheric Dust Index', unit: 'index', category: 'climate', description: 'Dust/particulate matter affecting panel soiling', range: '0 - 1', importance: 'Medium', weight: 0.03 },

  // Environmental (5)
  { id: 28, name: 'Protected Area', fullName: 'Protected Area Proximity', unit: 'km', category: 'environmental', description: 'Distance from nearest protected/reserved area', range: '0 - 50', importance: 'High', weight: 0.05 },
  { id: 29, name: 'Forest Cover', fullName: 'Forest Cover Percentage', unit: '%', category: 'environmental', description: 'Forest cover within 5km radius', range: '0 - 80', importance: 'High', weight: 0.04 },
  { id: 30, name: 'Water Body', fullName: 'Water Body Proximity', unit: 'km', category: 'environmental', description: 'Distance from rivers, lakes, wetlands', range: '0 - 20', importance: 'Medium', weight: 0.03 },
  { id: 31, name: 'Wildlife Corridor', fullName: 'Wildlife Corridor Impact', unit: 'boolean', category: 'environmental', description: 'Whether site intersects wildlife corridors', range: '0/1', importance: 'High', weight: 0.04 },
  { id: 32, name: 'Env. Sensitivity', fullName: 'Environmental Sensitivity Index', unit: 'score', category: 'environmental', description: 'Composite environmental sensitivity score', range: '0 - 1', importance: 'High', weight: 0.05 },

  // Grid (5)
  { id: 33, name: 'Grid Stability', fullName: 'Grid Stability Index', unit: 'index', category: 'grid', description: 'Reliability of the local electrical grid', range: '0 - 1', importance: 'High', weight: 0.06 },
  { id: 34, name: 'Transmission Loss', fullName: 'Transmission & Distribution Loss', unit: '%', category: 'grid', description: 'Expected power loss in transmission', range: '5 - 30', importance: 'Medium', weight: 0.03 },
  { id: 35, name: 'Demand Distance', fullName: 'Distance to Demand Center', unit: 'km', category: 'grid', description: 'Distance to nearest major consumption center', range: '0 - 200', importance: 'Medium', weight: 0.03 },
  { id: 36, name: 'Grid Congestion', fullName: 'Grid Congestion Level', unit: 'index', category: 'grid', description: 'Current congestion on the transmission network', range: '0 - 1', importance: 'Medium', weight: 0.04 },
  { id: 37, name: 'Evacuation Capacity', fullName: 'Power Evacuation Capacity', unit: 'MW', category: 'grid', description: 'Available evacuation capacity in the network', range: '10 - 500', importance: 'High', weight: 0.05 },

  // Economic (5)
  { id: 38, name: 'Tariff Rate', fullName: 'Solar Power Tariff Rate', unit: '₹/kWh', category: 'economic', description: 'Available power purchase agreement tariff', range: '2.0 - 4.0', importance: 'High', weight: 0.06 },
  { id: 39, name: 'Policy Incentives', fullName: 'Government Policy Incentive Score', unit: 'score', category: 'economic', description: 'Composite score of state-level incentives', range: '0 - 1', importance: 'High', weight: 0.05 },
  { id: 40, name: 'Labor Availability', fullName: 'Skilled Labor Availability', unit: 'index', category: 'economic', description: 'Availability of skilled installation workforce', range: '0 - 1', importance: 'Medium', weight: 0.03 },
  { id: 41, name: 'Local Economy', fullName: 'Local Economic Development Index', unit: 'index', category: 'economic', description: 'Economic development level of the region', range: '0 - 1', importance: 'Low', weight: 0.02 },
  { id: 42, name: 'Investment Climate', fullName: 'State Investment Climate Score', unit: 'score', category: 'economic', description: 'Overall investment friendliness of the state', range: '0 - 1', importance: 'Medium', weight: 0.04 },
];

export default featureDefinitions;
