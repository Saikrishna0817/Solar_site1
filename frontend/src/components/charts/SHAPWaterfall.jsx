import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell, ReferenceLine } from 'recharts';
import { CHART_COLORS } from '../../data/constants';

const SHAPWaterfall = ({ data = [], className = '' }) => {
  const chartData = data.slice(0, 10).map(d => ({
    ...d,
    value: Number(d.value),
    fill: Number(d.value) >= 0 ? CHART_COLORS.quaternary : '#EF4444',
  }));

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload?.[0]) {
      const d = payload[0].payload;
      return (
        <div className="glass-strong rounded-lg px-4 py-2 text-sm">
          <p className="text-txt-primary font-medium">{d.feature}</p>
          <p style={{ color: d.fill }} className="font-mono">
            SHAP: {d.value > 0 ? '+' : ''}{d.value}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className={`w-full ${className}`} style={{ height: 360 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 20, left: 120, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} horizontal={false} />
          <XAxis type="number" tick={{ fill: CHART_COLORS.text, fontSize: 11 }} axisLine={{ stroke: CHART_COLORS.grid }} />
          <YAxis
            type="category"
            dataKey="feature"
            tick={{ fill: CHART_COLORS.text, fontSize: 11 }}
            axisLine={{ stroke: CHART_COLORS.grid }}
            width={115}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine x={0} stroke={CHART_COLORS.grid} />
          <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={18}>
            {chartData.map((entry, index) => (
              <Cell key={index} fill={entry.fill} fillOpacity={0.8} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default SHAPWaterfall;
