import { ResponsiveContainer, ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { CHART_COLORS } from '../../data/constants';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload?.length) {
    return (
      <div className="glass-strong rounded-lg px-4 py-3 text-sm shadow-lg">
        <p className="text-txt-primary font-semibold mb-1">{label}</p>
        {payload.map((entry, i) => (
          <p key={i} style={{ color: entry.color }} className="flex justify-between gap-4">
            <span>{entry.name}:</span>
            <span className="font-mono">{typeof entry.value === 'number' ? entry.value.toLocaleString() : entry.value}</span>
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export const MonthlyGenerationChart = ({ data = [], className = '' }) => {
  return (
    <div className={`w-full ${className}`} style={{ height: 320 }}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} />
          <XAxis dataKey="month" tick={{ fill: CHART_COLORS.text, fontSize: 12 }} axisLine={{ stroke: CHART_COLORS.grid }} />
          <YAxis tick={{ fill: CHART_COLORS.text, fontSize: 11 }} axisLine={{ stroke: CHART_COLORS.grid }} />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ color: CHART_COLORS.text, fontSize: 12 }} />
          <Bar
            dataKey="generation"
            name="Generation (MWh)"
            fill={CHART_COLORS.primary}
            radius={[4, 4, 0, 0]}
            fillOpacity={0.8}
          />
          <Line
            dataKey="irradiance"
            name="GHI (kWh/m²/day)"
            stroke={CHART_COLORS.secondary}
            strokeWidth={2}
            dot={{ fill: CHART_COLORS.secondary, r: 3 }}
            yAxisId={0}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};

export const YearlyProjectionChart = ({ data = [], className = '' }) => {
  return (
    <div className={`w-full ${className}`} style={{ height: 320 }}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} />
          <XAxis
            dataKey="year"
            tick={{ fill: CHART_COLORS.text, fontSize: 11 }}
            axisLine={{ stroke: CHART_COLORS.grid }}
            interval={4}
          />
          <YAxis tick={{ fill: CHART_COLORS.text, fontSize: 11 }} axisLine={{ stroke: CHART_COLORS.grid }} />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ color: CHART_COLORS.text, fontSize: 12 }} />
          <Bar
            dataKey="generation"
            name="Annual (MWh)"
            fill={CHART_COLORS.primary}
            fillOpacity={0.6}
            radius={[2, 2, 0, 0]}
          />
          <Line
            dataKey="cumulative"
            name="Cumulative (MWh)"
            stroke={CHART_COLORS.quaternary}
            strokeWidth={2}
            dot={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};

export default MonthlyGenerationChart;
