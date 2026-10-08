// State-wise aggregated solar potential & installed capacity for India
// Sources:
//   - Installed capacity: MNRE Physical Progress (State-wise RE Installed Capacity, 31.07.2026)
//   - Solar potential: NISE "Solar PV Potential of India (Ground Mounted) 2025" (3,343 GWp total)
//   - GHI: NIWE Resource Portal averages (maps.niwe.res.in)

export const stateData = [
  { state: 'Rajasthan', potentialGW: 828.78, installedGW: 44.14, avgGHI: 5.58, color: '#F5A623' },
  { state: 'Gujarat', potentialGW: 223.28, installedGW: 33.76, avgGHI: 5.42, color: '#E8590C' },
  { state: 'Tamil Nadu', potentialGW: 204.77, installedGW: 14.12, avgGHI: 5.35, color: '#D97706' },
  { state: 'Andhra Pradesh', potentialGW: 243.22, installedGW: 8.14, avgGHI: 5.48, color: '#06B6D4' },
  { state: 'Karnataka', potentialGW: 223.28, installedGW: 11.64, avgGHI: 5.38, color: '#8B5CF6' },
  { state: 'Madhya Pradesh', potentialGW: 318.97, installedGW: 6.54, avgGHI: 5.32, color: '#10B981' },
  { state: 'Maharashtra', potentialGW: 486.68, installedGW: 20.35, avgGHI: 5.25, color: '#3B82F6' },
  { state: 'Telangana', potentialGW: 140.45, installedGW: 5.17, avgGHI: 5.28, color: '#14B8A6' },
  { state: 'Uttar Pradesh', potentialGW: 97.84, installedGW: 6.02, avgGHI: 5.15, color: '#EF4444' },
  { state: 'Punjab', potentialGW: 11.0, installedGW: 1.6, avgGHI: 5.10, color: '#F59E0B' },
  { state: 'Haryana', potentialGW: 6.0, installedGW: 2.86, avgGHI: 5.12, color: '#A855F7' },
  { state: 'Odisha', potentialGW: 25.0, installedGW: 1.13, avgGHI: 4.95, color: '#EC4899' },
  { state: 'Chhattisgarh', potentialGW: 18.0, installedGW: 2.03, avgGHI: 4.88, color: '#F97316' },
  { state: 'Jharkhand', potentialGW: 18.0, installedGW: 0.32, avgGHI: 4.82, color: '#84CC16' },
  { state: 'Bihar', potentialGW: 11.0, installedGW: 0.49, avgGHI: 4.75, color: '#22D3EE' },
  { state: 'West Bengal', potentialGW: 6.0, installedGW: 0.36, avgGHI: 4.68, color: '#A78BFA' },
  { state: 'Kerala', potentialGW: 6.0, installedGW: 2.63, avgGHI: 4.55, color: '#FB923C' },
  { state: 'Uttarakhand', potentialGW: 16.0, installedGW: 0.89, avgGHI: 4.48, color: '#34D399' },
  { state: 'Himachal Pradesh', potentialGW: 34.0, installedGW: 0.39, avgGHI: 4.95, color: '#60A5FA' },
  { state: 'Assam', potentialGW: 13.0, installedGW: 0.74, avgGHI: 4.35, color: '#C084FC' },
];

// Overall Summary — only figures with a traceable source are kept:
//   totalPotentialGW  NISE 2025 (same report as the state rows above)
//   totalInstalledGW  MNRE Physical Progress, 31.07.2026 (kept in sync by
//                     scripts/update_frontend_metrics.py, which also writes
//                     KEY_METRICS.totalCapacityGW from the same feed)
//   targetGW/year     MNRE 500 GW by 2030 target
//   percentAchieved   derived here, not published: 164.59 GW solar installed ÷
//                     500 GW renewable target = 32.9%. Solar-only numerator
//                     against an all-renewable target — read it as "solar's
//                     share of the 500 GW goal", not an official progress rate.
// (totalSuitableSites / avgNationalGHI / statesWithHighPotential were dropped:
//  they had no source and no consumer.)
export const nationalSummary = {
  totalPotentialGW: 3343,
  totalInstalledGW: 164.59,
  targetGW: 500,
  targetYear: 2030,
  percentAchieved: 32.9,
};

export default stateData;
