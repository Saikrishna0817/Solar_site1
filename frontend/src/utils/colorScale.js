// Color scale utilities for solar site visualization

export const interpolateColor = (value, min, max, colorStart, colorEnd) => {
  const ratio = Math.max(0, Math.min(1, (value - min) / (max - min)));
  const r1 = parseInt(colorStart.slice(1, 3), 16);
  const g1 = parseInt(colorStart.slice(3, 5), 16);
  const b1 = parseInt(colorStart.slice(5, 7), 16);
  const r2 = parseInt(colorEnd.slice(1, 3), 16);
  const g2 = parseInt(colorEnd.slice(3, 5), 16);
  const b2 = parseInt(colorEnd.slice(5, 7), 16);
  const r = Math.round(r1 + (r2 - r1) * ratio);
  const g = Math.round(g1 + (g2 - g1) * ratio);
  const b = Math.round(b1 + (b2 - b1) * ratio);
  return `rgb(${r}, ${g}, ${b})`;
};

export const suitabilityToColor = (score) => {
  if (score >= 0.8) return interpolateColor(score, 0.8, 1.0, '#10B981', '#059669');
  if (score >= 0.6) return interpolateColor(score, 0.6, 0.8, '#F5A623', '#10B981');
  if (score >= 0.4) return interpolateColor(score, 0.4, 0.6, '#EF4444', '#F5A623');
  return interpolateColor(score, 0.0, 0.4, '#7F1D1D', '#EF4444');
};

export const ghiToColor = (ghi) => {
  if (ghi >= 5.5) return '#FF0040';
  if (ghi >= 5.0) return '#E8590C';
  if (ghi >= 4.5) return '#F5A623';
  if (ghi >= 4.0) return '#06B6D4';
  return '#1E3A5F';
};

export const getMarkerRadius = (capacity) => {
  if (capacity >= 500) return 12;
  if (capacity >= 200) return 10;
  if (capacity >= 100) return 8;
  if (capacity >= 50) return 6;
  return 5;
};

export const getConfidenceColor = (confidence) => {
  if (confidence >= 0.9) return '#10B981';
  if (confidence >= 0.8) return '#F5A623';
  if (confidence >= 0.7) return '#D97706';
  return '#EF4444';
};
