// Progress Component
import React from 'react';
import { useTheme } from '../../theme/ThemeProvider';

export const Progress = ({ 
  value = 0, 
  max = 100, 
  size = 'medium',
  variant = 'primary',
  showValue = false,
  className = '',
  style = {},
  ...props 
}) => {
  const { colors, spacing, borderRadius } = useTheme();
  
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  
  const sizes = {
    small: { height: '4px' },
    medium: { height: '6px' },
    large: { height: '8px' },
  };
  
  const variants = {
    primary: colors.primary,
    secondary: colors.secondary,
    success: colors.success,
    warning: colors.warning,
    error: colors.error,
  };
  
  const containerStyle = {
    width: '100%',
    backgroundColor: colors.background.elevated,
    borderRadius: borderRadius.pill,
    overflow: 'hidden',
    ...sizes[size],
    ...style,
  };
  
  const barStyle = {
    height: '100%',
    width: `${percentage}%`,
    backgroundColor: variants[variant],
    transition: 'width 0.3s ease',
    borderRadius: borderRadius.pill,
  };
  
  return (
    <div className={className}>
      <div style={containerStyle} {...props}>
        <div style={barStyle} />
      </div>
      {showValue && (
        <div style={{ 
          marginTop: spacing.xs, 
          fontSize: '12px', 
          color: colors.text.secondary,
          textAlign: 'center'
        }}>
          {Math.round(percentage)}%
        </div>
      )}
    </div>
  );
};

export default Progress;