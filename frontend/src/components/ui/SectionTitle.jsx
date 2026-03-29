import { motion } from 'framer-motion';

const SectionTitle = ({ title, subtitle, gradient = 'solar', align = 'center', className = '' }) => {
  const gradientClass = {
    solar: 'gradient-text-solar',
    tech: 'gradient-text-tech',
    mixed: 'gradient-text-mixed',
  }[gradient];

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-80px' }}
      transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
      className={`mb-10 md:mb-12 ${align === 'center' ? 'text-center' : 'text-left'} ${className}`}
    >
      <motion.h2
        className={`font-display font-bold text-3xl md:text-4xl lg:text-5xl mb-4 ${gradientClass}`}
        initial={{ letterSpacing: '-0.02em' }}
        whileInView={{ letterSpacing: '-0.01em' }}
        viewport={{ once: true }}
        transition={{ duration: 1.2, ease: 'easeOut' }}
      >
        {title}
      </motion.h2>
      {subtitle && (
        <motion.p
          className="text-txt-secondary text-lg md:text-xl max-w-2xl mx-auto leading-relaxed"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2, duration: 0.6 }}
        >
          {subtitle}
        </motion.p>
      )}
      <motion.div
        className={`mt-5 ${align === 'center' ? 'mx-auto' : ''} h-[2px] rounded-full`}
        style={{
          background: gradient === 'solar'
            ? 'linear-gradient(90deg, transparent, #F5A623, #E8590C, transparent)'
            : gradient === 'tech'
              ? 'linear-gradient(90deg, transparent, #06B6D4, #3B82F6, transparent)'
              : 'linear-gradient(90deg, transparent, #F5A623, #06B6D4, transparent)',
        }}
        initial={{ width: 0, opacity: 0 }}
        whileInView={{ width: 100, opacity: 0.7 }}
        viewport={{ once: true }}
        transition={{ delay: 0.4, duration: 0.8, ease: 'easeOut' }}
      />
    </motion.div>
  );
};

export default SectionTitle;
