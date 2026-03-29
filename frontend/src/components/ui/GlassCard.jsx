import { motion } from 'framer-motion';

const GlassCard = ({ children, className = '', hover = true, glow = false, accent = null, ...props }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-50px' }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      whileHover={hover ? { y: -4, scale: 1.005, transition: { duration: 0.25 } } : undefined}
      className={`glass-card p-5 card-shimmer ${hover ? '' : 'hover:transform-none hover:border-space-border hover:shadow-none'} ${
        glow ? 'shadow-glow-gold' : ''
      } ${className}`}
      style={accent ? { borderColor: `${accent}25` } : undefined}
      {...props}
    >
      {/* Subtle top edge highlight */}
      <div
        className="absolute top-0 left-[10%] right-[10%] h-[1px] rounded-full opacity-40"
        style={{
          background: accent
            ? `linear-gradient(90deg, transparent, ${accent}60, transparent)`
            : 'linear-gradient(90deg, transparent, rgba(245,166,35,0.15), transparent)',
        }}
      />
      {/* Corner accent glow */}
      <div
        className="absolute -top-12 -right-12 w-24 h-24 rounded-full pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-500"
        style={{
          background: `radial-gradient(circle, ${accent || 'rgba(245,166,35,0.06)'}, transparent 70%)`,
        }}
      />
      {children}
    </motion.div>
  );
};

export default GlassCard;
