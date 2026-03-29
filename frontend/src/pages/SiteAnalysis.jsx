import { useMemo } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { enrichedSites } from '../data/mockSites';
import SuitabilityGauge from '../components/charts/SuitabilityGauge';
import FeatureRadar from '../components/charts/FeatureRadar';
import { MonthlyGenerationChart, YearlyProjectionChart } from '../components/charts/GenerationChart';
import SHAPWaterfall from '../components/charts/SHAPWaterfall';
import GlassCard from '../components/ui/GlassCard';
import AnimatedCounter from '../components/ui/AnimatedCounter';
import { getSuitabilityColor, getSuitabilityLabel } from '../data/constants';
import { formatCapacity, formatGeneration, formatNumber } from '../utils/formatters';
import { getConfidenceColor } from '../utils/colorScale';

const SiteAnalysis = () => {
  const [searchParams] = useSearchParams();
  const siteId = parseInt(searchParams.get('id') || '1');

  const site = useMemo(
    () => enrichedSites.find(s => s.id === siteId) || enrichedSites[0],
    [siteId]
  );

  const color = getSuitabilityColor(site.suitability);
  const label = getSuitabilityLabel(site.suitability);

  const economicCards = [
    { label: 'LCOE', value: `₹${site.lcoe}`, unit: '/kWh', color: '#F5A623', description: 'Levelized Cost of Energy' },
    { label: 'NPV', value: `₹${site.npv}`, unit: ' Cr', color: '#10B981', description: 'Net Present Value (25yr)' },
    { label: 'Payback', value: site.paybackYears, unit: ' years', color: '#06B6D4', description: 'Investment Payback Period' },
    { label: 'Annual Gen.', value: formatGeneration(site.annualGeneration), unit: '', color: '#8B5CF6', description: 'Annual Energy Generation' },
  ];

  return (
    <div className="min-h-screen pt-24 pb-16 bg-space-deep">
      <div className="container-custom">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-base text-txt-dim mb-6">
          <Link to="/dashboard" className="hover:text-solar-gold transition-colors">Dashboard</Link>
          <span>›</span>
          <span className="text-txt-primary">{site.name}</span>
        </div>

        {/* Site Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-6 md:p-8 mb-6"
        >
          <div className="flex flex-col lg:flex-row items-start lg:items-center gap-8">
            <SuitabilityGauge score={site.suitability} size={180} />

            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h1 className="font-display font-bold text-3xl md:text-4xl text-txt-primary">{site.name}</h1>
                <span
                  className="px-3 py-1 rounded-full text-xs font-semibold"
                  style={{ backgroundColor: `${color}20`, color }}
                >
                  {label}
                </span>
              </div>

              <p className="text-txt-secondary mb-4">
                {site.district}, {site.state} • {site.lat.toFixed(4)}°N, {site.lng.toFixed(4)}°E
              </p>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="glass p-3 rounded-lg">
                  <p className="text-xs text-txt-dim">GHI</p>
                  <p className="font-display font-bold text-solar-gold text-lg">{site.ghi} <span className="text-xs text-txt-dim">kWh/m²/day</span></p>
                </div>
                <div className="glass p-3 rounded-lg">
                  <p className="text-xs text-txt-dim">Capacity</p>
                  <p className="font-display font-bold text-tech-cyan text-lg">{formatCapacity(site.capacity)}</p>
                </div>
                <div className="glass p-3 rounded-lg">
                  <p className="text-xs text-txt-dim">Land Type</p>
                  <p className="font-display font-semibold text-txt-primary text-lg">{site.landType}</p>
                </div>
                <div className="glass p-3 rounded-lg">
                  <p className="text-xs text-txt-dim">Confidence</p>
                  <p className="font-display font-bold text-lg" style={{ color: getConfidenceColor(site.confidence) }}>
                    {(site.confidence * 100).toFixed(0)}%
                  </p>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
          {/* Feature Radar */}
          <GlassCard hover={false}>
            <h3 className="font-display font-semibold text-txt-primary text-lg mb-4">Feature Analysis</h3>
            <FeatureRadar featureScores={site.featureScores} />
          </GlassCard>

          {/* Monthly Generation */}
          <GlassCard hover={false}>
            <h3 className="font-display font-semibold text-txt-primary text-lg mb-4">Monthly Generation Profile</h3>
            <MonthlyGenerationChart data={site.monthlyGeneration} />
          </GlassCard>

          {/* 25-Year Projection */}
          <GlassCard hover={false}>
            <h3 className="font-display font-semibold text-txt-primary text-lg mb-4">25-Year Generation Projection</h3>
            <YearlyProjectionChart data={site.yearlyProjection} />
          </GlassCard>

          {/* SHAP Waterfall */}
          <GlassCard hover={false}>
            <h3 className="font-display font-semibold text-txt-primary text-lg mb-4">Feature Contributions (SHAP)</h3>
            <p className="text-txt-dim text-sm mb-3">Impact on suitability score prediction</p>
            <SHAPWaterfall data={site.shapValues} />
          </GlassCard>
        </div>

        {/* Economics Cards */}
        <h3 className="font-display font-semibold text-txt-primary text-2xl mb-4">Economic Analysis</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
          {economicCards.map((card, i) => (
            <motion.div
              key={card.label}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
            >
              <GlassCard className="text-center">
                <p className="text-sm text-txt-dim mb-1">{card.description}</p>
                <p className="font-display font-bold text-3xl mb-1" style={{ color: card.color }}>
                  {card.value}<span className="text-base text-txt-dim">{card.unit}</span>
                </p>
                <p className="text-base font-semibold text-txt-secondary">{card.label}</p>
              </GlassCard>
            </motion.div>
          ))}
        </div>

        {/* Site Details Table */}
        <GlassCard hover={false} className="mb-6">
          <h3 className="font-display font-semibold text-txt-primary text-lg mb-4">Site Parameters</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {[
              { label: 'Elevation', value: `${site.elevation} m` },
              { label: 'Slope', value: `${site.slope}°` },
              { label: 'DNI', value: `${site.dni} kWh/m²/day` },
              { label: 'Grid Distance', value: `${site.gridDistance} km` },
              { label: 'Road Distance', value: `${site.roadDistance} km` },
              { label: 'Temperature', value: `${site.temperature}°C` },
              { label: 'Humidity', value: `${site.humidity}%` },
              { label: 'Wind Speed', value: `${site.windSpeed} m/s` },
              { label: 'Rainfall', value: `${site.rainfall} mm/yr` },
            ].map(param => (
              <div key={param.label} className="flex justify-between border-b border-space-border/30 pb-2">
                <span className="text-txt-dim text-base">{param.label}</span>
                <span className="text-txt-primary text-base font-mono">{param.value}</span>
              </div>
            ))}
          </div>
        </GlassCard>

        {/* Back to Dashboard */}
        <div className="text-center">
          <Link
            to="/dashboard"
            className="btn-outline inline-flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 17l-5-5m0 0l5-5m-5 5h12" />
            </svg>
            Back to Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
};

export default SiteAnalysis;
