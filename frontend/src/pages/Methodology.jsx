import { useState } from 'react';
import { motion } from 'framer-motion';
import GlassCard from '../components/ui/GlassCard';
import SectionTitle from '../components/ui/SectionTitle';
import { featureDefinitions } from '../data/mockFeatures';
import { FEATURE_CATEGORIES, KEY_METRICS } from '../data/constants';
// Gate table copied from models/metrics.json + models/gate.json by
// scripts/update_frontend_metrics.py --write, so the page carries the same
// numbers the API gate enforces.
// ponytail: baked at sync time — rerun the script after retraining, else the cards
// show the previous run. Upgrade path: serve the table from /api/health.
import gateMetrics from '../data/gateMetrics.json';

const c0Mae = gateMetrics.c0_mae;
const gate3 = gateMetrics.gate3 || null;
const servedName = gate3?.gate3_pass ? gate3.served_model : null;
const rankedModels = [...gateMetrics.models].sort((a, b) => a.cv_mae - b.cv_mae);
const cvFrontRunner = rankedModels.find((m) => m.beats_c0) || null;

// The served artifact: residual model over C0, Gate 3 contract (LOGO bootstrap
// CI + held-out plants), with its conformal interval.
const servedCard = servedName ? {
  name: `residual ${servedName} (served)`,
  badge: 'Serving (Gate 3)',
  color: '#F5A623',
  params: `held-out MAE ${gate3.heldout?.model_mae?.toFixed?.(4)} vs C0 ${gate3.heldout?.c0_mae?.toFixed?.(4)}; ΔMAE CI ${gate3.delta_ci95?.map?.((v) => v.toFixed(4)).join(' to ')}`,
  strength: `Gate 3 passed: beats C0 on the district-bootstrap CI and on held-out plants; conformal 90% half-width ±${gate3.conformal90_halfwidth?.toFixed?.(4)}. Serves as c0_physics + residual.`,
} : {
  name: 'serving',
  badge: 'C0 physics only',
  color: '#8B5CF6',
  params: 'Gate 3 not passed',
  strength: 'No model cleared Gate 3 — the API serves the pvlib C0 physics baseline alone.',
};

// One card per CV candidate (43-feature batch, metrics.json) — context, not
// what the API serves; the served artifact is the card above.
const modelCards = [servedCard, ...rankedModels.map((m) => ({
  name: m.model_name.replace(/_/g, ' '),
  badge: !m.beats_c0 ? 'Rejected' : m === cvFrontRunner ? 'Best CV (not served)' : 'Beats C0 (CV)',
  color: !m.beats_c0 ? '#8B5CF6' : '#10B981',
  params: `CV MAE ${m.cv_mae.toFixed(4)} vs C0 ${c0Mae.toFixed(4)}`,
  strength: !m.beats_c0
    ? 'At or above the physics baseline — refused by every gate.'
    : m === cvFrontRunner
      ? 'Lowest CV MAE among candidates that clear the CV rule — superseded by the pre-registered residual model, which is what src/api/services/gate.py loads.'
      : 'Clears the CV baseline but loses on CV MAE — not served.',
}))];

const Methodology = () => {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredFeatures = featureDefinitions.filter(f => {
    const matchesCategory = selectedCategory === 'all' || f.category === selectedCategory;
    const matchesSearch = !searchQuery || f.fullName.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          f.name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const pipelineStages = [
    {
      title: 'Data Acquisition',
      time: 'Stage 1',
      color: '#06B6D4',
      items: ['NASA POWER API — Solar irradiance (GHI, DNI, DHI)', 'SRTM DEM — Terrain elevation, slope, aspect', 'ESA WorldCover — Land use/land cover (%)', 'OSM — Infrastructure proximity', 'MODIS AOD — Aerosol optical depth', 'Census 2011 + projections — Population & density'],
    },
    {
      title: 'Feature Engineering',
      time: 'Stage 2',
      color: '#8B5CF6',
      items: [`${KEY_METRICS.featuresUsed} total features (raw + engineered)`, 'Collinear drop: Pearson > 0.95 pairs and known near-duplicates', 'Train/test split 80/20 stratified by state, taken before imputation', 'Train-only medians, winsorization, log-transform, StandardScaler', 'Composite infrastructure index (individual distance columns dropped)', 'Every fitted statistic comes from the training fold only'],
    },
    {
      title: 'Model Training (Real CUF)',
      time: 'Stage 3',
      color: '#F5A623',
      items: [`CEA-actual CUF labels for ${KEY_METRICS.sitesAnalyzed} in-scope plants (${KEY_METRICS.statesWithPlants} states: Telangana + Andhra Pradesh)`, `${KEY_METRICS.districtsAnalyzed}-district feature frame; physics-derived CUF is never used as a label`, 'Collinear drop + RFE (Random Forest estimator) re-fitted inside every CV fold', `${KEY_METRICS.evaluationMethod}`, 'Serving gate (Gate 3): district-bootstrap CI must beat pvlib C0 AND held-out plants must beat C0 (models/gate.json)', 'Pre-registered feature set (models/pre_registered_features.json) — committed before any run'],
    },
    {
      title: 'Scoring & Serving',
      time: 'Stage 4',
      color: '#10B981',
      items: [servedName
        ? `Serves residual ${servedName}: held-out MAE ${gate3.heldout?.model_mae?.toFixed?.(4)} vs C0 ${gate3.heldout?.c0_mae?.toFixed?.(4)}; conformal 90% ±${gate3.conformal90_halfwidth?.toFixed?.(4)}`
        : 'Gate 3 failed — the API serves the C0 physics baseline only (see /api/health)', 'SHAP attributions come from the live model — empty state otherwise', 'Economics (LCOE, NPV, payback) are browser-side demo formulas, not model output', 'State potential and installed capacity are NISE/MNRE published totals', 'District CUF choropleth: predicted ±90% interval, measured label where one exists (scripts/export_district_cuf_frontend.py)'],
    },
  ];

  return (
    <div className="min-h-screen pt-24 pb-16 bg-space-deep">
      <div className="container-custom">
        <SectionTitle
          title="Methodology"
          subtitle="A transparent, reproducible pipeline: CEA plant CUF labels, leave-one-district-out CV, and a physics-baseline serving gate"
        />

        {/* Pipeline Visualization */}
        <div className="relative mb-20">
          {/* Vertical line */}
          <div className="absolute left-6 md:left-1/2 top-0 bottom-0 w-0.5 bg-space-border md:-translate-x-0.5" />

          {pipelineStages.map((stage, i) => (
            <motion.div
              key={stage.title}
              initial={{ opacity: 0, x: i % 2 === 0 ? -30 : 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.15 }}
              className={`relative flex items-start gap-6 mb-12 ${
                i % 2 === 0 ? 'md:flex-row' : 'md:flex-row-reverse'
              }`}
            >
              {/* Timeline dot */}
              <div
                className="absolute left-6 md:left-1/2 w-4 h-4 rounded-full -translate-x-1/2 z-10"
                style={{ backgroundColor: stage.color, boxShadow: `0 0 12px ${stage.color}60` }}
              />

              {/* Content */}
              <div className={`ml-14 md:ml-0 md:w-[45%] ${i % 2 === 0 ? 'md:pr-12 md:text-right' : 'md:pl-12'}`}>
                <GlassCard hover={false}>
                  <div className="flex items-center gap-3 mb-3" style={{ justifyContent: i % 2 === 0 ? 'flex-end' : 'flex-start' }}>
                    <span className="text-xs font-mono px-2 py-1 rounded-full" style={{ color: stage.color, backgroundColor: `${stage.color}15` }}>
                      {stage.time}
                    </span>
                  </div>
                  <h3 className="font-display font-bold text-xl text-txt-primary mb-3" style={{ color: stage.color }}>
                    {stage.title}
                  </h3>
                  <ul className={`space-y-1.5 ${i % 2 === 0 ? 'md:text-right' : ''}`}>
                    {stage.items.map((item, j) => (
                      <li key={j} className="text-txt-dim text-base flex items-start gap-2" style={{ justifyContent: i % 2 === 0 ? 'flex-end' : 'flex-start' }}>
                        <span className="w-1 h-1 rounded-full mt-2 flex-shrink-0" style={{ backgroundColor: stage.color, order: i % 2 === 0 ? 1 : 0 }} />
                        {item}
                      </li>
                    ))}
                  </ul>
                </GlassCard>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Model Architecture */}
        <SectionTitle title="Model Architecture" subtitle="Six candidates were trained; only models that beat the pvlib C0 physics baseline can be served" gradient="tech" />

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-16">
          {modelCards.map((model, i) => (
            <motion.div
              key={model.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
            >
              <GlassCard className="h-full text-center">
                <div
                  className="w-16 h-16 rounded-2xl mx-auto mb-4 flex items-center justify-center font-display font-bold text-sm"
                  style={{ backgroundColor: `${model.color}15`, color: model.color, border: `1px solid ${model.color}30` }}
                >
                  {model.badge}
                </div>
                <h3 className="font-display font-semibold text-txt-primary text-xl mb-2">{model.name}</h3>
                <p className="text-sm font-mono text-txt-dim mb-3 bg-space-surface px-3 py-1 rounded-lg inline-block">{model.params}</p>
                <p className="text-txt-secondary text-base">{model.strength}</p>
              </GlassCard>
            </motion.div>
          ))}
        </div>

        {/* Feature Explorer */}
        <SectionTitle title="Feature Schema" subtitle={`The model trains on ${KEY_METRICS.featuresUsed} raw + engineered features; the explorer below is an illustrative catalog of ${featureDefinitions.length} named features, not the training matrix`} gradient="mixed" />

        {/* Category tabs */}
        <div className="flex flex-wrap gap-2 mb-6">
          <button
            onClick={() => setSelectedCategory('all')}
            className={`px-4 py-2 rounded-lg text-sm transition-all ${
              selectedCategory === 'all' ? 'bg-solar-gold/20 text-solar-gold border border-solar-gold/30' : 'text-txt-dim border border-space-border hover:text-txt-primary'
            }`}
          >
            All ({featureDefinitions.length})
          </button>
          {FEATURE_CATEGORIES.map(cat => (
            <button
              key={cat.key}
              onClick={() => setSelectedCategory(cat.key)}
              className={`px-4 py-2 rounded-lg text-sm transition-all flex items-center gap-1.5 ${
                selectedCategory === cat.key
                  ? 'border text-txt-primary'
                  : 'text-txt-dim border border-space-border hover:text-txt-primary'
              }`}
              style={selectedCategory === cat.key ? { backgroundColor: `${cat.color}15`, borderColor: `${cat.color}40`, color: cat.color } : {}}
            >
              <span>{cat.icon}</span>
              {cat.label}
            </button>
          ))}
        </div>

        {/* Search */}
        <input
          type="text"
          placeholder="Search features..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full md:w-80 px-4 py-2 mb-6 text-sm bg-space-surface border border-space-border rounded-lg text-txt-primary placeholder:text-txt-dim focus:outline-none focus:border-solar-gold/50 transition-colors"
        />

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mb-16">
          {filteredFeatures.map((f, i) => {
            const cat = FEATURE_CATEGORIES.find(c => c.key === f.category);
            return (
              <motion.div
                key={f.id}
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: Math.min(i * 0.03, 0.3) }}
              >
                <GlassCard className="!p-4 h-full">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-sm">{cat?.icon}</span>
                      <span className="font-mono text-xs px-2 py-0.5 rounded" style={{ backgroundColor: `${cat?.color}15`, color: cat?.color }}>
                        {f.name}
                      </span>
                    </div>
                    <span className={`text-xs px-2 py-0.5 rounded ${
                      f.importance === 'Critical' ? 'bg-red-500/15 text-red-400' :
                      f.importance === 'High' ? 'bg-orange-500/15 text-orange-400' :
                      f.importance === 'Medium' ? 'bg-blue-500/15 text-blue-400' :
                      'bg-gray-500/15 text-gray-400'
                    }`}>
                      {f.importance}
                    </span>
                  </div>
                  <h4 className="text-base font-semibold text-txt-primary mb-1">{f.fullName}</h4>
                  <p className="text-sm text-txt-dim mb-2">{f.description}</p>
                  <div className="flex justify-between text-sm text-txt-dim">
                    <span>Range: <span className="text-txt-secondary font-mono">{f.range}</span></span>
                    <span>Unit: <span className="text-txt-secondary">{f.unit}</span></span>
                  </div>
                </GlassCard>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default Methodology;
