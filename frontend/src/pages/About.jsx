import { motion } from 'framer-motion';
import GlassCard from '../components/ui/GlassCard';
import SectionTitle from '../components/ui/SectionTitle';
import GradientButton from '../components/ui/GradientButton';
import { KEY_METRICS } from '../data/constants';

const About = () => {
  const techStack = [
    { category: 'Frontend', items: ['React 18', 'Three.js / R3F', 'Framer Motion', 'Recharts', 'Leaflet', 'Tailwind CSS 3'] },
    { category: 'Backend', items: ['Python 3.10+', 'FastAPI', 'scikit-learn', 'Ridge Regression', 'SHAP', 'Pandas/NumPy'] },
    { category: 'Data Sources', items: ['NASA POWER', 'SRTM DEM', 'ISRO Bhuvan', 'CEA/PGCIL', 'IMD Weather', 'Census India'] },
    { category: 'ML Models', items: ['Ridge Regression', 'Random Forest', 'LASSO', 'Weighted Composite Index', 'SHAP Explainability', '5-Fold CV'] },
  ];

  const researchHighlights = [
    { label: 'Training Samples', value: `${KEY_METRICS.sitesAnalyzed} solar plants` },
    { label: 'Feature Dimensions', value: `${KEY_METRICS.featuresUsed} input features` },
    { label: 'Model Type', value: 'Ridge + WCI' },
    { label: 'Districts Analyzed', value: `${KEY_METRICS.districtsAnalyzed} districts` },
    { label: 'Coverage', value: `${KEY_METRICS.statesWithPlants} states` },
    { label: 'Tracked Capacity', value: `${KEY_METRICS.totalCapacityGW} GW` },
    { label: 'Grid Resolution', value: '5 km × 5 km' },
    { label: 'Temporal Span', value: '20-year weather data' },
  ];

  return (
    <div className="min-h-screen pt-24 pb-16 bg-space-deep">
      <div className="container-custom">
        <SectionTitle
          title="About SolarSite-India"
          subtitle="An AI-powered platform for accelerating India's solar energy transition"
        />

        {/* Mission */}
        <GlassCard hover={false} className="mb-10 max-w-4xl mx-auto">
          <h3 className="font-display font-bold text-2xl text-txt-primary mb-4 gradient-text-solar">Our Mission</h3>
          <p className="text-txt-secondary text-base leading-relaxed mb-4">
            India's ambitious target of {KEY_METRICS.targetGW} GW renewable energy capacity by {KEY_METRICS.targetYear} requires identifying thousands
            of optimal solar farm locations across the country. Traditional site selection methods are slow,
            expensive, and subjective — taking 6-12 months and ₹50-100 lakhs per site assessment, with a 70% failure rate.
          </p>
          <p className="text-txt-secondary leading-relaxed">
            <strong className="text-txt-primary">SolarSite-India</strong> uses a weighted composite index and Ridge regression model
            trained on real CUF data from {KEY_METRICS.sitesAnalyzed} operational solar plants to evaluate solar potential across {KEY_METRICS.districtsAnalyzed} districts.
            Our platform enables data-driven decision-making in minutes rather than months, at zero cost,
            with transparent feature importance explanations for every recommendation.
          </p>
        </GlassCard>

        {/* Research Highlights */}
        <SectionTitle title="Research Highlights" gradient="tech" />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-14">
          {researchHighlights.map((item, i) => (
            <motion.div
              key={item.label}
              initial={{ opacity: 0, y: 15 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.05 }}
            >
              <GlassCard className="text-center !p-4">
                <p className="font-display font-bold text-xl text-solar-gold mb-1">{item.value}</p>
                <p className="text-txt-dim text-sm">{item.label}</p>
              </GlassCard>
            </motion.div>
          ))}
        </div>

        {/* Tech Stack */}
        <SectionTitle title="Technology Stack" gradient="mixed" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-14">
          {techStack.map((stack, i) => (
            <motion.div
              key={stack.category}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
            >
              <GlassCard className="h-full">
                <h3 className="font-display font-semibold text-txt-primary mb-4 text-sm uppercase tracking-wider">
                  {stack.category}
                </h3>
                <div className="flex flex-wrap gap-2">
                  {stack.items.map(item => (
                    <span key={item} className="px-2.5 py-1 text-xs font-mono text-txt-secondary bg-space-surface border border-space-border rounded-md">
                      {item}
                    </span>
                  ))}
                </div>
              </GlassCard>
            </motion.div>
          ))}
        </div>

        {/* Paper Info */}
        <SectionTitle title="Research Paper" gradient="solar" />
        <GlassCard hover={false} className="max-w-3xl mx-auto mb-12">
          <div className="text-center">
            <h3 className="font-display font-bold text-xl text-txt-primary mb-3">
              SolarSite-India: AI-Optimized Solar Energy Site Selection Using Real-Plant CUF Data
            </h3>
            <p className="text-txt-dim text-sm mb-6">
              A framework for identifying optimal solar deployment locations across India using 42 geospatial,
              climatic, and economic features, trained on real Capacity Utilization Factor (CUF) data from
              {KEY_METRICS.sitesAnalyzed} operational solar plants.
            </p>

            <div className="glass p-4 rounded-lg mb-6 text-left">
              <p className="text-txt-dim text-xs mb-2 uppercase tracking-wider">Key Contributions</p>
              <ul className="space-y-2 text-txt-secondary text-base">
                <li className="flex items-start gap-2">
                  <span className="text-solar-gold mt-0.5">•</span>
                  42-feature multi-dimensional site characterization schema
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-solar-gold mt-0.5">•</span>
                  Real CUF target from {KEY_METRICS.sitesAnalyzed} operational solar plants (CEA data)
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-solar-gold mt-0.5">•</span>
                  Ridge regression + RF feature importance for transparent scoring
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-solar-gold mt-0.5">•</span>
                  District-level assessment across {KEY_METRICS.districtsAnalyzed} districts in {KEY_METRICS.statesWithPlants} states
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-solar-gold mt-0.5">•</span>
                  Interactive visualization platform for stakeholder engagement
                </li>
              </ul>
            </div>

            <div className="flex justify-center gap-4">
              <GradientButton variant="solar" size="md">
                Download Paper (PDF)
              </GradientButton>
              <GradientButton to="/results" variant="outline" size="md">
                View Results →
              </GradientButton>
            </div>
          </div>
        </GlassCard>

        {/* Contact / CTA */}
        <div className="text-center py-12">
          <p className="text-txt-dim text-sm mb-4">
            Built with ♥ for India's sustainable energy future
          </p>
          <div className="flex justify-center gap-4">
            <GradientButton to="/dashboard" variant="solar">
              Explore Dashboard →
            </GradientButton>
            <GradientButton to="/methodology" variant="outline">
              View Methodology
            </GradientButton>
          </div>
        </div>
      </div>
    </div>
  );
};

export default About;
