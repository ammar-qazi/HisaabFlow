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

// HisaabFlow Logo - Professional S-shaped design
export const Logo = (props) => (
  <IconWrapper {...props}>
    <g transform="scale(0.033, 0.033)">
      {/* Top curved section */}
      <path
        fill="currentColor"
        opacity="1.000000"
        stroke="none"
        d="M365.401123,313.422363 C347.106201,327.672852 329.476410,342.192719 313.044434,358.040466 C287.607361,382.573120 271.342621,411.729858 268.943054,447.784027 C268.288666,457.616486 268.396088,467.418854 268.169647,477.235321 C268.115906,479.565704 268.176666,481.877258 267.433899,484.154388 C265.263031,490.809814 261.903809,491.951691 255.316299,489.638031 C246.667862,486.600586 241.349274,479.407867 234.456161,474.209076 C225.993500,467.826508 218.454178,460.362366 210.598724,453.269073 C207.784561,450.727905 204.696121,448.226562 201.726089,445.708801 C199.727097,444.014282 197.660324,442.192169 194.341812,443.091187 C193.201843,436.434662 187.514084,433.321320 183.346008,429.204620 C171.422913,417.428650 159.943314,405.394592 152.400925,390.191254 C137.237564,359.626190 135.472107,328.574554 148.166397,296.613953 C159.170303,268.909210 177.223587,246.798584 199.841568,227.891708 C232.439941,200.641998 266.634888,175.424225 299.801697,148.900848 C323.735077,129.761383 347.653961,110.603806 371.582977,91.458878 C381.722656,83.346405 392.829773,79.233986 405.976532,82.736778 C410.090759,83.832954 413.805725,85.632019 417.241394,87.967758 C449.756989,110.073395 481.775269,132.872040 512.028809,158.021912 C519.238831,164.015579 524.842102,171.354294 522.210938,181.847366 C520.770752,187.590576 517.078003,191.881317 512.850769,195.733032 C498.931671,208.415497 483.641174,219.398468 468.915741,231.083420 C434.471619,258.415527 400.083618,285.818390 365.401123,313.422363 z"
      />

      {/* Bottom curved section */}
      <path
        fill="currentColor"
        opacity="1.000000"
        stroke="none"
        d="M613.209595,472.076233 C601.369446,494.326263 584.091858,511.259186 565.009338,526.633545 C542.056152,545.126465 519.222534,563.767700 496.297455,582.295715 C472.248138,601.732422 448.245667,621.229248 424.018768,640.442688 C416.760925,646.198547 409.695740,652.376648 401.175873,656.354675 C387.880798,662.562317 374.813385,661.580627 363.006073,653.230835 C351.104065,644.813965 340.219727,634.964600 328.381836,626.448669 C313.710052,615.894104 300.154144,603.944397 285.655426,593.162170 C278.187592,587.608582 269.790070,581.832092 268.498749,570.572266 C267.151398,558.823914 271.917267,550.155273 280.116394,542.887512 C296.574463,528.298950 314.278748,515.227478 331.367859,501.405121 C357.262604,480.460358 383.681335,460.173706 409.407562,439.010529 C430.886169,421.341492 452.784058,404.179779 473.825439,385.981232 C488.575409,373.224121 501.462830,359.024536 508.923523,340.563141 C513.926270,328.183929 515.377441,315.169678 516.807190,302.083801 C517.317505,297.413330 516.989990,292.462952 519.342224,288.296417 C521.668396,287.862366 522.937012,289.093536 524.270081,290.010193 C550.936157,308.345795 576.270935,328.361420 600.046570,350.324707 C616.450134,365.477905 623.849670,384.899506 626.091003,406.585419 C628.465210,429.556885 624.173279,451.305756 613.209595,472.076233 z"
      />
    </g>
  </IconWrapper>
);

// Building icon (actual building for UI elements)
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
  Logo, Building, CreditCard, DollarSign, TrendingUp, TrendingDown,
  ArrowLeftRight, RefreshCw,
  BarChart, PieChart,
  Tag, Folder,
  Plus, Minus,
  Search, Filter,
};