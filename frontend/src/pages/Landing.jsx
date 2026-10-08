import { Suspense, lazy } from 'react';
import { motion } from 'framer-motion';
import GlassCard from '../components/ui/GlassCard';
import GradientButton from '../components/ui/GradientButton';
import AnimatedCounter from '../components/ui/AnimatedCounter';
import SectionTitle from '../components/ui/SectionTitle';
import SuitabilityCalculator from '../components/calculator/SuitabilityCalculator';
import { KEY_METRICS } from '../data/constants';

const SolarGlobe = lazy(() => import('../components/three/SolarGlobe'));
const ParticleField = lazy(() => import('../components/three/ParticleField'));

const fadeInUp = {
  initial: { opacity: 0, y: 40 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: '-80px' },
  transition: { duration: 0.7 },
};

const stagger = {
  initial: { opacity: 0 },
  whileInView: { opacity: 1 },
  viewport: { once: true },
  transition: { staggerChildren: 0.1 },
};

const Landing = () => {
  const heroStats = [
    { value: KEY_METRICS.targetGW, suffix: ' GW', label: `National Target by ${KEY_METRICS.targetYear}` },
    { value: KEY_METRICS.sitesAnalyzed, suffix: '', label: 'Plants with CUF Labels' },
    { value: KEY_METRICS.districtsAnalyzed, suffix: '', label: 'Districts Analyzed' },
    { value: KEY_METRICS.featuresUsed, suffix: '', label: 'Input Features' },
  ];

  const problemCards = [
    { before: 'Manual review', after: 'Automated', label: 'Site Assessment', icon: '⏱️' },
    { before: 'Field surveys', after: 'Browser-based', label: 'Assessment Cost', icon: '💰' },
    { before: 'Subjective calls', after: 'Data-Driven', label: 'Decision Quality', icon: '📊' },
  ];

  const pipelineSteps = [
    { title: 'Data Collection', description: `${KEY_METRICS.featuresUsed} features from satellite, weather, grid, and land sources across ${KEY_METRICS.districtsAnalyzed} districts`, icon: '📡', color: '#06B6D4' },
    { title: 'Preprocessing', description: 'Collinear-feature drop, then leakage-free imputation, winsorization, and scaling fitted on training folds only', icon: '⚙️', color: '#8B5CF6' },
    { title: 'Real CUF Target', description: `CEA-actual CUF from ${KEY_METRICS.sitesAnalyzed} operational solar plants as the ML training target`, icon: '🧠', color: '#F5A623' },
    { title: 'Model Training', description: 'A single elastic-net regression, with RFE feature selection re-fitted inside every cross-validation fold', icon: '📈', color: '#10B981' },
    { title: 'Gate & Serving', description: 'The API serves the model only when its leave-one-district-out CV MAE beats the pvlib physics baseline', icon: '🏆', color: '#E8590C' },
  ];

  const features = [
    { title: 'Interactive Map', description: 'Explore solar sites and districts across Telangana + Andhra Pradesh with real-time filtering', icon: '🗺️' },
    { title: 'Real CUF Data', description: `Trained on CEA-actual CUF from ${KEY_METRICS.sitesAnalyzed} operational plants (Telangana + Andhra Pradesh), not simulated data`, icon: '🤖' },
    { title: 'Economic Analysis', description: 'On-page LCOE, NPV, and payback calculators — demo estimates, not model output', icon: '💹' },
    { title: 'Transparent Scoring', description: 'SHAP feature attributions for every served prediction, instead of a black box', icon: '🔍' },
    { title: 'Multi-Scale Analysis', description: 'Utility-scale plants and district-level solar potential assessment', icon: '🏗️' },
    { title: 'Research Ready', description: 'Publication-quality charts and export capabilities', icon: '📄' },
  ];

  return (
    <div className="overflow-hidden">
      {/* ═══════════ HERO SECTION ═══════════ */}
      <section className="relative min-h-screen flex items-center justify-center bg-gradient-hero overflow-hidden">
        {/* Particle background */}
        <Suspense fallback={null}>
          <ParticleField />
        </Suspense>

        <div className="container-custom relative z-10 grid grid-cols-1 lg:grid-cols-2 gap-8 items-center pt-24 pb-12">
          {/* Left: Text */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <motion.div
              className="flex items-center gap-2 mb-5"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.5 }}
            >
              <span className="w-2.5 h-2.5 rounded-full bg-success animate-pulse" />
              <span className="text-sm font-mono text-txt-dim uppercase tracking-widest">Data-Driven Solar Intelligence</span>
            </motion.div>

            <h1 className="font-display font-bold text-5xl md:text-6xl lg:text-7xl leading-[1.08] mb-6">
              Finding India's
              <br />
              <span className="gradient-text-solar">Optimal Solar</span>
              <br />
              Destinations
            </h1>

            <p className="text-txt-secondary text-lg md:text-xl lg:text-2xl mb-8 max-w-xl leading-relaxed">
              Machine learning trained on real plant performance data scores district-level solar potential across
              Telangana and Andhra Pradesh,
              supporting the <span className="text-solar-gold font-semibold">500 GW renewable target by 2030</span>.
            </p>

            <motion.div
              className="flex flex-wrap gap-3 mb-10"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.5 }}
            >
              <GradientButton to="/dashboard" variant="solar" size="lg">
                Explore the Map
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </GradientButton>
              <GradientButton to="/methodology" variant="outline" size="lg">
                View Research
              </GradientButton>
            </motion.div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {heroStats.map((stat, i) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  transition={{ delay: 0.7 + i * 0.12, type: 'spring', stiffness: 200 }}
                  className="text-center glass rounded-xl py-3 px-2"
                >
                  <div className="font-display font-bold text-2xl md:text-3xl text-txt-primary">
                    <AnimatedCounter end={stat.value} duration={2000} suffix={stat.suffix} />
                  </div>
                  <p className="text-sm text-txt-dim mt-1">{stat.label}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Right: 3D Globe */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8, rotateY: -15 }}
            animate={{ opacity: 1, scale: 1, rotateY: 0 }}
            transition={{ duration: 1.2, delay: 0.4, ease: [0.22, 1, 0.36, 1] }}
            className="hidden lg:block h-[500px] relative"
          >
            <Suspense fallback={
              <div className="w-full h-full flex items-center justify-center">
                <div className="w-32 h-32 rounded-full bg-gradient-solar opacity-20 animate-pulse" />
              </div>
            }>
              <SolarGlobe className="w-full h-full" />
            </Suspense>
          </motion.div>
        </div>

        {/* Scroll indicator */}
        <motion.div
          className="absolute bottom-8 left-1/2 -translate-x-1/2"
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
        >
          <div className="flex flex-col items-center gap-2">
            <span className="text-2xs text-txt-dim uppercase tracking-widest">Scroll</span>
            <svg className="w-5 h-5 text-txt-dim" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
            </svg>
          </div>
        </motion.div>
      </section>

      {/* ═══════════ PROBLEM/SOLUTION ═══════════ */}
      <section className="section-padding bg-space-deep relative">
        <div className="container-custom">
          <SectionTitle
            title="Why SolarSite-India?"
            subtitle="Traditional solar site selection is slow, expensive, and unreliable. Our AI changes that."
            gradient="tech"
          />

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {problemCards.map((card, i) => (
              <motion.div
                key={card.label}
                initial={{ opacity: 0, y: 30, scale: 0.95 }}
                whileInView={{ opacity: 1, y: 0, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.15, type: 'spring', stiffness: 200 }}
              >
                <GlassCard className="text-center h-full">
                  <motion.span
                    className="text-5xl mb-4 block"
                    whileHover={{ scale: 1.2, rotate: [0, -10, 10, 0] }}
                    transition={{ duration: 0.4 }}
                  >
                    {card.icon}
                  </motion.span>
                  <p className="text-txt-dim text-base mb-2">{card.label}</p>
                  <div className="flex items-center justify-center gap-4 my-4">
                    <div>
                      <p className="text-red-400 font-mono text-lg line-through opacity-70">{card.before}</p>
                      <p className="text-sm text-txt-dim">Before</p>
                    </div>
                    <motion.svg
                      className="w-7 h-7 text-solar-gold flex-shrink-0"
                      fill="none" viewBox="0 0 24 24" stroke="currentColor"
                      animate={{ x: [0, 4, 0] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </motion.svg>
                    <div>
                      <p className="text-success font-semibold text-lg">{card.after}</p>
                      <p className="text-sm text-txt-dim">After</p>
                    </div>
                  </div>
                </GlassCard>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════════ HOW IT WORKS ═══════════ */}
      <section className="section-padding relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-hero opacity-50" />
        <div className="container-custom relative z-10">
          <SectionTitle
            title="How It Works"
            subtitle={`A five-stage pipeline: ${KEY_METRICS.featuresUsed} features per site into a single trained model, served only when it beats a physics baseline`}
            gradient="solar"
          />

          <div className="relative">
            {/* Connection line */}
            <div className="hidden lg:block absolute top-1/2 left-0 right-0 h-0.5 bg-space-border -translate-y-1/2" />

            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
              {pipelineSteps.map((step, i) => (
                <motion.div
                  key={step.title}
                  initial={{ opacity: 0, y: 30, scale: 0.9 }}
                  whileInView={{ opacity: 1, y: 0, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.12, type: 'spring', stiffness: 200, damping: 20 }}
                  className="relative"
                >
                  <GlassCard className="text-center h-full relative z-10">
                    {/* Step number */}
                    <motion.div
                      className="w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold mx-auto mb-3"
                      style={{ background: `${step.color}20`, color: step.color, border: `1px solid ${step.color}40` }}
                      whileHover={{ scale: 1.15, rotate: 360 }}
                      transition={{ duration: 0.5 }}
                    >
                      {i + 1}
                    </motion.div>
                    <span className="text-3xl mb-2 block">{step.icon}</span>
                    <h3 className="font-display font-semibold text-txt-primary text-base mb-2">{step.title}</h3>
                    <p className="text-txt-dim text-sm leading-relaxed">{step.description}</p>
                  </GlassCard>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════ FEATURES GRID ═══════════ */}
      <section className="section-padding bg-space-deep">
        <div className="container-custom">
          <SectionTitle
            title="Platform Features"
            subtitle="Everything you need for solar site assessment, from map exploration to economic analysis"
            gradient="mixed"
          />

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {features.map((feat, i) => (
              <motion.div
                key={feat.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.08 }}
              >
                <GlassCard className="h-full group">
                  <motion.span
                    className="text-4xl mb-4 block"
                    whileHover={{ scale: 1.25, y: -4 }}
                    transition={{ type: 'spring', stiffness: 300 }}
                  >
                    {feat.icon}
                  </motion.span>
                  <h3 className="font-display font-semibold text-txt-primary text-lg mb-2 group-hover:text-solar-gold transition-colors duration-300">{feat.title}</h3>
                  <p className="text-txt-dim text-base leading-relaxed">{feat.description}</p>
                </GlassCard>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════════ INTERACTIVE CALCULATOR ═══════════ */}
      <section className="section-padding relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-hero opacity-30" />
        <div className="container-custom relative z-10">
          <SectionTitle
            title="Try It Yourself"
            subtitle="Adjust the parameters below to see how different factors affect solar site suitability"
            gradient="solar"
          />
          <div className="max-w-5xl mx-auto">
            <SuitabilityCalculator />
          </div>
        </div>
      </section>

      {/* ═══════════ CTA ═══════════ */}
      <section className="py-20 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-solar-gold/5 via-transparent to-tech-cyan/5" />
        {/* Decorative orbs */}
        <motion.div
          className="absolute top-10 left-[15%] w-48 h-48 rounded-full bg-solar-gold/5 blur-3xl"
          animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.5, 0.3] }}
          transition={{ duration: 6, repeat: Infinity }}
        />
        <motion.div
          className="absolute bottom-10 right-[15%] w-48 h-48 rounded-full bg-tech-cyan/5 blur-3xl"
          animate={{ scale: [1.2, 1, 1.2], opacity: [0.3, 0.5, 0.3] }}
          transition={{ duration: 6, repeat: Infinity, delay: 3 }}
        />
        <div className="container-custom relative z-10 text-center">
          <motion.div {...fadeInUp}>
            <h2 className="font-display font-bold text-3xl md:text-5xl gradient-text-solar mb-5">
              Ready to Explore India's Solar Potential?
            </h2>
            <p className="text-txt-secondary text-lg md:text-xl mb-8 max-w-xl mx-auto">
              Dive into the interactive dashboard and discover optimal solar sites backed by real-world plant performance data.
            </p>
            <motion.div
              className="flex justify-center gap-4"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
            >
              <GradientButton to="/dashboard" variant="solar" size="lg">
                Open Dashboard →
              </GradientButton>
              <GradientButton to="/results" variant="outline" size="lg">
                View Results
              </GradientButton>
            </motion.div>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default Landing;
