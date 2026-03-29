import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell } from 'recharts';
import GlassCard from '../components/ui/GlassCard';
import SectionTitle from '../components/ui/SectionTitle';
import AnimatedCounter from '../components/ui/AnimatedCounter';
import ScatterPlot from '../components/charts/ScatterPlot';
import SHAPWaterfall from '../components/charts/SHAPWaterfall';
import { enrichedSites } from '../data/mockSites';
import stateData from '../data/stateData';
import { CHART_COLORS, getSuitabilityColor } from '../data/constants';
import { formatCapacity, formatScore } from '../utils/formatters';

const ChartTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass-strong rounded-lg px-4 py-2 text-sm">
      <p className="text-txt-primary font-medium mb-1">{label}</p>
      {payload.map((e, i) => (
        <p key={i} style={{ color: e.color || e.fill }}>{e.name}: {typeof e.value === 'number' ? e.value.toFixed(1) : e.value}</p>
      ))}
    </div>
  );
};

const Results = () => {
  const [sortBy, setSortBy] = useState('suitability');
  const [sortOrder, setSortOrder] = useState('desc');
  const [expandedCase, setExpandedCase] = useState(null);

  const metrics = [
    { label: 'R² Score', value: 0.88, dec: 2, desc: 'Variance explained', color: '#10B981' },
    { label: 'MAPE', value: 11.5, dec: 1, suffix: '%', desc: 'Mean Abs % Error', color: '#F5A623' },
    { label: 'RMSE', value: 0.065, dec: 3, desc: 'Root Mean Sq Error', color: '#06B6D4' },
    { label: 'MAE', value: 0.052, dec: 3, desc: 'Mean Abs Error', color: '#8B5CF6' },
  ];

  const stateChart = useMemo(() => [...stateData].sort((a, b) => b.potentialGW - a.potentialGW).slice(0, 12), []);

  const sortedSites = useMemo(() => {
    return [...enrichedSites].sort((a, b) => sortOrder === 'desc' ? b[sortBy] - a[sortBy] : a[sortBy] - b[sortBy]).slice(0, 20);
  }, [sortBy, sortOrder]);

  const globalSHAP = [
    { feature: 'GHI (kWh/m²/day)', value: '0.245' },
    { feature: 'Grid Distance (km)', value: '-0.180' },
    { feature: 'Land Availability', value: '0.155' },
    { feature: 'DNI (kWh/m²/day)', value: '0.142' },
    { feature: 'Slope (°)', value: '-0.128' },
    { feature: 'Sunshine Hours', value: '0.115' },
    { feature: 'Road Distance (km)', value: '-0.098' },
    { feature: 'Temperature (°C)', value: '-0.085' },
    { feature: 'Substation Capacity', value: '0.072' },
    { feature: 'Policy Incentives', value: '0.065' },
  ];

  const cases = [
    { id: 1, title: 'Bhadla Solar Park', sub: "World's Largest Solar Park — Validation", state: 'Rajasthan', score: 0.94, cap: '2,245 MW',
      finding: 'Model correctly identified Bhadla as highest-scoring (0.94), validating against real-world status as world\'s largest solar park.',
      details: 'GHI: 5.72 | DNI: 5.45 | Elevation: 220m | Grid: 8km | LCOE: ₹2.15/kWh' },
    { id: 2, title: 'Mahbubnagar, Telangana', sub: 'Emerging Solar Hub — Discovery', state: 'Telangana', score: 0.83, cap: '100 MW',
      finding: 'Model identified Mahbubnagar as Telangana\'s top solar location, aligning with TSREDCO solar park proposals.',
      details: 'GHI: 5.38 | DNI: 5.08 | Elevation: 440m | Grid: 10km | LCOE: ₹2.42/kWh' },
    { id: 3, title: '500 GW Target Assessment', sub: 'National Policy Scenario', state: 'Pan-India', score: null, cap: '556 GW',
      finding: 'India has ~556 GW utility-scale potential across 20,780 sites, exceeding the 500 GW target. Top: Rajasthan (142), Gujarat (72), AP (56).',
      details: '20 states | 30K+ screened | 20,780 suitable | Avg GHI: 5.12 | 15.9% installed' },
  ];

  return (
    <div className="min-h-screen pt-24 pb-16 bg-space-deep">
      <div className="container-custom">
        <SectionTitle title="Results & Analysis" subtitle="Key findings from our ML ensemble model trained on 127 operational solar plants" />

        {/* Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-16">
          {metrics.map((m, i) => (
            <motion.div key={m.label} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.1 }}>
              <GlassCard className="text-center h-full">
                <p className="text-txt-dim text-sm mb-2">{m.desc}</p>
                <div className="font-display font-bold text-4xl mb-1" style={{ color: m.color }}>
                  <AnimatedCounter end={m.value} decimals={m.dec} suffix={m.suffix || ''} duration={1500} />
                </div>
                <p className="text-txt-secondary font-semibold text-base">{m.label}</p>
              </GlassCard>
            </motion.div>
          ))}
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-16">
          <GlassCard hover={false}>
            <h3 className="font-display font-semibold text-txt-primary text-lg mb-2">Predicted vs Actual Suitability</h3>
            <p className="text-txt-dim text-sm mb-4">Points near the diagonal = accurate predictions (R² = 0.88)</p>
            <ScatterPlot />
          </GlassCard>
          <GlassCard hover={false}>
            <h3 className="font-display font-semibold text-txt-primary text-lg mb-2">Global Feature Importance (SHAP)</h3>
            <p className="text-txt-dim text-sm mb-4">Average impact on model output across all predictions</p>
            <SHAPWaterfall data={globalSHAP} />
          </GlassCard>
        </div>

        {/* State Bar Chart */}
        <SectionTitle title="State-wise Solar Potential" subtitle="Top 12 states by utility-scale potential (GW)" gradient="tech" />
        <GlassCard hover={false} className="mb-16">
          <div style={{ height: 400 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stateChart} margin={{ top: 10, right: 20, bottom: 60, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} />
                <XAxis dataKey="state" tick={{ fill: CHART_COLORS.text, fontSize: 10 }} axisLine={{ stroke: CHART_COLORS.grid }} angle={-35} textAnchor="end" interval={0} />
                <YAxis tick={{ fill: CHART_COLORS.text, fontSize: 11 }} axisLine={{ stroke: CHART_COLORS.grid }} />
                <Tooltip content={<ChartTooltip />} />
                <Bar dataKey="potentialGW" name="Potential (GW)" radius={[4, 4, 0, 0]} barSize={32}>
                  {stateChart.map((e, i) => <Cell key={i} fill={e.color} fillOpacity={0.8} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        {/* Top Sites Table */}
        <SectionTitle title="Top Ranked Sites" subtitle="Highest scoring solar sites identified by the ML model" gradient="solar" />
        <GlassCard hover={false} className="mb-16 overflow-x-auto">
          <div className="flex items-center gap-4 mb-4">
            <span className="text-txt-dim text-sm">Sort:</span>
            {['suitability', 'ghi', 'capacity', 'lcoe'].map(f => (
              <button key={f} onClick={() => { if (sortBy === f) setSortOrder(o => o === 'desc' ? 'asc' : 'desc'); else { setSortBy(f); setSortOrder(f === 'lcoe' ? 'asc' : 'desc'); } }}
                className={`px-3 py-1 rounded-lg text-xs ${sortBy === f ? 'bg-solar-gold/20 text-solar-gold border border-solar-gold/30' : 'text-txt-dim border border-space-border'}`}>
                {f.charAt(0).toUpperCase() + f.slice(1)} {sortBy === f && (sortOrder === 'desc' ? '↓' : '↑')}
              </button>
            ))}
          </div>
          <table className="w-full text-base">
            <thead><tr className="border-b border-space-border text-txt-dim text-xs">
              <th className="py-3 px-3 text-left">#</th><th className="py-3 px-3 text-left">Site</th><th className="py-3 px-3 text-left">State</th>
              <th className="py-3 px-3 text-right">Score</th><th className="py-3 px-3 text-right">GHI</th><th className="py-3 px-3 text-right">Cap</th>
              <th className="py-3 px-3 text-right">LCOE</th><th className="py-3 px-3 text-right">NPV</th>
            </tr></thead>
            <tbody>{sortedSites.map((s, i) => (
              <tr key={s.id} className="border-b border-space-border/30 hover:bg-space-light/20">
                <td className="py-3 px-3 text-txt-dim font-mono">{i + 1}</td>
                <td className="py-3 px-3 text-txt-primary font-medium">{s.name}</td>
                <td className="py-3 px-3 text-txt-dim">{s.state}</td>
                <td className="py-3 px-3 text-right font-mono font-bold" style={{ color: getSuitabilityColor(s.suitability) }}>{formatScore(s.suitability)}</td>
                <td className="py-3 px-3 text-right text-solar-gold font-mono">{s.ghi}</td>
                <td className="py-3 px-3 text-right text-txt-primary">{formatCapacity(s.capacity)}</td>
                <td className="py-3 px-3 text-right font-mono">₹{s.lcoe}</td>
                <td className="py-3 px-3 text-right text-success font-mono">₹{s.npv}Cr</td>
              </tr>
            ))}</tbody>
          </table>
        </GlassCard>

        {/* Case Studies */}
        <SectionTitle title="Case Studies" subtitle="Real-world validation and key findings" gradient="mixed" />
        <div className="space-y-4">
          {cases.map((cs, i) => (
            <motion.div key={cs.id} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.1 }}>
              <GlassCard hover={false} className="cursor-pointer" onClick={() => setExpandedCase(expandedCase === cs.id ? null : cs.id)}>
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-display font-bold text-xl text-txt-primary">{cs.title}</h3>
                      {cs.score && <span className="text-xs font-bold font-mono px-2 py-0.5 rounded"
                        style={{ color: getSuitabilityColor(cs.score), background: `${getSuitabilityColor(cs.score)}15` }}>
                        {formatScore(cs.score)}</span>}
                    </div>
                    <p className="text-txt-dim text-base mb-1">{cs.sub}</p>
                    <p className="text-txt-secondary text-base">{cs.finding}</p>
                    {expandedCase === cs.id && (
                      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-4 pt-4 border-t border-space-border">
                        <p className="text-xs font-mono text-txt-dim bg-space-surface p-3 rounded-lg">{cs.details}</p>
                      </motion.div>
                    )}
                  </div>
                  <div className="flex items-center gap-2 text-txt-dim text-sm shrink-0">
                    <span>{cs.cap}</span>
                    <svg className={`w-4 h-4 transition-transform ${expandedCase === cs.id ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
              </GlassCard>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Results;
