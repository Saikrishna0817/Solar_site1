import { Link } from 'react-router-dom';
import { KEY_METRICS } from '../../data/constants';

const Footer = () => {
  return (
    <footer className="relative border-t border-space-border bg-space-deep">
      <div className="divider-glow" />
      <div className="container-custom py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="md:col-span-1">
            <Link to="/" className="flex items-center gap-3 mb-4">
              <div className="w-9 h-9 rounded-xl bg-gradient-solar flex items-center justify-center text-space-deep font-bold">
                ☀
              </div>
              <span className="font-display font-bold text-xl text-txt-primary">
                Solar<span className="gradient-text-solar">Site</span>
              </span>
            </Link>
            <p className="text-txt-dim text-base leading-relaxed">
              AI-powered platform identifying optimal solar energy deployment locations across India,
              supporting the 500 GW renewable energy target by 2030.
            </p>
          </div>

          {/* Navigation */}
          <div>
            <h4 className="font-display font-semibold text-txt-primary mb-4 text-base uppercase tracking-wider">Platform</h4>
            <div className="flex flex-col gap-2">
              <Link to="/dashboard" className="text-txt-dim hover:text-solar-gold text-base transition-colors link-underline">Dashboard</Link>
              <Link to="/analyze" className="text-txt-dim hover:text-solar-gold text-base transition-colors link-underline">Site Analysis</Link>
              <Link to="/methodology" className="text-txt-dim hover:text-solar-gold text-base transition-colors link-underline">Methodology</Link>
              <Link to="/results" className="text-txt-dim hover:text-solar-gold text-base transition-colors link-underline">Results</Link>
            </div>
          </div>

          {/* Research */}
          <div>
            <h4 className="font-display font-semibold text-txt-primary mb-4 text-base uppercase tracking-wider">Research</h4>
            <div className="flex flex-col gap-2">
              <span className="text-txt-dim text-base">{KEY_METRICS.modelType} model</span>
              <span className="text-txt-dim text-base">{KEY_METRICS.featuresUsed}-Feature Schema</span>
              <span className="text-txt-dim text-base">{KEY_METRICS.sitesAnalyzed} Training Plants</span>
              <span className="text-txt-dim text-base">{KEY_METRICS.evaluationMethod}</span>
            </div>
          </div>

          {/* Tech */}
          <div>
            <h4 className="font-display font-semibold text-txt-primary mb-4 text-base uppercase tracking-wider">Technology</h4>
            <div className="flex flex-wrap gap-2">
              {['React', 'Three.js', 'Leaflet', 'XGBoost', 'FastAPI', 'Python'].map(tech => (
                <span key={tech} className="px-2.5 py-1 text-xs font-mono text-txt-dim bg-space-surface border border-space-border rounded-md">
                  {tech}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-10 pt-5 border-t border-space-border flex flex-col sm:flex-row justify-between items-center gap-4">
          <p className="text-txt-dim text-sm">
            © 2025 SolarSite-India. Research project for sustainable energy deployment.
          </p>
          <div className="flex items-center gap-4">
            <span className="text-txt-dim text-xs flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-success animate-pulse" />
              System Online
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
