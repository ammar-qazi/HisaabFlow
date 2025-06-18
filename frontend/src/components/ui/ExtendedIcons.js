// Extended Icons - Financial and data visualization icons
import React from 'react';

const IconWrapper = ({ children, size = 24, color = 'currentColor', className = '', ...props }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke={color}
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
    {...props}
  >
    {children}
  </svg>
);

// Financial Icons
export const Building = (props) => (
  <IconWrapper {...props}>
    <path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z" />
    <path d="M6 12h4m4 0h4M6 16h4m4 0h4M6 8h4m4 0h4" />
  </IconWrapper>
);

export const CreditCard = (props) => (
  <IconWrapper {...props}>
    <rect width="20" height="14" x="2" y="5" rx="2" />
    <line x1="2" x2="22" y1="10" y2="10" />
  </IconWrapper>
);

export const DollarSign = (props) => (
  <IconWrapper {...props}>
    <line x1="12" x2="12" y1="1" y2="23" />
    <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
  </IconWrapper>
);

export const TrendingUp = (props) => (
  <IconWrapper {...props}>
    <polyline points="22,7 13.5,15.5 8.5,10.5 2,17" />
    <polyline points="16,7 22,7 22,13" />
  </IconWrapper>
);

export const TrendingDown = (props) => (
  <IconWrapper {...props}>
    <polyline points="22,17 13.5,8.5 8.5,13.5 2,7" />
    <polyline points="16,17 22,17 22,11" />
  </IconWrapper>
);

// Transfer & Exchange Icons
export const ArrowLeftRight = (props) => (
  <IconWrapper {...props}>
    <path d="M8 3 4 7l4 4" />
    <path d="M4 7h16" />
    <path d="m16 21 4-4-4-4" />
    <path d="M20 17H4" />
  </IconWrapper>
);

export const RefreshCw = (props) => (
  <IconWrapper {...props}>
    <path d="m3 12 3-3 3 3" />
    <path d="M6 9V7a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2" />
    <path d="m21 12-3 3-3-3" />
    <path d="M18 15v2a4 4 0 0 1-4 4H10a4 4 0 0 1-4-4v-2" />
  </IconWrapper>
);

// Data Icons
export const BarChart = (props) => (
  <IconWrapper {...props}>
    <line x1="12" x2="12" y1="20" y2="10" />
    <line x1="18" x2="18" y1="20" y2="4" />
    <line x1="6" x2="6" y1="20" y2="16" />
  </IconWrapper>
);

export const PieChart = (props) => (
  <IconWrapper {...props}>
    <path d="M21.21 15.89A10 10 0 1 1 8 2.83" />
    <path d="M22 12A10 10 0 0 0 12 2v10z" />
  </IconWrapper>
);

// Category Icons
export const Tag = (props) => (
  <IconWrapper {...props}>
    <path d="M12 2H2v10l9.29 9.29c.94.94 2.48.94 3.42 0l6.58-6.58c.94-.94.94-2.48 0-3.42L12 2Z" />
    <path d="M7 7h.01" />
  </IconWrapper>
);

export const Folder = (props) => (
  <IconWrapper {...props}>
    <path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z" />
  </IconWrapper>
);

// Plus/Minus for expandable sections
export const Plus = (props) => (
  <IconWrapper {...props}>
    <path d="M5 12h14" />
    <path d="M12 5v14" />
  </IconWrapper>
);

export const Minus = (props) => (
  <IconWrapper {...props}>
    <path d="M5 12h14" />
  </IconWrapper>
);

// Additional utility icons
export const Search = (props) => (
  <IconWrapper {...props}>
    <circle cx="11" cy="11" r="8" />
    <path d="m21 21-4.35-4.35" />
  </IconWrapper>
);

export const Filter = (props) => (
  <IconWrapper {...props}>
    <polygon points="22,3 2,3 10,12.46 10,19 14,21 14,12.46 22,3" />
  </IconWrapper>
);

export default {
  Building, CreditCard, DollarSign, TrendingUp, TrendingDown,
  ArrowLeftRight, RefreshCw,
  BarChart, PieChart,
  Tag, Folder,
  Plus, Minus,
  Search, Filter,
};