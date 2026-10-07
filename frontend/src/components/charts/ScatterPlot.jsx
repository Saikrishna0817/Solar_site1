import { ResponsiveContainer, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ZAxis } from 'recharts';
import { CHART_COLORS } from '../../data/constants';

const ScatterPlot = ({ data = [], className = '' }) => {
  // ponytail: nothing serves pooled out-of-fold predictions yet, so an empty
  // `data` renders an honest empty state — this used to fill the chart with
  // Math.random() points dressed up as model validation. Ceiling = the card
  // stays empty until real predictions exist. Upgrade path = expose OOF
  // (pred, label) pairs from the training run (models/metrics.json or a
  // /v1/evaluation endpoint) and pass them here.
  if (!data.length) {
    return (
      <div className={`w-full ${className}`} style={{ height: 400 }}>
        <div className="w-full h-full flex items-center justify-center text-center px-8">
          <p className="text-txt-dim text-sm leading-relaxed max-w-sm">
            Predicted-vs-actual points require out-of-fold predictions from the
            trained backend, which the API does not expose yet. No points are
            drawn until it does.
          </p>
        </div>
      </div>
    );
  }

  const chartData = data;

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
