import React from 'react';
import { Camera, Refrigerator, UtensilsCrossed, PieChart, ShoppingBag, Sparkles, Home } from 'lucide-react';


export default function Navbar({ currentPage, setCurrentPage, onOpenAssistant }) {
  const navItems = [
    { id: 'home', label: 'Home', icon: Home, emoji: '🏠' },
    { id: 'scan', label: 'Scan', icon: Camera, highlight: true, emoji: '📸' },
    { id: 'recipes', label: 'Recipes', icon: UtensilsCrossed, emoji: '🍳' },
    { id: 'pantry', label: 'Pantry', icon: Refrigerator, emoji: '🧺' },
    { id: 'nutrition', label: 'Nutrition', icon: PieChart, emoji: '📊' },
    { id: 'shopping', label: 'Shopping', icon: ShoppingBag, emoji: '🛒' },
    { id: 'scan-meal', label: 'Meal Scan', icon: Sparkles, emoji: '✨' },
  ];

  return (
    <>
      {/* Desktop Header */}
      <header className="sticky top-0 z-40 glass-panel border-b border-gray-800/80 px-4 lg:px-8 py-3">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div 
            onClick={() => setCurrentPage('home')}
            className="flex items-center gap-2.5 cursor-pointer group"
          >
            <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-emerald-400 via-teal-400 to-cyan-400 p-0.5 flex items-center justify-center shadow-lg shadow-emerald-500/25 group-hover:scale-110 group-hover:rotate-6 transition-all duration-300">
              <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center">
                <span className="text-2xl cute-float">🥗</span>
              </div>
            </div>
            <div>
              <span className="text-xl font-black bg-gradient-to-r from-white via-slate-100 to-emerald-400 bg-clip-text text-transparent tracking-tight">
                NutriScan
              </span>
              <span className="hidden sm:inline-block ml-2 text-[11px] text-emerald-300 font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/15 border border-emerald-400/30 badge-pulse">
                ✨ AI Copilot
              </span>
            </div>
          </div>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center gap-1.5 bg-slate-900/80 p-1.5 rounded-2xl border border-slate-800/80 shadow-inner">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = currentPage === item.id;
              if (item.highlight) {
                return (
                  <button
                    key={item.id}
                    onClick={() => setCurrentPage(item.id)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-extrabold transition-all hover:scale-105 ${
                      active
                        ? 'bg-gradient-to-r from-emerald-400 to-teal-400 text-slate-950 shadow-md shadow-emerald-500/35'
                        : 'bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30 border border-emerald-400/40'
                    }`}
                  >
                    <span className="text-sm">{item.emoji}</span>
                    <span>{item.label}</span>
                  </button>
                );
              }
              return (
                <button
                  key={item.id}
                  onClick={() => setCurrentPage(item.id)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-bold transition-all hover:scale-105 ${
                    active
                      ? 'bg-slate-800 text-white shadow-sm border border-slate-700'
                      : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Assistant Trigger Button */}
          <div className="flex items-center gap-2">
            <button
              onClick={onOpenAssistant}
              className="flex items-center gap-2 px-3.5 py-2 rounded-2xl bg-gradient-to-r from-emerald-500/10 to-teal-500/10 hover:from-emerald-500/20 hover:to-teal-500/20 text-emerald-300 text-xs font-bold border border-emerald-500/30 transition-all hover:scale-105 shadow-sm"
            >
              <span className="text-sm cute-float">🤖</span>
              <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
              <span className="hidden sm:inline">Ask AI Chef</span>
            </button>
          </div>
        </div>
      </header>

      {/* Mobile Bottom Navigation Bar */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 z-40 glass-panel border-t border-slate-800/80 px-2 py-2 flex items-center justify-around">
        {navItems.slice(0, 5).map((item) => {
          const Icon = item.icon;
          const active = currentPage === item.id;
          if (item.highlight) {
            return (
              <button
                key={item.id}
                onClick={() => setCurrentPage(item.id)}
                className="flex flex-col items-center justify-center -mt-5"
              >
                <div className={`w-12 h-12 rounded-2xl flex items-center justify-center shadow-lg transition-transform border ${
                  active 
                    ? 'bg-gradient-to-tr from-emerald-400 to-teal-400 text-slate-950 scale-110 shadow-emerald-500/50 border-white/20' 
                    : 'bg-emerald-500 text-slate-950 shadow-emerald-500/30 border-emerald-400/40'
                }`}>
                  <span className="text-xl">{item.emoji}</span>
                </div>
                <span className="text-[10px] font-bold mt-1 text-emerald-400">{item.label}</span>
              </button>
            );
          }
          return (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              className={`flex flex-col items-center justify-center py-1 px-2 rounded-xl transition-all ${
                active ? 'text-emerald-400 scale-105 font-bold' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <span className="text-sm">{item.emoji}</span>
              <span className="text-[10px] font-medium mt-0.5">{item.label}</span>
            </button>
          );
        })}
      </div>
    </>
  );
}
