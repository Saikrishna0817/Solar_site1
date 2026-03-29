import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { getSuitabilityColor, getSuitabilityLabel } from '../../data/constants';

const SuitabilityGauge = ({ score, size = 200, className = '' }) => {
  const [animatedScore, setAnimatedScore] = useState(0);
  const radius = (size - 20) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeWidth = 12;
  const center = size / 2;

  useEffect(() => {
    const timer = setTimeout(() => setAnimatedScore(score), 200);
    return () => clearTimeout(timer);
  }, [score]);

  const progress = animatedScore * circumference * 0.75; // 270 degrees
  const color = getSuitabilityColor(score);
  const label = getSuitabilityLabel(score);

  return (
    <div className={`relative inline-flex flex-col items-center ${className}`}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {/* Background arc */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="rgba(30, 58, 82, 0.3)"
          strokeWidth={strokeWidth}
          strokeDasharray={`${circumference * 0.75} ${circumference * 0.25}`}
          strokeDashoffset={0}
          strokeLinecap="round"
          transform={`rotate(135, ${center}, ${center})`}
        />
        {/* Foreground arc */}
        <motion.circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={`${circumference * 0.75} ${circumference * 0.25}`}
          strokeLinecap="round"
          transform={`rotate(135, ${center}, ${center})`}
          initial={{ strokeDashoffset: circumference * 0.75 }}
          animate={{ strokeDashoffset: circumference * 0.75 - progress }}
          transition={{ duration: 1.5, ease: [0.22, 1, 0.36, 1], delay: 0.3 }}
          style={{ filter: `drop-shadow(0 0 8px ${color}40)` }}
        />
      </svg>
      {/* Center text */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <motion.span
          className="font-display font-bold text-4xl"
          style={{ color }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          {(animatedScore * 100).toFixed(0)}
        </motion.span>
        <span className="text-txt-dim text-sm mt-1">/ 100</span>
        <span
          className="text-xs font-semibold mt-2 px-3 py-1 rounded-full"
          style={{ backgroundColor: `${color}20`, color }}
        >
          {label}
        </span>
      </div>
    </div>
  );
};

export default SuitabilityGauge;
