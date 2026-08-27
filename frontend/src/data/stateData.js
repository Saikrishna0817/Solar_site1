// State-wise aggregated solar potential & installed capacity for India
// Sources:
//   - Installed capacity: MNRE Physical Progress (State-wise RE Installed Capacity, 31.07.2026)
//   - Solar potential: NISE "Solar PV Potential of India (Ground Mounted) 2025" (3,343 GWp total)
//   - GHI: NIWE Resource Portal averages (maps.niwe.res.in)

export const stateData = [
  { state: 'Rajasthan', potentialGW: 828.78, installedGW: 44.14, suitableSites: 4250, avgGHI: 5.58, avgSuitability: 0.86, topDistrict: 'Jaisalmer', color: '#F5A623' },
  { state: 'Gujarat', potentialGW: 223.28, installedGW: 33.76, suitableSites: 2100, avgGHI: 5.42, avgSuitability: 0.82, topDistrict: 'Kutch', color: '#E8590C' },
  { state: 'Tamil Nadu', potentialGW: 204.77, installedGW: 14.12, suitableSites: 1800, avgGHI: 5.35, avgSuitability: 0.80, topDistrict: 'Ramanathapuram', color: '#D97706' },
  { state: 'Andhra Pradesh', potentialGW: 243.22, installedGW: 8.14, suitableSites: 2400, avgGHI: 5.48, avgSuitability: 0.84, topDistrict: 'Kurnool', color: '#06B6D4' },
  { state: 'Karnataka', potentialGW: 223.28, installedGW: 11.64, suitableSites: 1500, avgGHI: 5.38, avgSuitability: 0.81, topDistrict: 'Tumkur', color: '#8B5CF6' },
  { state: 'Madhya Pradesh', potentialGW: 318.97, installedGW: 6.54, suitableSites: 1900, avgGHI: 5.32, avgSuitability: 0.79, topDistrict: 'Rewa', color: '#10B981' },
  { state: 'Maharashtra', potentialGW: 486.68, installedGW: 20.35, suitableSites: 1700, avgGHI: 5.25, avgSuitability: 0.77, topDistrict: 'Dhule', color: '#3B82F6' },
  { state: 'Telangana', potentialGW: 140.45, installedGW: 5.17, suitableSites: 1200, avgGHI: 5.28, avgSuitability: 0.78, topDistrict: 'Mahbubnagar', color: '#14B8A6' },
  { state: 'Uttar Pradesh', potentialGW: 97.84, installedGW: 6.02, suitableSites: 900, avgGHI: 5.15, avgSuitability: 0.74, topDistrict: 'Jhansi', color: '#EF4444' },
  { state: 'Punjab', potentialGW: 11.0, installedGW: 1.6, suitableSites: 400, avgGHI: 5.10, avgSuitability: 0.72, topDistrict: 'Bathinda', color: '#F59E0B' },
  { state: 'Haryana', potentialGW: 6.0, installedGW: 2.86, suitableSites: 350, avgGHI: 5.12, avgSuitability: 0.73, topDistrict: 'Hisar', color: '#A855F7' },
  { state: 'Odisha', potentialGW: 25.0, installedGW: 1.13, suitableSites: 600, avgGHI: 4.95, avgSuitability: 0.68, topDistrict: 'Kalahandi', color: '#EC4899' },
  { state: 'Chhattisgarh', potentialGW: 18.0, installedGW: 2.03, suitableSites: 450, avgGHI: 4.88, avgSuitability: 0.66, topDistrict: 'Korba', color: '#F97316' },
  { state: 'Jharkhand', potentialGW: 18.0, installedGW: 0.32, suitableSites: 300, avgGHI: 4.82, avgSuitability: 0.64, topDistrict: 'Hazaribagh', color: '#84CC16' },
  { state: 'Bihar', potentialGW: 11.0, installedGW: 0.49, suitableSites: 200, avgGHI: 4.75, avgSuitability: 0.62, topDistrict: 'Nawada', color: '#22D3EE' },
  { state: 'West Bengal', potentialGW: 6.0, installedGW: 0.36, suitableSites: 180, avgGHI: 4.68, avgSuitability: 0.58, topDistrict: 'Purulia', color: '#A78BFA' },
  { state: 'Kerala', potentialGW: 6.0, installedGW: 2.63, suitableSites: 120, avgGHI: 4.55, avgSuitability: 0.55, topDistrict: 'Kasaragod', color: '#FB923C' },
  { state: 'Uttarakhand', potentialGW: 16.0, installedGW: 0.89, suitableSites: 150, avgGHI: 4.48, avgSuitability: 0.52, topDistrict: 'Dehradun', color: '#34D399' },
  { state: 'Himachal Pradesh', potentialGW: 34.0, installedGW: 0.39, suitableSites: 180, avgGHI: 4.95, avgSuitability: 0.68, topDistrict: 'Lahaul Spiti', color: '#60A5FA' },
  { state: 'Assam', potentialGW: 13.0, installedGW: 0.74, suitableSites: 100, avgGHI: 4.35, avgSuitability: 0.48, topDistrict: 'Kamrup', color: '#C084FC' },
];

// Overall Summary (from MNRE/CEA official data as of 31.07.2026)
export const nationalSummary = {
  totalPotentialGW: 3343,
  totalInstalledGW: 164.59,
  totalSuitableSites: 20780,
  avgNationalGHI: 5.12,
  targetGW: 500,
  targetYear: 2030,
  percentAchieved: 32.9,
  statesWithHighPotential: 8,
};

export default stateData;