// Formatting utilities

export const formatNumber = (num, decimals = 0) => {
  if (num === null || num === undefined) return '—';
  return new Intl.NumberFormat('en-IN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(num);
};

export const formatCurrency = (num, currency = '₹') => {
  if (num >= 10000000) return `${currency}${(num / 10000000).toFixed(1)} Cr`;
  if (num >= 100000) return `${currency}${(num / 100000).toFixed(1)} L`;
  if (num >= 1000) return `${currency}${(num / 1000).toFixed(1)}K`;
  return `${currency}${num}`;
};

export const formatCapacity = (mw) => {
  if (mw >= 1000) return `${(mw / 1000).toFixed(1)} GW`;
  return `${mw} MW`;
};

export const formatGeneration = (mwh) => {
  if (mwh >= 1000000) return `${(mwh / 1000000).toFixed(1)} TWh`;
  if (mwh >= 1000) return `${(mwh / 1000).toFixed(1)} GWh`;
  return `${mwh} MWh`;
};

export const formatPercentage = (value, decimals = 1) => {
  return `${(value * 100).toFixed(decimals)}%`;
};

export const formatScore = (score) => {
  return (score * 100).toFixed(0);
};

export const formatDistance = (km) => {
  if (km < 1) return `${(km * 1000).toFixed(0)} m`;
  return `${km.toFixed(1)} km`;
};

export const truncateText = (text, maxLength = 40) => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};
