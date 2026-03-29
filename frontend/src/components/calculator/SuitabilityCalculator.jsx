import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { calculateSuitability } from '../../services/calculations';
import { getSuitabilityColor, getSuitabilityLabel } from '../../data/constants';

const SuitabilityCalculator = ({ className = '' }) => {
  const [inputs, setInputs] = useState({
    ghi: 5.0,
    temperature: 27,
    slope: 2,
    roadDistance: 5,
    gridDistance: 10,
    landScore: 0.7,
  });

  const result = useMemo(() => calculateSuitability(inputs), [inputs]);
  const color = getSuitabilityColor(result.score);
  const label = getSuitabilityLabel(result.score);

  const sliderConfig = [
    { key: 'ghi', label: 'Solar GHI', unit: 'kWh/m²/day', min: 3.5, max: 6.0, step: 0.1, icon: '☀️' },
    { key: 'temperature', label: 'Temperature', unit: '°C', min: 10, max: 45, step: 1, icon: '🌡️' },
    { key: 'slope', label: 'Terrain Slope', unit: '°', min: 0, max: 15, step: 0.5, icon: '⛰️' },
    { key: 'roadDistance', label: 'Road Distance', unit: 'km', min: 0, max: 20, step: 0.5, icon: '🛣️' },
    { key: 'gridDistance', label: 'Grid Distance', unit: 'km', min: 0, max: 40, step: 1, icon: '⚡' },
    { key: 'landScore', label: 'Land Suitability', unit: 'score', min: 0, max: 1, step: 0.05, icon: '🏗️' },
  ];

  return (
    <div className={`glass-card p-6 md:p-8 ${className}`}>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Sliders */}
        <div className="space-y-5">
          {sliderConfig.map(({ key, label, unit, min, max, step, icon }) => (
            <div key={key}>
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm text-txt-secondary flex items-center gap-2">
                  <span>{icon}</span>
                  {label}
                </label>
                <span className="text-sm font-mono text-solar-gold">
                  {inputs[key]} {unit}
                </span>
              </div>
              <input
                type="range"
                min={min}
                max={max}
                step={step}
                value={inputs[key]}
                onChange={(e) => setInputs(prev => ({ ...prev, [key]: parseFloat(e.target.value) }))}
                className="w-full h-1.5 rounded-full appearance-none cursor-pointer"
                style={{
                  background: `linear-gradient(to right, #F5A623 0%, #F5A623 ${((inputs[key] - min) / (max - min)) * 100}%, #1E3A52 ${((inputs[key] - min) / (max - min)) * 100}%, #1E3A52 100%)`,
                }}
              />
              <div className="flex justify-between text-xs text-txt-dim mt-1">
                <span>{min}</span>
                <span>{max}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Results */}
        <div className="flex flex-col items-center justify-center">
          {/* Score gauge */}
          <div className="relative w-48 h-48 mb-6">
            <svg viewBox="0 0 200 200" className="w-full h-full">
              <circle cx="100" cy="100" r="85" fill="none" stroke="rgba(30,58,82,0.3)" strokeWidth="10"
                strokeDasharray={`${Math.PI * 170 * 0.75} ${Math.PI * 170 * 0.25}`}
                transform="rotate(135, 100, 100)" strokeLinecap="round" />
              <motion.circle
                cx="100" cy="100" r="85" fill="none" stroke={color} strokeWidth="10"
                strokeDasharray={`${Math.PI * 170 * 0.75} ${Math.PI * 170 * 0.25}`}
                strokeLinecap="round" transform="rotate(135, 100, 100)"
                animate={{ strokeDashoffset: Math.PI * 170 * 0.75 * (1 - result.score) }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
                style={{ filter: `drop-shadow(0 0 6px ${color}50)` }}
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="font-display font-bold text-4xl" style={{ color }}>
                {(result.score * 100).toFixed(0)}
              </span>
              <span className="text-txt-dim text-sm">/ 100</span>
            </div>
          </div>

          <span
            className="px-4 py-1.5 rounded-full text-sm font-semibold mb-6"
            style={{ backgroundColor: `${color}20`, color }}
          >
            {label}
          </span>

          {/* Breakdown bars */}
          <div className="w-full space-y-3">
            {result.breakdown.map(({ feature, score, contribution }) => (
              <div key={feature}>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-txt-secondary">{feature}</span>
                  <span className="text-txt-dim font-mono">{(score * 100).toFixed(0)}%</span>
                </div>
                <div className="w-full h-1.5 bg-space-border rounded-full overflow-hidden">
                  <motion.div
                    className="h-full rounded-full"
                    style={{ background: `linear-gradient(90deg, ${color}, ${color}80)` }}
                    animate={{ width: `${score * 100}%` }}
                    transition={{ duration: 0.5, ease: 'easeOut' }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SuitabilityCalculator;
