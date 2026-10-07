import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { Component } from 'react';
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import SiteAnalysis from './pages/SiteAnalysis';
import Methodology from './pages/Methodology';
import Results from './pages/Results';
import About from './pages/About';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, info) {
    console.error('App ErrorBoundary caught:', error, info);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '40px', textAlign: 'center', color: '#E8F4FD', background: '#0A0E1A', minHeight: '100vh' }}>
          <h1 style={{ color: '#F5A623', marginBottom: '16px' }}>Something went wrong</h1>
          <pre style={{ textAlign: 'left', fontSize: '12px', color: '#EF4444', maxWidth: '600px', margin: '0 auto', overflow: 'auto' }}>
            {this.state.error?.toString()}
          </pre>
        </div>
      );
    }
    return this.props.children;
  }
}

// ponytail: runtime propTypes dropped (children: node x2 only); add TS props when a type bug bites.

const PageTransition = ({ children }) => (
  <motion.div
    initial={{ opacity: 0, y: 8 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -8 }}
    transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
  >
    {children}
  </motion.div>
);

const AnimatedRoutes = () => {
  const location = useLocation();
  const isDashboard = location.pathname === '/dashboard';

  return (
    <>
      <Navbar />
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<PageTransition><Landing /></PageTransition>} />
          <Route path="/dashboard" element={<PageTransition><Dashboard /></PageTransition>} />
          <Route path="/analyze" element={<PageTransition><SiteAnalysis /></PageTransition>} />
          <Route path="/site/:id" element={<PageTransition><SiteAnalysis /></PageTransition>} />
          <Route path="/methodology" element={<PageTransition><Methodology /></PageTransition>} />
          <Route path="/results" element={<PageTransition><Results /></PageTransition>} />
          <Route path="/about" element={<PageTransition><About /></PageTransition>} />
        </Routes>
      </AnimatePresence>
      {!isDashboard && <Footer />}
    </>
  );
};

function App() {
  return (
    <BrowserRouter>
      <ErrorBoundary>
        <AnimatedRoutes />
      </ErrorBoundary>
    </BrowserRouter>
  );
}

export default App;
