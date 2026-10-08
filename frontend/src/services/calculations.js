// Client-side suitability scoring calculations
// Heuristic for the on-page "Try It Yourself" calculator (6 sliders) — this is
// NOT the trained model and not model output. The served model is the
// elastic_net plant-level CUF regressor in KEY_METRICS.modelType.
// ponytail: the weights below are hand-picked, fitted to nothing; ceiling = a
// visitor can read the gauge as a model prediction. Upgrade path = score the
// calculator through /v1/predict and keep this block as a labeled fallback.

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

