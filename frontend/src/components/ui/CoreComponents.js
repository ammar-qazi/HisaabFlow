// Core UI Components - Button, Card, Badge
import React from 'react';
import { useTheme } from '../../theme/ThemeProvider';

// Button Component
export const Button = ({ 
  variant = 'primary', 
  size = 'medium', 
  disabled = false, 
  loading = false,
  leftIcon,
  rightIcon,
  children, 
  onClick,
  className = '',
  ...props 
}) => {
  const { colors, spacing, borderRadius } = useTheme();
  
  const variants = {
    primary: {
      backgroundColor: disabled ? colors.action.disabled : colors.primary,
      color: 'white',
      border: 'none',
      '&:hover': { backgroundColor: colors.primaryDark },
    },
    secondary: {
      backgroundColor: 'transparent',
      color: disabled ? colors.action.disabled : colors.text.primary,
      border: `1px solid ${disabled ? colors.action.disabled : colors.border}`,
      '&:hover': { backgroundColor: colors.action.hover },
    },
    outline: {
      backgroundColor: 'transparent',
      color: disabled ? colors.action.disabled : colors.primary,
      border: `1px solid ${disabled ? colors.action.disabled : colors.primary}`,
      '&:hover': { backgroundColor: colors.action.hover },
    },
  };
  
  const sizes = {
    small: { padding: `${spacing.xs} ${spacing.sm}`, fontSize: '12px' },
    medium: { padding: `${spacing.sm} ${spacing.md}`, fontSize: '14px' },
    large: { padding: `${spacing.md} ${spacing.lg}`, fontSize: '16px' },
  };
  
  const baseStyle = {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.xs,
    borderRadius: borderRadius.md,
    fontWeight: '500',
    cursor: disabled || loading ? 'not-allowed' : 'pointer',
    transition: 'all 0.2s ease',
    opacity: disabled ? 0.6 : 1,
    ...variants[variant],
    ...sizes[size],
  };
  
  return (
    <button
      style={baseStyle}
      disabled={disabled || loading}
      onClick={onClick}
      className={className}
      {...props}
    >
      {leftIcon && !loading && leftIcon}
      {loading && <Spinner size={16} />}
      {children}
      {rightIcon && !loading && rightIcon}
    </button>
  );
};

// Card Component
export const Card = ({ 
  children, 
  elevated = false, 
  padding = 'lg',
  className = '',
  style = {},
  ...props 
}) => {
  const { colors, spacing, borderRadius, shadows } = useTheme();
  
  const cardStyle = {
    backgroundColor: colors.background.paper,
    borderRadius: borderRadius.lg,
    border: `1px solid ${colors.border}`,
    boxShadow: elevated ? shadows.md : shadows.sm,
    padding: spacing[padding],
    transition: 'all 0.2s ease',
    ...style,
  };
  
  return (
    <div style={cardStyle} className={className} {...props}>
      {children}
    </div>
  );
};

// Badge Component
export const Badge = ({ 
  variant = 'default', 
  size = 'medium',
  children, 
  className = '',
  style = {},
  ...props 
}) => {
  const { colors, spacing, borderRadius } = useTheme();
  
  const variants = {
    default: { backgroundColor: colors.background.elevated, color: colors.text.primary },
    primary: { backgroundColor: colors.primary, color: 'white' },
    secondary: { backgroundColor: colors.secondary, color: 'white' },
    success: { backgroundColor: colors.success, color: 'white' },
    warning: { backgroundColor: colors.warning, color: 'white' },
    error: { backgroundColor: colors.error, color: 'white' },
    outline: { 
      backgroundColor: 'transparent', 
      color: colors.text.primary,
      border: `1px solid ${colors.border}`,
    },
  };
  
  const sizes = {
    small: { padding: `2px ${spacing.xs}`, fontSize: '10px' },
    medium: { padding: `${spacing.xs} ${spacing.sm}`, fontSize: '12px' },
    large: { padding: `${spacing.xs} ${spacing.md}`, fontSize: '14px' },
  };
  
  const badgeStyle = {
    display: 'inline-flex',
    alignItems: 'center',
    borderRadius: borderRadius.pill,
    fontWeight: '500',
    whiteSpace: 'nowrap',
    ...variants[variant],
    ...sizes[size],
    ...style,
  };
  
  return (
    <span style={badgeStyle} className={className} {...props}>
      {children}
    </span>
  );
};

// Spinner Component
export const Spinner = ({ size = 24, color, className = '', style = {} }) => {
  const { colors } = useTheme();
  
  const spinnerStyle = {
    width: size,
    height: size,
    border: `2px solid ${colors.background.elevated}`,
    borderTopColor: color || colors.primary,
    borderRadius: '50%',
    animation: 'spin 0.8s linear infinite',
    ...style,
  };
  
  return (
    <>
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
      <div style={spinnerStyle} className={className} />
    </>
  );
};

export default { Button, Card, Badge, Spinner };