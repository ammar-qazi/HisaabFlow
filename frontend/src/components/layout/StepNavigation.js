import React from 'react';
import { useTheme } from '../../theme/ThemeProvider';
import { Badge } from '../ui';
import { CloudUpload, Settings, Download } from '../ui/Icons';

const StepNavigation = ({ currentStep = 1 }) => {
  const theme = useTheme();

  const steps = [
    {
      number: 1,
      title: 'Upload Files',
      description: 'Select CSV bank statements',
      icon: CloudUpload,
    },
    {
      number: 2,
      title: 'Configure',
      description: 'Map columns & set rules',
      icon: Settings,
    },
    {
      number: 3,
      title: 'Review & Export',
      description: 'Verify data and export results',
      icon: Download,
    },
  ];

  const sidebarStyles = {
    width: '280px',
    backgroundColor: theme.colors.background.paper,
    borderRight: `1px solid ${theme.colors.border}`,
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
    padding: theme.spacing.lg,
    gap: theme.spacing.md,
  };

  const titleStyles = {
    color: theme.colors.text.primary,
    fontSize: '18px',
    fontWeight: '600',
    marginBottom: theme.spacing.lg,
    paddingBottom: theme.spacing.md,
    borderBottom: `1px solid ${theme.colors.divider}`,
  };

  const stepItemStyles = (step) => ({
    display: 'flex',
    alignItems: 'flex-start',
    gap: theme.spacing.md,
    padding: theme.spacing.md,
    borderRadius: theme.borderRadius.lg,
    backgroundColor: step.number === currentStep 
      ? theme.colors.action.selected 
      : 'transparent',
    border: step.number === currentStep 
      ? `1px solid ${theme.colors.primary}` 
      : '1px solid transparent',
    transition: 'all 0.2s ease',
    cursor: 'pointer',
  });

  const stepIconStyles = (step) => ({
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: '40px',
    height: '40px',
    borderRadius: '50%',
    backgroundColor: step.number <= currentStep 
      ? theme.colors.primary 
      : theme.colors.background.elevated,
    color: step.number <= currentStep 
      ? 'white' 
      : theme.colors.text.secondary,
    flexShrink: 0,
  });

  const stepContentStyles = {
    flex: 1,
    minWidth: 0,
  };

  const stepTitleStyles = (step) => ({
    color: step.number === currentStep 
      ? theme.colors.primary 
      : theme.colors.text.primary,
    fontSize: '14px',
    fontWeight: '600',
    marginBottom: '4px',
  });

  const stepDescriptionStyles = {
    color: theme.colors.text.secondary,
    fontSize: '12px',
    lineHeight: '1.4',
  };

  const stepNumberStyles = (step) => ({
    fontSize: '12px',
    fontWeight: '600',
    color: step.number <= currentStep ? 'white' : theme.colors.text.secondary,
  });

  const progressBarStyles = {
    marginTop: theme.spacing.xl,
    paddingTop: theme.spacing.lg,
    borderTop: `1px solid ${theme.colors.divider}`,
  };

  const progressLabelStyles = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: theme.spacing.sm,
    fontSize: '12px',
    color: theme.colors.text.secondary,
  };

  const progressBarContainerStyles = {
    width: '100%',
    height: '8px',
    backgroundColor: theme.colors.background.elevated,
    borderRadius: theme.borderRadius.pill,
    overflow: 'hidden',
  };

  const progressBarFillStyles = {
    height: '100%',
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.pill,
    width: `${(currentStep / steps.length) * 100}%`,
    transition: 'width 0.3s ease',
  };

  return (
    <nav style={sidebarStyles}>
      <h2 style={titleStyles}>Workflow Progress</h2>
      
      <div style={{ flex: 1 }}>
        {steps.map((step) => {
          const IconComponent = step.icon;
          
          return (
            <div key={step.number} style={stepItemStyles(step)}>
              <div style={stepIconStyles(step)}>
                {step.number <= currentStep ? (
                  <IconComponent size={18} />
                ) : (
                  <span style={stepNumberStyles(step)}>{step.number}</span>
                )}
              </div>
              
              <div style={stepContentStyles}>
                <div style={stepTitleStyles(step)}>
                  {step.title}
                </div>
                <div style={stepDescriptionStyles}>
                  {step.description}
                </div>
              </div>
              
              {step.number === currentStep && (
                <Badge variant="primary" style={{ fontSize: '10px' }}>
                  Current
                </Badge>
              )}
            </div>
          );
        })}
      </div>

      {/* Progress Bar */}
      <div style={progressBarStyles}>
        <div style={progressLabelStyles}>
          <span>Overall Progress</span>
          <span>{Math.round((currentStep / steps.length) * 100)}%</span>
        </div>
        <div style={progressBarContainerStyles}>
          <div style={progressBarFillStyles} />
        </div>
      </div>
    </nav>
  );
};

export default StepNavigation;