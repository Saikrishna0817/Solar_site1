import { motion } from 'framer-motion';
import GlassCard from '../components/ui/GlassCard';
import SectionTitle from '../components/ui/SectionTitle';
import GradientButton from '../components/ui/GradientButton';

const About = () => {
  const techStack = [
    { category: 'Frontend', items: ['React 18', 'Three.js / R3F', 'Framer Motion', 'Recharts', 'Leaflet', 'Tailwind CSS 3'] },
    { category: 'Backend', items: ['Python 3.10+', 'FastAPI', 'scikit-learn', 'XGBoost', 'SHAP', 'Pandas/NumPy'] },
    { category: 'Data Sources', items: ['NASA POWER', 'SRTM DEM', 'ISRO Bhuvan', 'CEA/PGCIL', 'IMD Weather', 'Census India'] },
    { category: 'ML Models', items: ['Random Forest', 'XGBoost', 'Gradient Boosting', 'Weighted Ensemble', 'SHAP Explainability', '5-Fold CV'] },
  ];

  const researchHighlights = [
    { label: 'Training Samples', value: '127 solar plants' },
    { label: 'Feature Dimensions', value: '42 input features' },
    { label: 'Model Accuracy', value: 'R² = 0.88' },
    { label: 'Prediction Error', value: 'MAPE = 11.5%' },
    { label: 'Coverage', value: '28 states / UTs' },
    { label: 'Sites Screened', value: '30,000+ sites' },
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
            India's ambitious target of 500 GW renewable energy capacity by 2030 requires identifying thousands
            of optimal solar farm locations across the country. Traditional site selection methods are slow,
            expensive, and subjective — taking 6-12 months and ₹50-100 lakhs per site assessment, with a 70% failure rate.
          </p>
          <p className="text-txt-secondary leading-relaxed">
            <strong className="text-txt-primary">SolarSite-India</strong> uses a machine learning ensemble model
            trained on 127 operational solar plants to predict site suitability across 30,000+ potential locations.
            Our platform enables data-driven decision-making in minutes rather than months, at zero cost,
            with transparent AI explanations for every recommendation.
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
              SolarSite-India: AI-Optimized Solar Energy Site Selection Using Multi-Model Ensemble Learning
            </h3>
            <p className="text-txt-dim text-sm mb-6">
              A comprehensive machine learning framework for identifying optimal solar deployment
              locations across India using 42 geospatial, climatic, and economic features.
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
                  Weighted ensemble (RF + XGBoost + GBM) achieving R² = 0.88
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-solar-gold mt-0.5">•</span>
                  SHAP-based explainability for transparent AI decisions
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-solar-gold mt-0.5">•</span>
                  Nationwide assessment of 30,000+ utility-scale sites
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
