import React from 'react';

// ============================================
// FUNDINVESTIGATOR - FINAL BRAND PACKAGE
// Locked Design: FIN in dark lens, short handle
// ============================================

/*
BRAND SPECIFICATIONS
====================

COLORS:
- Navy (Primary):     #1E3A5F
- Gold (Accent):      #D4AF37  
- White:              #FFFFFF
- Gray (Secondary):   #64748B
- Light Gray:         #94A3B8

TYPOGRAPHY:
- Font Family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif
- Alternative: Inter, SF Pro, Segoe UI
- Fund: 700 (Bold)
- Investigator: 400 (Regular)
- FIN: 700 (Bold)

LOGO SPECS:
- Lens radius: 36px (in primary logo)
- Handle: 4px stroke, 60% shortened
- FIN font-size: 24px (centered in lens)
- Wordmark gap from lens: 10px
*/

const colors = {
  navy: "#1E3A5F",
  gold: "#D4AF37",
  white: "#FFFFFF",
  gray: "#64748B",
  lightGray: "#94A3B8",
};

// ============================================
// PRIMARY LOGO
// ============================================
export const LogoPrimary = ({ width = 280 }) => (
  <svg width={width} height={width * 0.28} viewBox="0 0 280 78" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="42" cy="38" r="36" fill={colors.navy}/>
    <text x="42" y="47" fontFamily="system-ui, -apple-system, BlinkMacSystemFont, sans-serif" fontSize="24" fontWeight="700" fill={colors.white} textAnchor="middle">
      <tspan fill={colors.white}>F</tspan><tspan fill={colors.gold}>I</tspan><tspan fill={colors.white}>N</tspan>
    </text>
    <line x1="68" y1="64" x2="76" y2="72" stroke={colors.navy} strokeWidth="4" strokeLinecap="round"/>
    <text x="88" y="35" fontFamily="system-ui, -apple-system, BlinkMacSystemFont, sans-serif" fontSize="28" fontWeight="700" fill={colors.navy}>Fund</text>
    <text x="88" y="60" fontFamily="system-ui, -apple-system, BlinkMacSystemFont, sans-serif" fontSize="18" fontWeight="400" fill={colors.gray}>Investigator</text>
  </svg>
);

// ============================================
// LOGO FOR DARK BACKGROUNDS
// ============================================
export const LogoPrimaryDark = ({ width = 280 }) => (
  <svg width={width} height={width * 0.28} viewBox="0 0 280 78" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="42" cy="38" r="36" fill={colors.white}/>
    <text x="42" y="47" fontFamily="system-ui, -apple-system, BlinkMacSystemFont, sans-serif" fontSize="24" fontWeight="700" fill={colors.navy} textAnchor="middle">
      <tspan fill={colors.navy}>F</tspan><tspan fill={colors.gold}>I</tspan><tspan fill={colors.navy}>N</tspan>
    </text>
    <line x1="68" y1="64" x2="76" y2="72" stroke={colors.white} strokeWidth="4" strokeLinecap="round"/>
    <text x="88" y="35" fontFamily="system-ui, -apple-system, BlinkMacSystemFont, sans-serif" fontSize="28" fontWeight="700" fill={colors.white}>Fund</text>
    <text x="88" y="60" fontFamily="system-ui, -apple-system, BlinkMacSystemFont, sans-serif" fontSize="18" fontWeight="400" fill={colors.lightGray}>Investigator</text>
  </svg>
);

// ============================================
// LOGO WITH TAGLINE
// ============================================
export const LogoWithTagline = ({ width = 280 }) => (
  <svg width={width} height={width * 0.35} viewBox="0 0 280 98" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="42" cy="38" r="36" fill={colors.navy}/>
    <text x="42" y="47" fontFamily="system-ui, -apple-system, BlinkMacSystemFont, sans-serif" fontSize="24" fontWeight="700" fill={colors.white} textAnchor="middle">
      <tspan fill={colors.white}>F</tspan><tspan fill={colors.gold}>I</tspan><tspan fill={colors.white}>N</tspan>
    </text>
    <line x1="68" y1="64" x2="76" y2="72" stroke={colors.navy} strokeWidth="4" strokeLinecap="round"/>
    <text x="88" y="32" fontFamily="system-ui, -apple-system, BlinkMacSystemFont, sans-serif" fontSize="26" fontWeight="700" fill={colors.navy}>Fund</text>
    <text x="88" y="55" fontFamily="system-ui, -apple-system, BlinkMacSystemFont, sans-serif" fontSize="17" fontWeight="400" fill={colors.gray}>Investigator</text>
    <text x="88" y="78" fontFamily="system-ui, -apple-system, BlinkMacSystemFont, sans-serif" fontSize="11" fontWeight="500" fill={colors.lightGray} letterSpacing="0.5">Know your Fund</text>
  </svg>
);

// ============================================
// ICON ONLY
// ============================================
export const IconOnly = ({ size = 100 }) => (
  <svg width={size} height={size} viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="44" cy="44" r="40" fill={colors.navy}/>
    <text x="44" y="54" fontFamily="system-ui, -apple-system, sans-serif" fontSize="28" fontWeight="700" fill={colors.white} textAnchor="middle">
      <tspan fill={colors.white}>F</tspan><tspan fill={colors.gold}>I</tspan><tspan fill={colors.white}>N</tspan>
    </text>
    <line x1="73" y1="73" x2="82" y2="82" stroke={colors.navy} strokeWidth="5" strokeLinecap="round"/>
  </svg>
);

// ============================================
// APP ICON
// ============================================
export const AppIcon = ({ size = 80 }) => (
  <svg width={size} height={size} viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="80" height="80" rx="18" fill={colors.navy}/>
    <circle cx="36" cy="36" r="24" fill={colors.white} fillOpacity="0.12" stroke={colors.gold} strokeWidth="2"/>
    <text x="36" y="44" fontFamily="system-ui, sans-serif" fontSize="16" fontWeight="700" fill={colors.white} textAnchor="middle">
      <tspan fill={colors.white}>F</tspan><tspan fill={colors.gold}>I</tspan><tspan fill={colors.white}>N</tspan>
    </text>
    <line x1="54" y1="54" x2="62" y2="62" stroke={colors.gold} strokeWidth="3" strokeLinecap="round"/>
  </svg>
);

// ============================================
// FAVICON (32px)
// ============================================
export const Favicon = ({ size = 32 }) => (
  <svg width={size} height={size} viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="32" height="32" rx="7" fill={colors.navy}/>
    <text x="16" y="20" fontFamily="system-ui, sans-serif" fontSize="10" fontWeight="700" fill={colors.white} textAnchor="middle">
      <tspan fill={colors.white}>F</tspan><tspan fill={colors.gold}>I</tspan><tspan fill={colors.white}>N</tspan>
    </text>
  </svg>
);

// ============================================
// SOCIAL AVATAR (Circular)
// ============================================
export const SocialAvatar = ({ size = 100 }) => (
  <svg width={size} height={size} viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="50" cy="50" r="48" fill={colors.navy}/>
    <circle cx="46" cy="46" r="28" fill={colors.white} fillOpacity="0.1" stroke={colors.gold} strokeWidth="2"/>
    <text x="46" y="54" fontFamily="system-ui, sans-serif" fontSize="18" fontWeight="700" fill={colors.white} textAnchor="middle">
      <tspan fill={colors.white}>F</tspan><tspan fill={colors.gold}>I</tspan><tspan fill={colors.white}>N</tspan>
    </text>
    <line x1="66" y1="66" x2="74" y2="74" stroke={colors.gold} strokeWidth="3" strokeLinecap="round"/>
  </svg>
);

// ============================================
// STACKED LOGO
// ============================================
export const LogoStacked = ({ width = 140 }) => (
  <svg width={width} height={width * 1.25} viewBox="0 0 140 175" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="70" cy="55" r="48" fill={colors.navy}/>
    <text x="70" y="65" fontFamily="system-ui, sans-serif" fontSize="32" fontWeight="700" fill={colors.white} textAnchor="middle">
      <tspan fill={colors.white}>F</tspan><tspan fill={colors.gold}>I</tspan><tspan fill={colors.white}>N</tspan>
    </text>
    <line x1="105" y1="90" x2="115" y2="100" stroke={colors.navy} strokeWidth="5" strokeLinecap="round"/>
    <text x="70" y="138" fontFamily="system-ui, sans-serif" fontSize="24" fontWeight="700" fill={colors.navy} textAnchor="middle">Fund</text>
    <text x="70" y="160" fontFamily="system-ui, sans-serif" fontSize="14" fontWeight="400" fill={colors.gray} textAnchor="middle">Investigator</text>
  </svg>
);

// ============================================
// WORDMARK ONLY
// ============================================
export const Wordmark = ({ width = 200 }) => (
  <svg width={width} height={width * 0.18} viewBox="0 0 200 36" fill="none" xmlns="http://www.w3.org/2000/svg">
    <text x="0" y="26" fontFamily="system-ui, -apple-system, BlinkMacSystemFont, sans-serif" fontSize="26" fontWeight="700" fill={colors.navy}>Fund</text>
    <text x="68" y="26" fontFamily="system-ui, -apple-system, BlinkMacSystemFont, sans-serif" fontSize="26" fontWeight="400" fill={colors.gray}>Investigator</text>
  </svg>
);

// ============================================
// SHOWCASE COMPONENT
// ============================================
export default function FundInvestigatorBrandPackage() {
  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-4xl mx-auto">
        
        {/* Header */}
        <div className="mb-10">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">FundInvestigator</h1>
          <p className="text-slate-500">Brand Package — Final</p>
        </div>

        {/* Brand Specifications */}
        <div className="bg-white rounded-2xl p-6 shadow-sm mb-8">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Brand Specifications</h2>
          
          {/* Colors */}
          <div className="mb-6">
            <h3 className="text-sm font-medium text-slate-600 mb-3">Colors</h3>
            <div className="flex gap-4">
              <div className="flex flex-col items-center">
                <div className="w-14 h-14 rounded-xl shadow" style={{ backgroundColor: '#1E3A5F' }}></div>
                <span className="text-xs font-medium text-slate-700 mt-2">Navy</span>
                <span className="text-xs text-slate-400">#1E3A5F</span>
              </div>
              <div className="flex flex-col items-center">
                <div className="w-14 h-14 rounded-xl shadow" style={{ backgroundColor: '#D4AF37' }}></div>
                <span className="text-xs font-medium text-slate-700 mt-2">Gold</span>
                <span className="text-xs text-slate-400">#D4AF37</span>
              </div>
              <div className="flex flex-col items-center">
                <div className="w-14 h-14 rounded-xl shadow border" style={{ backgroundColor: '#FFFFFF' }}></div>
                <span className="text-xs font-medium text-slate-700 mt-2">White</span>
                <span className="text-xs text-slate-400">#FFFFFF</span>
              </div>
              <div className="flex flex-col items-center">
                <div className="w-14 h-14 rounded-xl shadow" style={{ backgroundColor: '#64748B' }}></div>
                <span className="text-xs font-medium text-slate-700 mt-2">Gray</span>
                <span className="text-xs text-slate-400">#64748B</span>
              </div>
              <div className="flex flex-col items-center">
                <div className="w-14 h-14 rounded-xl shadow" style={{ backgroundColor: '#94A3B8' }}></div>
                <span className="text-xs font-medium text-slate-700 mt-2">Light Gray</span>
                <span className="text-xs text-slate-400">#94A3B8</span>
              </div>
            </div>
          </div>

          {/* Typography */}
          <div>
            <h3 className="text-sm font-medium text-slate-600 mb-3">Typography</h3>
            <div className="bg-slate-50 rounded-lg p-4 text-sm">
              <p className="mb-2"><strong>Font Family:</strong> system-ui, -apple-system, BlinkMacSystemFont, sans-serif</p>
              <p className="mb-2"><strong>Web Alternative:</strong> Inter, SF Pro Display, Segoe UI</p>
              <p className="mb-2"><strong>"Fund":</strong> 700 (Bold), #1E3A5F</p>
              <p className="mb-2"><strong>"Investigator":</strong> 400 (Regular), #64748B</p>
              <p><strong>"FIN":</strong> 700 (Bold), White with Gold "I"</p>
            </div>
          </div>
        </div>

        {/* Primary Logo */}
        <div className="bg-white rounded-2xl p-8 shadow-sm mb-6">
          <h2 className="text-sm font-medium text-slate-500 mb-4">Primary Logo</h2>
          <div className="flex justify-center p-6 bg-slate-50 rounded-xl">
            <LogoPrimary width={320} />
          </div>
        </div>

        {/* With Tagline */}
        <div className="bg-white rounded-2xl p-8 shadow-sm mb-6">
          <h2 className="text-sm font-medium text-slate-500 mb-4">With Tagline</h2>
          <div className="flex justify-center p-6 bg-slate-50 rounded-xl">
            <LogoWithTagline width={320} />
          </div>
        </div>

        {/* Dark Background */}
        <div className="bg-white rounded-2xl p-8 shadow-sm mb-6">
          <h2 className="text-sm font-medium text-slate-500 mb-4">On Dark Background</h2>
          <div className="flex justify-center p-6 bg-slate-900 rounded-xl">
            <LogoPrimaryDark width={320} />
          </div>
        </div>

        {/* Stacked */}
        <div className="bg-white rounded-2xl p-8 shadow-sm mb-6">
          <h2 className="text-sm font-medium text-slate-500 mb-4">Stacked Logo</h2>
          <div className="flex justify-center p-6 bg-slate-50 rounded-xl">
            <LogoStacked width={160} />
          </div>
        </div>

        {/* Icon Only */}
        <div className="bg-white rounded-2xl p-8 shadow-sm mb-6">
          <h2 className="text-sm font-medium text-slate-500 mb-4">Icon Only</h2>
          <div className="flex justify-center p-6 bg-slate-50 rounded-xl">
            <IconOnly size={120} />
          </div>
        </div>

        {/* App Icons */}
        <div className="bg-white rounded-2xl p-8 shadow-sm mb-6">
          <h2 className="text-sm font-medium text-slate-500 mb-4">App Icons</h2>
          <div className="flex items-end justify-center gap-6 p-6">
            <div className="flex flex-col items-center gap-2">
              <AppIcon size={80} />
              <span className="text-xs text-slate-400">80px</span>
            </div>
            <div className="flex flex-col items-center gap-2">
              <AppIcon size={64} />
              <span className="text-xs text-slate-400">64px</span>
            </div>
            <div className="flex flex-col items-center gap-2">
              <AppIcon size={48} />
              <span className="text-xs text-slate-400">48px</span>
            </div>
            <div className="flex flex-col items-center gap-2">
              <Favicon size={32} />
              <span className="text-xs text-slate-400">32px</span>
            </div>
          </div>
        </div>

        {/* Social Avatar */}
        <div className="bg-white rounded-2xl p-8 shadow-sm mb-6">
          <h2 className="text-sm font-medium text-slate-500 mb-4">Social Avatar</h2>
          <div className="flex justify-center gap-6 p-6">
            <SocialAvatar size={100} />
            <SocialAvatar size={64} />
          </div>
        </div>

        {/* Wordmark */}
        <div className="bg-white rounded-2xl p-8 shadow-sm mb-6">
          <h2 className="text-sm font-medium text-slate-500 mb-4">Wordmark Only</h2>
          <div className="flex justify-center p-6 bg-slate-50 rounded-xl">
            <Wordmark width={240} />
          </div>
        </div>

        {/* Summary */}
        <div className="bg-slate-900 rounded-2xl p-6 text-white">
          <h2 className="font-semibold mb-4">Brand Summary</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
            <div>
              <p className="text-slate-400">Brand</p>
              <p>FundInvestigator</p>
            </div>
            <div>
              <p className="text-slate-400">Tagline</p>
              <p>Know your Fund</p>
            </div>
            <div>
              <p className="text-slate-400">Mark</p>
              <p>F<span className="text-amber-400">I</span>N in lens</p>
            </div>
            <div>
              <p className="text-slate-400">Primary</p>
              <p>Navy #1E3A5F</p>
            </div>
            <div>
              <p className="text-slate-400">Accent</p>
              <p>Gold #D4AF37</p>
            </div>
            <div>
              <p className="text-slate-400">Domain</p>
              <p>fundinvestigator.com</p>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
