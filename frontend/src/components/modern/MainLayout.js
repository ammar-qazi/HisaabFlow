import React from 'react';
import { useTheme } from '../../theme/ThemeProvider';

const MainLayout = ({ children, sidebar, fullHeight = true }) => {
  const theme = useTheme();

  const layoutStyles = {
    display: 'flex',
    width: '100%',
    height: fullHeight ? '100vh' : 'auto',
    backgroundColor: theme.colors.background.default,
    overflow: 'hidden',
  };

  const sidebarStyles = {
    flexShrink: 0,
    height: '100%',
    overflowY: 'auto',
    overflowX: 'hidden',
  };

  const contentStyles = {
    flex: 1,
    height: '100%',
    overflowY: 'auto',
    overflowX: 'hidden',
    display: 'flex',
    flexDirection: 'column',
  };

  return (
    <div style={layoutStyles}>
      {sidebar && (
        <div style={sidebarStyles}>
          {sidebar}
        </div>
      )}
      <div style={contentStyles}>
        {children}
      </div>
    </div>
  );
};

export default MainLayout;