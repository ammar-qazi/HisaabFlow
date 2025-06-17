import React, { useState, useRef } from 'react';

// Simple SVG Icon Components
const IconWrapper = ({ children, size = 24, color = 'currentColor', ...props }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke={color}
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    {...props}
  >
    {children}
  </svg>
);

const CloudUpload = (props) => (
  <IconWrapper {...props}>
    <path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242" />
    <path d="m12 12 4-4-4-4" />
    <path d="M16 8H8" />
  </IconWrapper>
);

const Settings = (props) => (
  <IconWrapper {...props}>
    <circle cx="12" cy="12" r="3" />
    <path d="m12 1 1.68 3.36L17 6.64l-1.32 2.68L19 12l-3.32 2.68L17 17.36l-3.32 1.32L12 23l-1.68-3.36L7 17.36l1.32-2.68L5 12l3.32-2.68L7 6.64l3.32-1.32L12 1z" />
  </IconWrapper>
);

const Eye = (props) => (
  <IconWrapper {...props}>
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
    <circle cx="12" cy="12" r="3" />
  </IconWrapper>
);

const Download = (props) => (
  <IconWrapper {...props}>
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="7,10 12,15 17,10" />
    <line x1="12" x2="12" y1="15" y2="3" />
  </IconWrapper>
);

const FileText = (props) => (
  <IconWrapper {...props}>
    <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
  </IconWrapper>
);

const Check = (props) => (
  <IconWrapper {...props}>
    <polyline points="20,6 9,17 4,12" />
  </IconWrapper>
);

const Trash2 = (props) => (
  <IconWrapper {...props}>
    <polyline points="3,6 5,6 21,6" />
    <path d="m19,6v14a2,2 0 0,1-2,2H7a2,2 0 0,1-2-2V6m3,0V4a2,2 0 0,1 2-2h4a2,2 0 0,1 2,2v2" />
  </IconWrapper>
);

const ChevronDown = (props) => (
  <IconWrapper {...props}>
    <polyline points="6,9 12,15 18,9" />
  </IconWrapper>
);

const Sun = (props) => (
  <IconWrapper {...props}>
    <circle cx="12" cy="12" r="5" />
    <path d="m12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72 1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
  </IconWrapper>
);

const Moon = (props) => (
  <IconWrapper {...props}>
    <path d="M12 3a6.364 6.364 0 0 0 9 9 9 9 0 1 1-9-9Z" />
  </IconWrapper>
);

const TrendingUp = (props) => (
  <IconWrapper {...props}>
    <polyline points="22,7 13.5,15.5 8.5,10.5 2,17" />
    <polyline points="16,7 22,7 22,13" />
  </IconWrapper>
);

const Building = (props) => (
  <IconWrapper {...props}>
    <path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z" />
    <path d="M6 12h4m4 0h4M6 16h4m4 0h4M6 8h4m4 0h4" />
  </IconWrapper>
);

const ArrowLeftRight = (props) => (
  <IconWrapper {...props}>
    <path d="M8 3 4 7l4 4" />
    <path d="M4 7h16" />
    <path d="m16 21 4-4-4-4" />
    <path d="M20 17H4" />
  </IconWrapper>
);

const ChevronLeft = (props) => (
  <IconWrapper {...props}>
    <polyline points="15,18 9,12 15,6" />
  </IconWrapper>
);

const ChevronRight = (props) => (
  <IconWrapper {...props}>
    <polyline points="9,18 15,12 9,6" />
  </IconWrapper>
);

const HisaabFlowPrototype = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [files] = useState([
    { name: 'wise_usd_2024.csv', size: '2.3 KB', bank: 'Wise USD', status: 'configured' },
    { name: 'nayapay_statement.csv', size: '5.1 KB', bank: 'NayaPay', status: 'pending' },
    { name: 'erste_bank_eur.csv', size: '3.7 KB', bank: 'Erste Bank', status: 'configured' },
  ]);

  const mockTransactions = [
    { date: '2024-06-15', amount: -45.50, category: 'Groceries', description: 'Supermarket Purchase', account: 'Wise USD' },
    { date: '2024-06-14', amount: 2500.00, category: 'Income', description: 'Salary Transfer', account: 'NayaPay' },
    { date: '2024-06-13', amount: -12.30, category: 'Transportation', description: 'Metro Card Top-up', account: 'Erste Bank' },
    { date: '2024-06-12', amount: -850.00, category: 'Rent', description: 'Monthly Rent Payment', account: 'Wise USD' },
  ];

  const steps = [
    { label: 'Upload Files', description: 'Select bank statement CSV files', icon: CloudUpload },
    { label: 'Configure', description: 'Map columns and apply bank templates', icon: Settings },
    { label: 'Review', description: 'Preview and validate processed data', icon: Eye },
    { label: 'Export', description: 'Download unified transaction data', icon: Download },
  ];

  const theme = {
    colors: darkMode ? {
      primary: '#4CAF50',
      primaryDark: '#2E7D32',
      secondary: '#42A5F5',
      background: '#121212',
      surface: '#1E1E1E',
      surfaceVariant: '#2A2A2A',
      text: '#E0E0E0',
      textSecondary: '#A0A0A0',
      border: 'rgba(255,255,255,0.1)',
      success: '#4CAF50',
      warning: '#FF9800',
      error: '#F44336',
    } : {
      primary: '#2E7D32',
      primaryDark: '#1B5E20',
      secondary: '#1976D2',
      background: '#F8F9FA',
      surface: '#FFFFFF',
      surfaceVariant: '#F5F5F5',
      text: '#212121',
      textSecondary: '#757575',
      border: '#E0E0E0',
      success: '#4CAF50',
      warning: '#FF9800',
      error: '#F44336',
    }
  };

  const handleNext = () => {
    setLoading(true);
    setTimeout(() => {
      setActiveStep((prevStep) => prevStep + 1);
      setLoading(false);
    }, 1500);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleFileSelect = (event) => {
    console.log('Files selected:', event.target.files);
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        backgroundColor: theme.colors.background,
        fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
      }}
    >
      {/* Global Styles */}
      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateX(20px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }

        @keyframes loading {
          0% {
            transform: translateX(-100%);
          }
          50% {
            transform: translateX(0%);
          }
          100% {
            transform: translateX(100%);
          }
        }
      `}</style>

      {/* Header */}
      <div
        style={{
          backgroundColor: theme.colors.surface,
          borderBottom: `1px solid ${theme.colors.border}`,
          padding: '0 24px',
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            height: '64px',
            maxWidth: '1200px',
            margin: '0 auto',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Building size={24} color={theme.colors.primary} />
            <span
              style={{
                fontSize: '20px',
                fontWeight: '600',
                color: theme.colors.text,
              }}
            >
              HisaabFlow
            </span>
            <span
              style={{
                padding: '2px 8px',
                borderRadius: '12px',
                fontSize: '12px',
                backgroundColor: theme.colors.surfaceVariant,
                color: theme.colors.primary,
                border: `1px solid ${theme.colors.primary}`,
              }}
            >
              v2.0
            </span>
          </div>
          <button
            onClick={() => setDarkMode(!darkMode)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 16px',
              backgroundColor: 'transparent',
              border: `1px solid ${theme.colors.border}`,
              borderRadius: '8px',
              color: theme.colors.text,
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
          >
            {darkMode ? <Sun size={16} /> : <Moon size={16} />}
            {darkMode ? 'Light' : 'Dark'}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '32px 24px' }}>
        <div style={{ marginBottom: '32px' }}>
          <h1
            style={{
              fontSize: '32px',
              fontWeight: '600',
              color: theme.colors.text,
              margin: '0 0 8px 0',
            }}
          >
            Bank Statement Parser
          </h1>
          <p
            style={{
              fontSize: '16px',
              color: theme.colors.textSecondary,
              margin: 0,
            }}
          >
            Upload multiple CSV files, detect transfers, and export unified financial data
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '32px' }}>
          {/* Progress Sidebar */}
          <div
            style={{
              backgroundColor: theme.colors.surface,
              padding: '24px',
              borderRadius: '12px',
              border: `1px solid ${theme.colors.border}`,
              height: 'fit-content',
            }}
          >
            <h3
              style={{
                color: theme.colors.text,
                marginBottom: '24px',
                fontWeight: '600',
              }}
            >
              Progress
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {steps.map((step, index) => {
                const Icon = step.icon;
                const isActive = index === activeStep;
                const isCompleted = index < activeStep;
                
                return (
                  <div
                    key={step.label}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      opacity: isActive || isCompleted ? 1 : 0.5,
                    }}
                  >
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        width: '40px',
                        height: '40px',
                        borderRadius: '50%',
                        backgroundColor: isActive || isCompleted ? theme.colors.primary : theme.colors.surfaceVariant,
                        color: isActive || isCompleted ? 'white' : theme.colors.textSecondary,
                      }}
                    >
                      <Icon size={20} />
                    </div>
                    <div>
                      <div
                        style={{
                          fontWeight: '500',
                          color: isActive ? theme.colors.primary : theme.colors.text,
                          marginBottom: '2px',
                        }}
                      >
                        {step.label}
                      </div>
                      <div
                        style={{
                          fontSize: '12px',
                          color: theme.colors.textSecondary,
                        }}
                      >
                        {step.description}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Main Content Area */}
          <div
            style={{
              backgroundColor: theme.colors.surface,
              padding: '32px',
              borderRadius: '12px',
              border: `1px solid ${theme.colors.border}`,
              minHeight: '500px',
            }}
          >
            {loading && (
              <div style={{ marginBottom: '16px' }}>
                <div
                  style={{
                    width: '100%',
                    height: '4px',
                    backgroundColor: theme.colors.surfaceVariant,
                    borderRadius: '2px',
                    overflow: 'hidden',
                  }}
                >
                  <div
                    style={{
                      height: '100%',
                      backgroundColor: theme.colors.primary,
                      borderRadius: '2px',
                      width: '30%',
                      animation: 'loading 2s ease-in-out infinite',
                    }}
                  />
                </div>
                <p
                  style={{
                    textAlign: 'center',
                    color: theme.colors.textSecondary,
                    margin: '8px 0 0 0',
                    fontSize: '14px',
                  }}
                >
                  Processing...
                </p>
              </div>
            )}

            {/* Step Content */}
            <div style={{ opacity: loading ? 0.5 : 1 }}>
              {activeStep === 0 && (
                <div>
                  <h3 style={{ color: theme.colors.text, marginBottom: '24px', fontWeight: '600' }}>
                    Upload Bank Statement Files
                  </h3>
                  <div
                    style={{
                      border: `2px dashed ${theme.colors.border}`,
                      borderRadius: '12px',
                      padding: '32px',
                      textAlign: 'center',
                      cursor: 'pointer',
                      backgroundColor: theme.colors.surfaceVariant,
                      transition: 'all 0.3s ease',
                    }}
                    onClick={handleFileSelect}
                  >
                    <CloudUpload size={48} style={{ color: theme.colors.primary, marginBottom: '16px' }} />
                    <h4 style={{ color: theme.colors.text, margin: '0 0 8px 0', fontWeight: '500' }}>
                      Drop CSV files here or click to browse
                    </h4>
                    <p style={{ color: theme.colors.textSecondary, margin: 0, fontSize: '14px' }}>
                      Supports multiple bank statement files
                    </p>
                  </div>
                  
                  {files.length > 0 && (
                    <div style={{ marginTop: '24px' }}>
                      <h4 style={{ color: theme.colors.text, marginBottom: '16px', fontWeight: '500' }}>
                        Uploaded Files ({files.length})
                      </h4>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {files.map((file, index) => (
                          <div
                            key={index}
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              padding: '16px',
                              backgroundColor: theme.colors.surface,
                              border: `1px solid ${theme.colors.border}`,
                              borderRadius: '8px',
                              gap: '12px',
                              animation: `fadeIn 0.3s ease ${index * 0.1}s both`,
                            }}
                          >
                            <FileText size={20} color={theme.colors.primary} />
                            <div style={{ flex: 1 }}>
                              <div style={{ fontWeight: '500', color: theme.colors.text, marginBottom: '4px' }}>
                                {file.name}
                              </div>
                              <div style={{ fontSize: '12px', color: theme.colors.textSecondary }}>
                                {file.size} • {file.bank}
                              </div>
                            </div>
                            <span
                              style={{
                                padding: '4px 8px',
                                borderRadius: '12px',
                                fontSize: '12px',
                                fontWeight: '500',
                                backgroundColor: file.status === 'configured' ? theme.colors.success : theme.colors.warning,
                                color: 'white',
                              }}
                            >
                              {file.status === 'configured' ? 'Ready' : 'Pending'}
                            </span>
                            <button
                              style={{
                                background: 'none',
                                border: 'none',
                                cursor: 'pointer',
                                padding: '4px',
                                borderRadius: '4px',
                                color: theme.colors.textSecondary,
                              }}
                            >
                              <Trash2 size={16} />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {activeStep === 1 && (
                <div>
                  <h3 style={{ color: theme.colors.text, marginBottom: '24px', fontWeight: '600' }}>
                    Bank Configuration
                  </h3>
                  <p style={{ color: theme.colors.textSecondary, marginBottom: '24px' }}>
                    Configure column mappings and categorization rules for each bank.
                  </p>
                  
                  {files.map((file, index) => (
                    <div
                      key={index}
                      style={{
                        border: `1px solid ${theme.colors.border}`,
                        borderRadius: '8px',
                        marginBottom: '16px',
                        overflow: 'hidden',
                      }}
                    >
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          padding: '16px',
                          backgroundColor: theme.colors.surface,
                          gap: '12px',
                        }}
                      >
                        <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '12px' }}>
                          <span style={{ fontWeight: '500', color: theme.colors.text }}>
                            {file.name}
                          </span>
                          <span
                            style={{
                              padding: '2px 8px',
                              borderRadius: '12px',
                              fontSize: '12px',
                              backgroundColor: theme.colors.surfaceVariant,
                              color: theme.colors.primary,
                              border: `1px solid ${theme.colors.primary}`,
                            }}
                          >
                            {file.bank}
                          </span>
                          {file.status === 'configured' && (
                            <Check size={16} color={theme.colors.success} />
                          )}
                        </div>
                      </div>
                      
                      <div style={{ 
                        padding: '16px', 
                        backgroundColor: theme.colors.surfaceVariant,
                        borderTop: `1px solid ${theme.colors.border}`
                      }}>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
                          <div>
                            <h4 style={{ 
                              color: theme.colors.text, 
                              marginBottom: '12px',
                              fontSize: '14px',
                              fontWeight: '500'
                            }}>
                              Column Mapping
                            </h4>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                <span style={{ color: theme.colors.text }}>Date</span>
                                <span style={{ color: theme.colors.textSecondary, fontSize: '12px' }}>Column A → 2024-06-15</span>
                              </div>
                              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                <span style={{ color: theme.colors.text }}>Amount</span>
                                <span style={{ color: theme.colors.textSecondary, fontSize: '12px' }}>Column B → -45.50</span>
                              </div>
                              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                <span style={{ color: theme.colors.text }}>Description</span>
                                <span style={{ color: theme.colors.textSecondary, fontSize: '12px' }}>Column C → Merchant</span>
                              </div>
                            </div>
                          </div>
                          <div>
                            <h4 style={{ 
                              color: theme.colors.text, 
                              marginBottom: '12px',
                              fontSize: '14px',
                              fontWeight: '500'
                            }}>
                              Categories Detected
                            </h4>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                              {['Groceries', 'Transportation', 'Dining', 'Income'].map((category) => (
                                <span
                                  key={category}
                                  style={{
                                    padding: '4px 8px',
                                    borderRadius: '12px',
                                    fontSize: '12px',
                                    backgroundColor: theme.colors.surface,
                                    color: theme.colors.text,
                                    border: `1px solid ${theme.colors.border}`,
                                  }}
                                >
                                  {category}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {activeStep === 2 && (
                <div>
                  <div style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center', 
                    marginBottom: '24px' 
                  }}>
                    <h3 style={{ 
                      color: theme.colors.text, 
                      margin: 0,
                      fontWeight: '600'
                    }}>
                      Transaction Preview
                    </h3>
                    <div style={{ display: 'flex', gap: '12px' }}>
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        padding: '6px 12px',
                        borderRadius: '16px',
                        backgroundColor: theme.colors.surfaceVariant,
                        border: `1px solid ${theme.colors.primary}`,
                      }}>
                        <TrendingUp size={16} color={theme.colors.primary} />
                        <span style={{ 
                          fontSize: '12px', 
                          color: theme.colors.primary,
                          fontWeight: '500'
                        }}>
                          {mockTransactions.length} transactions
                        </span>
                      </div>
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        padding: '6px 12px',
                        borderRadius: '16px',
                        backgroundColor: theme.colors.surfaceVariant,
                        border: `1px solid ${theme.colors.secondary}`,
                      }}>
                        <ArrowLeftRight size={16} color={theme.colors.secondary} />
                        <span style={{ 
                          fontSize: '12px', 
                          color: theme.colors.secondary,
                          fontWeight: '500'
                        }}>
                          2 transfers detected
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div style={{
                    border: `1px solid ${theme.colors.border}`,
                    borderRadius: '8px',
                    overflow: 'hidden',
                    backgroundColor: theme.colors.surface,
                  }}>
                    <div style={{
                      display: 'grid',
                      gridTemplateColumns: '120px 1fr 120px 120px 100px',
                      gap: '16px',
                      padding: '16px',
                      backgroundColor: theme.colors.surfaceVariant,
                      fontWeight: '500',
                      fontSize: '14px',
                      color: theme.colors.text,
                    }}>
                      <div>Date</div>
                      <div>Description</div>
                      <div>Category</div>
                      <div>Account</div>
                      <div style={{ textAlign: 'right' }}>Amount</div>
                    </div>
                    {mockTransactions.map((transaction, index) => (
                      <div
                        key={index}
                        style={{
                          display: 'grid',
                          gridTemplateColumns: '120px 1fr 120px 120px 100px',
                          gap: '16px',
                          padding: '16px',
                          borderTop: index > 0 ? `1px solid ${theme.colors.border}` : 'none',
                          animation: `fadeIn 0.3s ease ${index * 0.1}s both`,
                        }}
                      >
                        <div style={{ color: theme.colors.text, fontSize: '14px' }}>
                          {transaction.date}
                        </div>
                        <div style={{ color: theme.colors.text, fontSize: '14px' }}>
                          {transaction.description}
                        </div>
                        <div>
                          <span
                            style={{
                              padding: '4px 8px',
                              borderRadius: '12px',
                              fontSize: '12px',
                              fontWeight: '500',
                              backgroundColor: transaction.category === 'Income' ? theme.colors.success : theme.colors.surfaceVariant,
                              color: transaction.category === 'Income' ? 'white' : theme.colors.text,
                            }}
                          >
                            {transaction.category}
                          </span>
                        </div>
                        <div style={{ color: theme.colors.text, fontSize: '14px' }}>
                          {transaction.account}
                        </div>
                        <div
                          style={{
                            textAlign: 'right',
                            color: transaction.amount > 0 ? theme.colors.success : theme.colors.text,
                            fontWeight: '500',
                            fontSize: '14px',
                          }}
                        >
                          {transaction.amount > 0 ? '+' : ''}${Math.abs(transaction.amount).toFixed(2)}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeStep === 3 && (
                <div style={{ textAlign: 'center', padding: '32px 0' }}>
                  <Check 
                    size={64} 
                    style={{ 
                      color: theme.colors.success, 
                      marginBottom: '16px',
                      padding: '12px',
                      borderRadius: '50%',
                      backgroundColor: `${theme.colors.success}20`,
                    }} 
                  />
                  <h2 style={{ 
                    color: theme.colors.text, 
                    marginBottom: '8px',
                    fontWeight: '600'
                  }}>
                    Export Complete!
                  </h2>
                  <p style={{ 
                    color: theme.colors.textSecondary, 
                    marginBottom: '24px',
                    fontSize: '16px'
                  }}>
                    Your unified transaction data has been processed and is ready for download.
                  </p>
                  <button
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '8px',
                      padding: '12px 24px',
                      backgroundColor: theme.colors.primary,
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      fontSize: '16px',
                      fontWeight: '500',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                    }}
                  >
                    <Download size={20} />
                    Download CSV
                  </button>
                </div>
              )}
            </div>

            {/* Navigation Buttons */}
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginTop: '32px',
                paddingTop: '16px',
                borderTop: `1px solid ${theme.colors.border}`,
              }}
            >
              <button
                disabled={activeStep === 0 || loading}
                onClick={handleBack}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '10px 20px',
                  backgroundColor: 'transparent',
                  border: `1px solid ${theme.colors.border}`,
                  borderRadius: '8px',
                  color: theme.colors.text,
                  cursor: activeStep === 0 || loading ? 'not-allowed' : 'pointer',
                  opacity: activeStep === 0 || loading ? 0.5 : 1,
                  transition: 'all 0.2s ease',
                }}
              >
                <ChevronLeft size={16} />
                Back
              </button>
              <button
                onClick={handleNext}
                disabled={activeStep === steps.length - 1 || loading}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '10px 20px',
                  backgroundColor: theme.colors.primary,
                  border: 'none',
                  borderRadius: '8px',
                  color: 'white',
                  cursor: activeStep === steps.length - 1 || loading ? 'not-allowed' : 'pointer',
                  opacity: activeStep === steps.length - 1 || loading ? 0.5 : 1,
                  transition: 'all 0.2s ease',
                  minWidth: '120px',
                  justifyContent: 'center',
                }}
              >
                {activeStep === steps.length - 2 ? 'Process & Export' : 'Next'}
                <ChevronRight size={16} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HisaabFlowPrototype;