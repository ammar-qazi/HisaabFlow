import React from 'react';
import { useTheme } from '../../theme/ThemeProvider';

const ContentArea = ({ 
  children, 
  title, 
  subtitle, 
  actions,
  padding = 'lg',
  maxWidth = 'none' 
}) => {
  const theme = useTheme();

  const containerStyles = {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    backgroundColor: theme.colors.background.default,
    minHeight: '100%',
  };

  const headerStyles = title ? {
    backgroundColor: theme.colors.background.paper,
    borderBottom: `1px solid ${theme.colors.border}`,
    padding: `${theme.spacing.lg} ${theme.spacing[padding]}`,
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: theme.spacing.md,
  } : {};

  const headerContentStyles = {
    flex: 1,
    minWidth: 0,
  };

  const titleStyles = {
    color: theme.colors.text.primary,
    fontSize: '24px',
    fontWeight: '600',
    margin: 0,
    marginBottom: subtitle ? '4px' : 0,
  };

  const subtitleStyles = {
    color: theme.colors.text.secondary,
    fontSize: '14px',
    margin: 0,
    lineHeight: '1.4',
  };

  const actionsStyles = {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing.sm,
    flexShrink: 0,
  };

  const contentStyles = {
    flex: 1,
    padding: theme.spacing[padding],
    maxWidth: maxWidth !== 'none' ? maxWidth : undefined,
    margin: maxWidth !== 'none' ? '0 auto' : undefined,
    width: '100%',
    boxSizing: 'border-box',
  };

  return (
    <div style={containerStyles}>
      {title && (
        <div style={headerStyles}>
          <div style={headerContentStyles}>
            <h1 style={titleStyles}>{title}</h1>
            {subtitle && <p style={subtitleStyles}>{subtitle}</p>}
          </div>
          {actions && (
            <div style={actionsStyles}>
              {actions}
            </div>
          )}
        </div>
      )}
      
      <div style={contentStyles}>
        {children}
      </div>
    </div>
  );
};

export default ContentArea;