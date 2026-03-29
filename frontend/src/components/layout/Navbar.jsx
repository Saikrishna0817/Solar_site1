import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { NAV_LINKS } from '../../data/constants';

const Navbar = () => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    setMobileOpen(false);
  }, [location]);

  return (
    <motion.nav
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-700 ${
        scrolled
          ? 'glass-strong shadow-lg shadow-black/20'
          : 'bg-transparent'
      }`}
    >
      {/* Top accent line */}
      <div className="absolute top-0 left-0 right-0 h-[1px]">
        <div
          className="h-full transition-opacity duration-700"
          style={{
            background: 'linear-gradient(90deg, transparent 5%, rgba(245,166,35,0.3) 30%, rgba(6,182,212,0.15) 70%, transparent 95%)',
            opacity: scrolled ? 1 : 0,
          }}
        />
      </div>

      <div className="container-custom flex items-center justify-between h-16 md:h-20">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-3 group">
          <motion.div
            className="relative w-9 h-9 md:w-10 md:h-10"
            whileHover={{ rotate: 15, scale: 1.05 }}
            transition={{ type: 'spring', stiffness: 300, damping: 15 }}
          >
            <div className="absolute inset-0 rounded-xl bg-gradient-solar opacity-90 group-hover:opacity-100 transition-opacity" />
            <div className="absolute inset-0 rounded-xl bg-gradient-solar blur-md opacity-0 group-hover:opacity-40 transition-opacity" />
            <div className="absolute inset-0 flex items-center justify-center text-space-deep font-bold text-lg">
              ☀
            </div>
          </motion.div>
          <div className="flex flex-col">
            <span className="font-display font-bold text-xl md:text-2xl text-txt-primary leading-tight">
              Solar<span className="gradient-text-solar">Site</span>
            </span>
            <span className="text-[11px] text-txt-dim tracking-widest uppercase hidden sm:block">
              India • AI-Powered
            </span>
          </div>
        </Link>

        {/* Desktop Nav */}
        <div className="hidden md:flex items-center gap-0.5">
          {NAV_LINKS.map(link => (
            <Link
              key={link.path}
              to={link.path}
              className={`relative px-4 py-2 text-base font-medium rounded-lg transition-all duration-300 ${
                location.pathname === link.path
                  ? 'text-solar-gold'
                  : 'text-txt-secondary hover:text-txt-primary hover:bg-space-light/30'
              }`}
            >
              {link.label}
              {location.pathname === link.path && (
                <motion.div
                  layoutId="nav-indicator"
                  className="absolute bottom-0 left-3 right-3 h-[2px] rounded-full"
                  style={{ background: 'linear-gradient(90deg, #F5A623, #E8590C)' }}
                  transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                />
              )}
            </Link>
          ))}
        </div>

        {/* CTA Button */}
        <div className="hidden md:block">
          <Link
            to="/dashboard"
            className="btn-solar text-sm !py-2.5 !px-5 rounded-xl inline-flex items-center gap-2"
          >
            <span>Explore Map</span>
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </Link>
        </div>

        {/* Mobile Toggle */}
        <motion.button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="md:hidden p-2 text-txt-secondary hover:text-txt-primary transition-colors"
          whileTap={{ scale: 0.9 }}
        >
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            {mobileOpen ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </motion.button>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="md:hidden glass-strong border-t border-space-border overflow-hidden"
          >
            <div className="container-custom py-4 flex flex-col gap-1">
              {NAV_LINKS.map((link, i) => (
                <motion.div
                  key={link.path}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                >
                  <Link
                    to={link.path}
                    className={`px-4 py-3 rounded-lg text-sm font-medium transition-colors block ${
                      location.pathname === link.path
                        ? 'text-solar-gold bg-space-light/50'
                        : 'text-txt-secondary hover:text-txt-primary hover:bg-space-light/30'
                    }`}
                  >
                    {link.label}
                  </Link>
                </motion.div>
              ))}
              <Link
                to="/dashboard"
                className="btn-solar text-sm text-center mt-2"
              >
                Explore Map →
              </Link>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  );
};

export default Navbar;
