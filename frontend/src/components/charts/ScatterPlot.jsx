import { ResponsiveContainer, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ZAxis } from 'recharts';
import { CHART_COLORS } from '../../data/constants';

const ScatterPlot = ({ data = [], className = '' }) => {
  // Generate predicted vs actual data if not provided
  const chartData = data.length > 0 ? data : Array.from({ length: 50 }, () => {
    const actual = Math.random() * 0.6 + 0.4;
    const noise = (Math.random() - 0.5) * 0.12;
    return {
      actual: Number(actual.toFixed(3)),
      predicted: Number((actual + noise).toFixed(3)),
      residual: Number(Math.abs(noise).toFixed(3)),
    };
  });

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload?.length) {
      return (
        <div className="glass-strong rounded-lg px-4 py-2 text-sm">
          <p className="text-txt-secondary">Actual: <span className="text-solar-gold font-mono">{payload[0]?.value?.toFixed(3)}</span></p>
          <p className="text-txt-secondary">Predicted: <span className="text-tech-cyan font-mono">{payload[1]?.value?.toFixed(3)}</span></p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className={`w-full ${className}`} style={{ height: 400 }}>
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} />
          <XAxis
            type="number"
            dataKey="actual"
            name="Actual"
            domain={[0.3, 1.0]}
            tick={{ fill: CHART_COLORS.text, fontSize: 11 }}
            axisLine={{ stroke: CHART_COLORS.grid }}
            label={{ value: 'Actual Suitability', position: 'bottom', fill: CHART_COLORS.text, fontSize: 12 }}
          />
          <YAxis
            type="number"
            dataKey="predicted"
            name="Predicted"
            domain={[0.3, 1.0]}
            tick={{ fill: CHART_COLORS.text, fontSize: 11 }}
            axisLine={{ stroke: CHART_COLORS.grid }}
            label={{ value: 'Predicted Suitability', angle: -90, position: 'insideLeft', fill: CHART_COLORS.text, fontSize: 12 }}
          />
          <ZAxis range={[40, 80]} />
          <Tooltip content={<CustomTooltip />} />
          {/* Perfect prediction line */}
          <ReferenceLine
            segment={[{ x: 0.3, y: 0.3 }, { x: 1.0, y: 1.0 }]}
            stroke={CHART_COLORS.secondary}
            strokeDasharray="5 5"
            strokeOpacity={0.5}
          />
          <Scatter
            data={chartData}
            fill={CHART_COLORS.primary}
            fillOpacity={0.7}
            stroke={CHART_COLORS.primary}
            strokeOpacity={0.3}
          />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ScatterPlot;
