// Theme system for the modernized HisaabFlow
import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

const createThemeColors = (darkMode) => ({
  // Primary colors - Financial green
  primary: darkMode ? '#4CAF50' : '#2E7D32',
  primaryLight: darkMode ? '#81C784' : '#4CAF50',
  primaryDark: darkMode ? '#2E7D32' : '#1B5E20',
  
  // Secondary colors - Trust blue
  secondary: darkMode ? '#42A5F5' : '#1976D2',
  secondaryLight: darkMode ? '#90CAF9' : '#42A5F5',
  secondaryDark: darkMode ? '#1976D2' : '#0D47A1',
  
  // Status colors
  success: '#4CAF50',
  warning: '#FF9800',
  error: '#F44336',
  info: '#2196F3',
  
  // Background colors
  background: {
    default: darkMode ? '#121212' : '#F8F9FA',
    paper: darkMode ? '#1E1E1E' : '#FFFFFF',
    elevated: darkMode ? '#2A2A2A' : '#F5F5F5',
  },
  
  // Text colors
  text: {
    primary: darkMode ? '#E0E0E0' : '#212121',
    secondary: darkMode ? '#A0A0A0' : '#757575',
    disabled: darkMode ? '#616161' : '#BDBDBD',
  },
  
  // Border and divider colors
  divider: darkMode ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.12)',
  border: darkMode ? 'rgba(255,255,255,0.1)' : '#E0E0E0',
  
  // Action colors
  action: {
    hover: darkMode ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.04)',
    selected: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)',
    disabled: darkMode ? 'rgba(255,255,255,0.26)' : 'rgba(0,0,0,0.26)',
  },
});

const spacing = {
  xs: '4px',
  sm: '8px',
  md: '16px',
  lg: '24px',
  xl: '32px',
  xxl: '48px',
};

const typography = {
  fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  h1: { fontSize: '32px', fontWeight: '600', lineHeight: '1.2' },
  h2: { fontSize: '28px', fontWeight: '600', lineHeight: '1.3' },
  h3: { fontSize: '24px', fontWeight: '600', lineHeight: '1.3' },
  h4: { fontSize: '20px', fontWeight: '500', lineHeight: '1.4' },
  h5: { fontSize: '16px', fontWeight: '500', lineHeight: '1.4' },
  h6: { fontSize: '14px', fontWeight: '500', lineHeight: '1.4' },
  body1: { fontSize: '16px', fontWeight: '400', lineHeight: '1.5' },
  body2: { fontSize: '14px', fontWeight: '400', lineHeight: '1.5' },
  caption: { fontSize: '12px', fontWeight: '400', lineHeight: '1.4' },
};

const borderRadius = {
  xs: '4px',
  sm: '6px',
  md: '8px',
  lg: '12px',
  xl: '16px',
  pill: '50px',
};

const shadows = {
  none: 'none',
  sm: '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
  md: '0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.06)',
  lg: '0 10px 15px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.05)',
  xl: '0 20px 25px rgba(0,0,0,0.1), 0 10px 10px rgba(0,0,0,0.04)',
};

export const ThemeProvider = ({ children }) => {
  const [darkMode, setDarkMode] = useState(() => {
    // Check localStorage first, then system preference
    const saved = localStorage.getItem('hisaabflow-dark-mode');
    if (saved !== null) return JSON.parse(saved);
    return window.matchMedia?.('(prefers-color-scheme: dark)').matches || false;
  });

  const toggleDarkMode = () => {
    setDarkMode(prev => {
      const newMode = !prev;
      localStorage.setItem('hisaabflow-dark-mode', JSON.stringify(newMode));
      return newMode;
    });
  };

  const theme = {
    darkMode,
    toggleDarkMode,
    colors: createThemeColors(darkMode),
    spacing,
    typography,
    borderRadius,
    shadows,
  };

  // Update CSS custom properties for global styles
  useEffect(() => {
    const root = document.documentElement;
    const colors = theme.colors;
    
    root.style.setProperty('--color-primary', colors.primary);
    root.style.setProperty('--color-secondary', colors.secondary);
    root.style.setProperty('--color-background', colors.background.default);
    root.style.setProperty('--color-surface', colors.background.paper);
    root.style.setProperty('--color-text-primary', colors.text.primary);
    root.style.setProperty('--color-text-secondary', colors.text.secondary);
    root.style.setProperty('--color-border', colors.border);
    root.style.setProperty('--color-divider', colors.divider);
  }, [theme.colors]);

  return (
    <ThemeContext.Provider value={theme}>
      {children}
    </ThemeContext.Provider>
  );
};

// Utility functions for common style patterns
export const createStyles = (theme) => ({
  card: {
    backgroundColor: theme.colors.background.paper,
    borderRadius: theme.borderRadius.lg,
    border: `1px solid ${theme.colors.border}`,
    boxShadow: theme.shadows.sm,
    padding: theme.spacing.lg,
  },
  
  button: {
    primary: {
      backgroundColor: theme.colors.primary,
      color: 'white',
      border: 'none',
      borderRadius: theme.borderRadius.md,
      padding: `${theme.spacing.sm} ${theme.spacing.lg}`,
      fontSize: '14px',
      fontWeight: '500',
      cursor: 'pointer',
      transition: 'all 0.2s ease',
    },
    
    secondary: {
      backgroundColor: 'transparent',
      color: theme.colors.text.primary,
      border: `1px solid ${theme.colors.border}`,
      borderRadius: theme.borderRadius.md,
      padding: `${theme.spacing.sm} ${theme.spacing.lg}`,
      fontSize: '14px',
      fontWeight: '500',
      cursor: 'pointer',
      transition: 'all 0.2s ease',
    },
  },
  
  input: {
    backgroundColor: theme.colors.background.paper,
    border: `1px solid ${theme.colors.border}`,
    borderRadius: theme.borderRadius.md,
    padding: `${theme.spacing.sm} ${theme.spacing.md}`,
    fontSize: '14px',
    color: theme.colors.text.primary,
    '&:focus': {
      outline: 'none',
      borderColor: theme.colors.primary,
    },
  },
});

export default ThemeProvider;