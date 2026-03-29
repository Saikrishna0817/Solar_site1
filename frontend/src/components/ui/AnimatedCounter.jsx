import useAnimatedCounter from '../../hooks/useAnimatedCounter';

const AnimatedCounter = ({ end, duration = 2000, decimals = 0, prefix = '', suffix = '', className = '' }) => {
  const { count, ref } = useAnimatedCounter(end, duration, 0, decimals);

  return (
    <span ref={ref} className={className}>
      {prefix}{count.toLocaleString('en-IN', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}{suffix}
    </span>
  );
};

export default AnimatedCounter;
