import { useEffect, useMemo, useState } from 'react';
import { useParams, useSearchParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { enrichedSites } from '../data/mockSites';
import api, { isLive } from '../services/api';
import SuitabilityGauge from '../components/charts/SuitabilityGauge';
import FeatureRadar from '../components/charts/FeatureRadar';
import { MonthlyGenerationChart, YearlyProjectionChart } from '../components/charts/GenerationChart';
import SHAPWaterfall from '../components/charts/SHAPWaterfall';
import GlassCard from '../components/ui/GlassCard';
import { getSuitabilityColor, getSuitabilityLabel } from '../data/constants';
import { formatCapacity, formatGeneration } from '../utils/formatters';
import { getConfidenceColor } from '../utils/colorScale';

const SiteAnalysis = () => {
  const { id: routeId } = useParams();
  const [searchParams] = useSearchParams();
  // /site/:id is canonical; the legacy /analyze?id= query param still resolves.
  const rawId = routeId ?? searchParams.get('id');

  const site = useMemo(() => {
    // Bare /analyze (Navbar/Footer) carries no id: show the first site, labelled
    // as a default below — but an id that does not match must never silently
    // resolve to a different site.
    if (rawId === null || rawId === undefined || rawId === '') return enrichedSites[0] ?? null;
    const id = Number(rawId);
    if (!Number.isFinite(id)) return null;
    return enrichedSites.find(s => s.id === id) || null;
  }, [rawId]);

  const noIdSelected = rawId === null || rawId === undefined || rawId === '';

  // SHAP comes from the trained model only — mock mode never fabricates values.
  const [shap, setShap] = useState(null); // null | { loading } | { data } | { error }
  useEffect(() => {
    if (!site || !isLive) {
      setShap(null);
      return undefined;
    }
    let alive = true;
    setShap({ loading: true });
    api.getSiteShap(site.district)
      .then(({ data }) => { if (alive) setShap({ data }); })
      .catch((err) => { if (alive) setShap({ error: err?.message || String(err) }); });
    return () => { alive = false; };
  }, [site]);

  // No id, unknown id, or non-numeric id → say so; never fall back to another site.
  if (!site) {
    return (
      <div className="min-h-screen pt-24 pb-16 bg-space-deep">
        <div className="container-custom">
          <div className="glass-card p-8 max-w-xl mx-auto text-center">
            <h1 className="font-display font-bold text-2xl text-txt-primary mb-3">Site not found</h1>
            <p className="text-txt-dim text-base mb-6">
              {rawId
                ? <>No site matches id <span className="font-mono text-txt-secondary">{rawId}</span>.</>
                : 'This link does not identify a site.'}{' '}
              Pick a site from the dashboard list.
            </p>
            <Link to="/dashboard" className="btn-outline inline-flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 17l-5-5m0 0l5-5m-5 5h12" />
              </svg>
              Back to Dashboard
            </Link>
          </div>
        </div>
      </div>
    );
  }

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
        {/* No id in the URL — say which site is shown and how to pick another */}
        {noIdSelected && (
          <div className="glass-card px-4 py-3 mb-4 text-sm text-txt-dim flex flex-wrap items-center gap-x-3 gap-y-1">
            <span className="text-warning font-semibold">No site selected</span>
            <span>
              showing <span className="text-txt-primary font-medium">{site.name}</span> as a
              default — <Link to="/dashboard" className="text-solar-gold hover:underline">pick a site from the dashboard</Link>.
            </span>
          </div>
        )}
        {/* This page always reads mockSites.js — say so before any score appears */}
        <div className="glass-card px-4 py-3 mb-4 text-sm text-txt-dim">
          <span className="text-warning font-semibold">Demo data</span> — suitability, confidence, LCOE/NPV and the
          feature radar below come from <span className="font-mono text-txt-secondary">mockSites.js</span>, not the
          trained model. SHAP is the only real model output, and only when the API is running.
        </div>
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
                  <p className="text-xs text-txt-dim">Confidence (demo)</p>
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

          {/* SHAP Waterfall — real attributions only, honest empty state otherwise */}
          <GlassCard hover={false}>
            <h3 className="font-display font-semibold text-txt-primary text-lg mb-4">Feature Contributions (SHAP)</h3>
            <p className="text-txt-dim text-sm mb-3">Each feature and its contribution to the predicted plant CUF — not to the demo suitability score</p>
            {shap?.data?.values?.length ? (
              <SHAPWaterfall data={shap.data.values} />
            ) : (
              <div className="h-[360px] flex flex-col items-center justify-center gap-2 text-center px-8">
                <p className="text-txt-dim text-sm leading-relaxed max-w-sm">
                  SHAP attributions require the trained backend — set{' '}
                  <span className="font-mono text-txt-secondary">VITE_USE_MOCK=false</span>{' '}
                  and run the API. No values are shown until the model serves them.
                </p>
                {shap?.loading && (
                  <p className="text-txt-dim text-xs">Requesting attributions…</p>
                )}
                {shap?.error && (
                  <p className="text-txt-dim text-xs font-mono">{shap.error}</p>
                )}
              </div>
            )}
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
