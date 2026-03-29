import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const GradientButton = ({ to, children, variant = 'solar', size = 'md', className = '', onClick, ...props }) => {
  const variants = {
    solar: 'btn-solar',
    outline: 'btn-outline',
    tech: 'bg-gradient-tech text-white font-semibold border-none cursor-pointer transition-all duration-300 hover:shadow-glow-cyan hover:-translate-y-0.5',
  };

  const sizes = {
    sm: '!py-2 !px-4 text-sm',
    md: '!py-3 !px-6 text-base',
    lg: '!py-4 !px-8 text-lg',
  };

  const buttonClass = `${variants[variant]} ${sizes[size]} rounded-xl inline-flex items-center gap-2.5 ${className}`;

  const MotionComponent = to ? motion(Link) : motion.button;

  return (
    <MotionComponent
      to={to || undefined}
      className={buttonClass}
      onClick={onClick}
      whileTap={{ scale: 0.97 }}
      {...props}
    >
      {children}
    </MotionComponent>
  );
};

export default GradientButton;
