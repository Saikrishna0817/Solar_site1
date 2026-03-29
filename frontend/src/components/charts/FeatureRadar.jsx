import { ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Tooltip } from 'recharts';
import { FEATURE_CATEGORIES, CHART_COLORS } from '../../data/constants';

const FeatureRadar = ({ featureScores = {}, className = '' }) => {
  const data = FEATURE_CATEGORIES.map(cat => ({
    category: cat.label,
    score: (featureScores[cat.key] || 0.5) * 100,
    fullMark: 100,
    color: cat.color,
  }));

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload?.[0]) {
      const d = payload[0].payload;
      return (
        <div className="glass-strong rounded-lg px-3 py-2 text-sm">
          <p className="text-txt-primary font-medium">{d.category}</p>
          <p className="text-solar-gold">{d.score.toFixed(1)}%</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className={`w-full ${className}`} style={{ height: 320 }}>
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={data} cx="50%" cy="50%" outerRadius="75%">
          <PolarGrid stroke="rgba(30, 58, 82, 0.4)" />
          <PolarAngleAxis
            dataKey="category"
            tick={{ fill: '#8BA8BF', fontSize: 11, fontWeight: 500 }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fill: '#5A7A94', fontSize: 10 }}
            axisLine={false}
          />
          <Radar
            name="Score"
            dataKey="score"
            stroke={CHART_COLORS.primary}
            fill={CHART_COLORS.primary}
            fillOpacity={0.15}
            strokeWidth={2}
            dot={{ fill: CHART_COLORS.primary, r: 4 }}
          />
          <Tooltip content={<CustomTooltip />} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default FeatureRadar;
