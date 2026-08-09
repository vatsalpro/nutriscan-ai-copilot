import React from 'react';

export default function InstagramCameraIcon({ size = 'md', className = '' }) {
  const dimensions = {
    sm: 'w-7 h-7 p-1 rounded-xl',
    md: 'w-11 h-11 p-2 rounded-2xl',
    lg: 'w-20 h-20 p-4 rounded-3xl',
    xl: 'w-24 h-24 p-5 rounded-[2rem]'
  };

  const svgSizes = {
    sm: 18,
    md: 26,
    lg: 48,
    xl: 56
  };

  const sizeClass = dimensions[size] || dimensions.md;
  const svgSize = svgSizes[size] || 26;

  return (
    <div className={`relative inline-flex items-center justify-center bg-gradient-to-tr from-emerald-400 via-teal-400 to-cyan-400 shadow-lg shadow-emerald-500/25 border border-white/40 hover:scale-110 hover:rotate-6 transition-all duration-300 cute-float ${sizeClass} ${className}`}>
      {/* Glossy sheen overlay */}
      <div className="absolute inset-0 rounded-[inherit] bg-gradient-to-b from-white/30 via-transparent to-black/10 pointer-events-none" />
      
      {/* Clean, cute camera icon vector */}
      <svg
        width={svgSize}
        height={svgSize}
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="text-slate-950 drop-shadow-sm relative z-10"
      >
        <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z" />
        <circle cx="12" cy="13" r="3" />
      </svg>
    </div>
  );
}

