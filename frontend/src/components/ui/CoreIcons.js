// Core Icons - Most commonly used icons
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

// File & Upload Icons
export const CloudUpload = (props) => (
  <IconWrapper {...props}>
    <path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242" />
    <path d="m12 12 4-4-4-4" />
    <path d="M16 8H8" />
  </IconWrapper>
);

export const FileText = (props) => (
  <IconWrapper {...props}>
    <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
  </IconWrapper>
);

export const Download = (props) => (
  <IconWrapper {...props}>
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="7,10 12,15 17,10" />
    <line x1="12" x2="12" y1="15" y2="3" />
  </IconWrapper>
);

// Navigation Icons
export const ChevronLeft = (props) => (
  <IconWrapper {...props}>
    <polyline points="15,18 9,12 15,6" />
  </IconWrapper>
);

export const ChevronRight = (props) => (
  <IconWrapper {...props}>
    <polyline points="9,18 15,12 9,6" />
  </IconWrapper>
);

export const ChevronDown = (props) => (
  <IconWrapper {...props}>
    <polyline points="6,9 12,15 18,9" />
  </IconWrapper>
);

export const ChevronUp = (props) => (
  <IconWrapper {...props}>
    <polyline points="18,15 12,9 6,15" />
  </IconWrapper>
);

// Action Icons
export const Settings = (props) => (
  <IconWrapper {...props}>
    <circle cx="12" cy="12" r="3" />
    <path d="m12 1 1.68 3.36L17 6.64l-1.32 2.68L19 12l-3.32 2.68L17 17.36l-3.32 1.32L12 23l-1.68-3.36L7 17.36l1.32-2.68L5 12l3.32-2.68L7 6.64l3.32-1.32L12 1z" />
  </IconWrapper>
);

export const Eye = (props) => (
  <IconWrapper {...props}>
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
    <circle cx="12" cy="12" r="3" />
  </IconWrapper>
);

export const Edit = (props) => (
  <IconWrapper {...props}>
    <path d="m12 20h9" />
    <path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z" />
  </IconWrapper>
);

export const Trash2 = (props) => (
  <IconWrapper {...props}>
    <polyline points="3,6 5,6 21,6" />
    <path d="m19,6v14a2,2 0 0,1-2,2H7a2,2 0 0,1-2-2V6m3,0V4a2,2 0 0,1 2-2h4a2,2 0 0,1 2,2v2" />
  </IconWrapper>
);

// Status Icons
export const Check = (props) => (
  <IconWrapper {...props}>
    <polyline points="20,6 9,17 4,12" />
  </IconWrapper>
);

export const X = (props) => (
  <IconWrapper {...props}>
    <path d="m18 6-12 12" />
    <path d="m6 6 12 12" />
  </IconWrapper>
);

export const AlertCircle = (props) => (
  <IconWrapper {...props}>
    <circle cx="12" cy="12" r="10" />
    <line x1="12" x2="12" y1="8" y2="12" />
    <line x1="12" x2="12.01" y1="16" y2="16" />
  </IconWrapper>
);

export const CheckCircle = (props) => (
  <IconWrapper {...props}>
    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
    <polyline points="22,4 12,14.01 9,11.01" />
  </IconWrapper>
);

// Theme Icons
export const Sun = (props) => (
  <IconWrapper {...props}>
    <circle cx="12" cy="12" r="5" />
    <path d="m12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72 1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
  </IconWrapper>
);

export const Moon = (props) => (
  <IconWrapper {...props}>
    <path d="M12 3a6.364 6.364 0 0 0 9 9 9 9 0 1 1-9-9Z" />
  </IconWrapper>
);

export const Calendar = (props) => (
  <IconWrapper {...props}>
    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
    <line x1="16" x2="16" y1="2" y2="6" />
    <line x1="8" x2="8" y1="2" y2="6" />
    <line x1="3" x2="21" y1="10" y2="10" />
  </IconWrapper>
);

export default {
  CloudUpload, FileText, Download,
  ChevronLeft, ChevronRight, ChevronDown, ChevronUp,
  Settings, Eye, Edit, Trash2,
  Check, X, AlertCircle, CheckCircle,
  Sun, Moon, Calendar,
};