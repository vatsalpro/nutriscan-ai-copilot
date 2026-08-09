import React from 'react';

const DECORATIVE_ITEMS = [
  { emoji: '🥑', top: '7%', left: '3%', delay: '0s', size: 'text-3xl' },
  { emoji: '🍋', top: '12%', right: '4%', delay: '1.2s', size: 'text-3xl' },
  { emoji: '🍓', top: '26%', left: '6%', delay: '2.4s', size: 'text-2xl' },
  { emoji: '🫐', top: '33%', right: '8%', delay: '0.8s', size: 'text-3xl' },
  { emoji: '🍑', top: '46%', left: '4%', delay: '1.8s', size: 'text-3xl' },
  { emoji: '🥕', top: '53%', right: '5%', delay: '3.0s', size: 'text-2xl' },
  { emoji: '🍌', top: '66%', left: '7%', delay: '0.5s', size: 'text-3xl' },
  { emoji: '🍍', top: '74%', right: '4%', delay: '2.1s', size: 'text-3xl' },
  { emoji: '🍇', top: '84%', left: '5%', delay: '1.5s', size: 'text-2xl' },
  { emoji: '🥦', top: '91%', right: '6%', delay: '2.8s', size: 'text-3xl' },
  { emoji: '✨', top: '18%', left: '48%', delay: '1.0s', size: 'text-xl' },
  { emoji: '🌟', top: '62%', right: '42%', delay: '2.0s', size: 'text-xl' },
];

export default function BackgroundDecorations() {
  return (
    <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden select-none">
      {/* 4 Animated Glowing Pastel Mesh Orbs */}
      <div className="absolute -top-24 left-[10%] w-[32rem] h-[32rem] bg-emerald-500/18 blur-[100px] rounded-full animate-pulse pointer-events-none" />
      <div className="absolute top-[30%] right-[5%] w-[34rem] h-[34rem] bg-cyan-500/16 blur-[110px] rounded-full pointer-events-none cute-float" style={{ animationDuration: '14s' }} />
      <div className="absolute top-[60%] left-[8%] w-[36rem] h-[36rem] bg-purple-500/14 blur-[120px] rounded-full pointer-events-none cute-float" style={{ animationDuration: '16s' }} />
      <div className="absolute -bottom-20 right-[15%] w-[38rem] h-[38rem] bg-amber-500/14 blur-[110px] rounded-full pointer-events-none" />

      {/* Populated Floating Background Food & Sparkle Emojis */}
      {DECORATIVE_ITEMS.map((item, idx) => (
        <div
          key={idx}
          className={`absolute ${item.size} opacity-20 cute-float pointer-events-none`}
          style={{
            top: item.top,
            left: item.left,
            right: item.right,
            animationDelay: item.delay,
          }}
        >
          {item.emoji}
        </div>
      ))}
    </div>
  );
}
