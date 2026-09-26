import React from 'react';

export const RobotHero: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center my-6 select-none">
      {/* Robot SVG Container with Glow */}
      <div className="relative w-36 h-36 flex items-center justify-center">
        {/* Ambient background glow */}
        <div className="absolute inset-0 bg-blue-500/20 blur-2xl rounded-full scale-125 animate-pulse-subtle pointer-events-none" />
        <div className="absolute -bottom-4 w-28 h-6 bg-cyan-400/20 blur-lg rounded-full pointer-events-none" />

        <svg 
          viewBox="0 0 200 200" 
          className="w-28 h-28 relative z-10 drop-shadow-[0_0_20px_rgba(56,189,248,0.4)] animate-float"
        >
          <defs>
            {/* Robot Head Gradient */}
            <linearGradient id="robotHeadGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#38bdf8" />
              <stop offset="50%" stopColor="#2563eb" />
              <stop offset="100%" stopColor="#1e3a8a" />
            </linearGradient>

            {/* Earphone Outer Gradient */}
            <linearGradient id="earGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#60a5fa" />
              <stop offset="100%" stopColor="#1d4ed8" />
            </linearGradient>

            {/* Visor Screen Gradient */}
            <radialGradient id="visorGrad" cx="50%" cy="40%" r="60%">
              <stop offset="0%" stopColor="#08142c" />
              <stop offset="85%" stopColor="#040915" />
              <stop offset="100%" stopColor="#020610" />
            </radialGradient>

            {/* Eye Glow Filter */}
            <filter id="eyeGlow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="2.5" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>

            {/* Sparkle Glow Filter */}
            <filter id="sparkleGlow" x="-30%" y="-30%" width="160%" height="160%">
              <feGaussianBlur stdDeviation="2" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Sparkles / Stars around the robot matching screenshot */}
          {/* Sparkle 1: Top Left */}
          <path 
            d="M 45 42 Q 45 52 35 52 Q 45 52 45 62 Q 45 52 55 52 Q 45 52 45 42 Z" 
            fill="#38bdf8" 
            opacity="0.85"
            filter="url(#sparkleGlow)"
          />
          {/* Sparkle 2: Top Right */}
          <path 
            d="M 160 38 Q 160 46 152 46 Q 160 46 160 54 Q 160 46 168 46 Q 160 46 160 38 Z" 
            fill="#60a5fa" 
            opacity="0.8"
            filter="url(#sparkleGlow)"
          />
          {/* Sparkle 3: Bottom Right */}
          <path 
            d="M 165 125 Q 165 131 159 131 Q 165 131 165 137 Q 165 131 171 131 Q 165 131 165 125 Z" 
            fill="#38bdf8" 
            opacity="0.75"
            filter="url(#sparkleGlow)"
          />
          {/* Sparkle 4: Bottom Left small */}
          <circle cx="36" cy="120" r="2" fill="#93c5fd" opacity="0.6" />

          {/* Neck / Base connection */}
          <rect x="92" y="146" width="16" height="12" rx="4" fill="#1e3a8a" />
          <path d="M 78 158 Q 100 162 122 158 L 116 164 Q 100 168 84 164 Z" fill="#2563eb" opacity="0.8" />

          {/* Left Earphone / Antenna */}
          <rect x="36" y="85" width="14" height="34" rx="7" fill="url(#earGrad)" />
          <rect x="42" y="90" width="4" height="24" rx="2" fill="#38bdf8" opacity="0.9" />

          {/* Right Earphone / Antenna */}
          <rect x="150" y="85" width="14" height="34" rx="7" fill="url(#earGrad)" />
          <rect x="154" y="90" width="4" height="24" rx="2" fill="#38bdf8" opacity="0.9" />

          {/* Robot Head Body */}
          <rect 
            x="46" 
            y="60" 
            width="108" 
            height="88" 
            rx="40" 
            fill="url(#robotHeadGrad)" 
            stroke="#60a5fa" 
            strokeWidth="1.5"
            strokeOpacity="0.6"
          />

          {/* Head Highlight Rim on Top */}
          <path 
            d="M 68 64 Q 100 60 132 64" 
            stroke="#bae6fd" 
            strokeWidth="2.5" 
            strokeLinecap="round" 
            fill="none" 
            opacity="0.5" 
          />

          {/* Visor / Face Area */}
          <rect 
            x="56" 
            y="74" 
            width="88" 
            height="62" 
            rx="24" 
            fill="url(#visorGrad)" 
            stroke="#1d4ed8" 
            strokeWidth="1"
          />

          {/* Robot Eyes: Cute Curved Arched Glowing Visor Eyes (as in screenshot) */}
          {/* Left Eye: Curved upside-down U arch */}
          <path 
            d="M 72 108 Q 80 92 88 108" 
            stroke="#38bdf8" 
            strokeWidth="5" 
            strokeLinecap="round" 
            fill="none"
            filter="url(#eyeGlow)"
          />
          {/* Right Eye: Curved upside-down U arch */}
          <path 
            d="M 112 108 Q 120 92 128 108" 
            stroke="#38bdf8" 
            strokeWidth="5" 
            strokeLinecap="round" 
            fill="none"
            filter="url(#eyeGlow)"
          />

          {/* Subtle blush/glow dots under eyes */}
          <ellipse cx="70" cy="116" rx="4" ry="2" fill="#38bdf8" opacity="0.25" />
          <ellipse cx="130" cy="116" rx="4" ry="2" fill="#38bdf8" opacity="0.25" />

          {/* Visor Glare subtle reflection */}
          <path 
            d="M 66 78 Q 98 75 130 80" 
            stroke="white" 
            strokeWidth="1.5" 
            strokeLinecap="round" 
            fill="none" 
            opacity="0.15" 
          />
        </svg>
      </div>

      {/* Robot Status Text */}
      <h3 className="mt-3 text-lg font-bold text-white tracking-wide">
        NOVAX is ready!
      </h3>
      <p className="mt-1 text-xs text-slate-400 text-center max-w-sm">
        Attach your files or describe your task to get started.
      </p>
    </div>
  );
};
