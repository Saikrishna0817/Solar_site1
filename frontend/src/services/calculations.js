// Client-side suitability scoring calculations
// Mirrors the ML model's scoring logic for the interactive calculator

import { MODEL_WEIGHTS } from '../data/constants';

// Normalize a value to 0-1 range
const normalize = (value, min, max, inverse = false) => {
  const normalized = Math.max(0, Math.min(1, (value - min) / (max - min)));
  return inverse ? 1 - normalized : normalized;
};

// Individual feature scores
export const calculateFeatureScores = (inputs) => {
  const {
    ghi = 5.0,
    temperature = 27,
    slope = 2,
    roadDistance = 5,
    gridDistance = 10,
    landScore = 0.7,
  } = inputs;

  return {
    solar: normalize(ghi, 3.5, 6.0) * 0.95 + 0.05,
    temperature: normalize(temperature, 15, 40, true) * 0.3 + normalize(temperature, 15, 30) * 0.7,
    terrain: normalize(slope, 0, 15, true),
    road: normalize(roadDistance, 0, 20, true),
    grid: normalize(gridDistance, 0, 40, true),
    land: landScore,
  };
};

// Weighted suitability score
export const calculateSuitability = (inputs) => {
  const scores = calculateFeatureScores(inputs);
  const weights = {
    solar: 0.30,
    temperature: 0.10,
    terrain: 0.15,
    road: 0.10,
    grid: 0.20,
    land: 0.15,
  };

  const weightedScore = Object.keys(scores).reduce(
    (sum, key) => sum + scores[key] * weights[key],
    0
  );

  return {
    score: Math.max(0, Math.min(1, weightedScore)),
    featureScores: scores,
    breakdown: Object.keys(scores).map(key => ({
      feature: key.charAt(0).toUpperCase() + key.slice(1),
      score: scores[key],
      weight: weights[key],
      contribution: scores[key] * weights[key],
    })),
  };
};

// Economic calculations
export const calculateEconomics = (capacity, suitability, ghi) => {
  const annualGeneration = capacity * ghi * 0.18 * 365; // MWh
  const capitalCost = capacity * 4.5; // ₹ Crore per MW
  const annualRevenue = annualGeneration * 2.5 / 10000000; // ₹ Crore (at ₹2.5/kWh)
  const annualOM = capitalCost * 0.015; // 1.5% of capex
  const netAnnualRevenue = annualRevenue - annualOM;
  const lcoe = (capitalCost * 10000000 * 0.1) / annualGeneration; // ₹/kWh (10% CRF)
  const npv = netAnnualRevenue * 12 - capitalCost; // Simplified 25yr NPV
  const payback = capitalCost / netAnnualRevenue;

  return {
    annualGeneration: Math.round(annualGeneration),
    capitalCost: Math.round(capitalCost * 100) / 100,
    annualRevenue: Math.round(annualRevenue * 100) / 100,
    lcoe: Math.round(lcoe * 100) / 100,
    npv: Math.round(npv * 100) / 100,
    paybackYears: Math.round(payback * 10) / 10,
  };
};
