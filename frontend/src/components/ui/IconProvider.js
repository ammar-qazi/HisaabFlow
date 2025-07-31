// Hybrid icon system - use custom for core, Lucide for extended features
import React from 'react';

// Custom core icons (always loaded)
import * as CoreIcons from './Icons';

// Lazy-loaded Lucide icons for advanced features
const LucideIcon = React.lazy(() => import('lucide-react'));

export const IconProvider = ({ name, isCore = true, ...props }) => {
  if (isCore && CoreIcons[name]) {
    const Icon = CoreIcons[name];
    return <Icon {...props} />;
  }
  
  // Fallback to Lucide for extended features
  return (
    <React.Suspense fallback={<div style={{ width: props.size || 24, height: props.size || 24 }} />}>
      <LucideIcon name={name} {...props} />
    </React.Suspense>
  );
};

// Usage
<IconProvider name="Upload" isCore={true} />      // Uses custom SVG
<IconProvider name="Calendar" isCore={false} />        // Uses Lucide (if installed)
