import React from 'react';
import { useTheme } from '../../theme/ThemeProvider';
import { Button, Badge } from '../ui';
import { Building, Sun, Moon } from '../ui/Icons';

const AppHeader = () => {
  const theme = useTheme();

  const headerStyles = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: `${theme.spacing.md} ${theme.spacing.lg}`,
    backgroundColor: theme.colors.background.paper,
    borderBottom: `1px solid ${theme.colors.border}`,
    boxShadow: theme.shadows.sm,
    position: 'sticky',
    top: 0,
    zIndex: 100,
    minHeight: '64px',
  };

  const brandingStyles = {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing.md,
  };

  const logoStyles = {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing.sm,
    color: theme.colors.primary,
    fontSize: '24px',
    fontWeight: '700',
    textDecoration: 'none',
  };

  const versionBadgeStyles = {
    marginLeft: theme.spacing.sm,
  };

  const taglineStyles = {
    color: theme.colors.text.secondary,
    fontSize: '14px',
    fontStyle: 'italic',
    marginLeft: theme.spacing.md,
  };

  const actionsStyles = {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing.md,
  };

  const themeToggleStyles = {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing.sm,
    padding: `${theme.spacing.sm} ${theme.spacing.md}`,
    backgroundColor: 'transparent',
    border: `1px solid ${theme.colors.border}`,
    borderRadius: theme.borderRadius.md,
    color: theme.colors.text.primary,
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    fontSize: '14px',
  };

  return (
    <header style={headerStyles}>
      {/* Branding Section */}
      <div style={brandingStyles}>
        <div style={logoStyles}>
          <Building size={28} color={theme.colors.primary} />
          <span>HisaabFlow</span>
          <div style={versionBadgeStyles}>
            <Badge variant="primary">v2.0</Badge>
          </div>
        </div>
        <span style={taglineStyles}>
          Smart Bank Statement Parser
        </span>
      </div>

      {/* Actions Section */}
      <div style={actionsStyles}>
        {/* Theme Toggle */}
        <button
          onClick={theme.toggleDarkMode}
          style={themeToggleStyles}
          onMouseEnter={(e) => {
            e.target.style.backgroundColor = theme.colors.action.hover;
          }}
          onMouseLeave={(e) => {
            e.target.style.backgroundColor = 'transparent';
          }}
          title={`Switch to ${theme.darkMode ? 'light' : 'dark'} mode`}
        >
          {theme.darkMode ? (
            <>
              <Sun size={16} />
              <span>Light</span>
            </>
          ) : (
            <>
              <Moon size={16} />
              <span>Dark</span>
            </>
          )}
        </button>
      </div>
    </header>
  );
};

export default AppHeader;