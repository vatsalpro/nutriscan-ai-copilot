import React from 'react';
import { Refrigerator, Utensils, BarChart3, PiggyBank, RefreshCw, ArrowRight } from 'lucide-react';
import InstagramCameraIcon from '../components/InstagramCameraIcon';


export default function HomePage({ setCurrentPage, onSelectDemoIngredients }) {
  const [highlightIndex, setHighlightIndex] = React.useState(0);

  React.useEffect(() => {
    const timer = setInterval(() => {
      setHighlightIndex((prev) => (prev + 1) % 3);
    }, 800);
    return () => clearInterval(timer);
  }, []);

  const featureCards = [
    {
      icon: Utensils,
      color: 'from-emerald-400 to-teal-400',
      emoji: '🍳',
      title: 'Discover Recipes',
      desc: 'Find delicious meals using ingredients already sitting in your kitchen.'
    },
    {
      icon: BarChart3,
      color: 'from-cyan-400 to-blue-400',
      emoji: '📊',
      title: 'Understand Nutrition',
      desc: 'See estimated calories, protein, carbs, fat & fiber calculated per serving.'
    },
    {
      icon: PiggyBank,
      color: 'from-amber-400 to-orange-400',
      emoji: '💰',
      title: 'Save Money',
      desc: 'Estimate meal cost and avoid buying extra unnecessary store items.'
    },
    {
      icon: RefreshCw,
      color: 'from-purple-400 to-pink-400',
      emoji: '♻️',
      title: 'Reduce Food Waste',
      desc: 'Prioritize ingredients that should be cooked and enjoyed soon.'
    }
  ];

  const handleQuickDemo = () => {
    const demoItems = [
      { name: 'paneer', estimated_quantity: 200, unit: 'g', confidence: 0.94 },
      { name: 'potato', estimated_quantity: 250, unit: 'g', confidence: 0.92 },
      { name: 'tomato', estimated_quantity: 150, unit: 'g', confidence: 0.91 },
      { name: 'onion', estimated_quantity: 100, unit: 'g', confidence: 0.89 },
      { name: 'capsicum', estimated_quantity: 80, unit: 'g', confidence: 0.87 }
    ];
    onSelectDemoIngredients(demoItems);
    setCurrentPage('detected');
  };

  return (
    <div className="space-y-16 py-6 px-4 max-w-7xl mx-auto page-enter">
      {/* Cute Floating Background Ambient Emojis */}
      <div className="absolute top-12 left-10 text-3xl opacity-20 cute-float pointer-events-none select-none">🥑</div>
      <div className="absolute top-24 right-12 text-3xl opacity-20 cute-float pointer-events-none select-none" style={{ animationDelay: '1s' }}>🍋</div>
      <div className="absolute top-72 left-1/4 text-2xl opacity-15 cute-float pointer-events-none select-none" style={{ animationDelay: '2s' }}>🍓</div>
      <div className="absolute top-96 right-1/4 text-3xl opacity-15 cute-float pointer-events-none select-none" style={{ animationDelay: '1.5s' }}>🫐</div>

      {/* Hero Section */}
      <section className="relative text-center space-y-8 pt-8 pb-12 overflow-hidden">
        {/* Glow backdrop */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[30rem] h-[30rem] bg-emerald-500/10 blur-[130px] rounded-full pointer-events-none"></div>

        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-slate-800/90 border border-emerald-400/30 text-emerald-300 text-xs font-bold badge-pulse shadow-md">
          <span className="text-sm">✨</span>
          <span>Multimodal Vision AI Powered</span>
        </div>

        {/* Animated Sequential Ultra-Fast 0.8s Highlight Tagline */}
        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-black tracking-tight text-white leading-tight flex flex-wrap items-center justify-center gap-2 sm:gap-4">
          <span
            className={`inline-block transition-all duration-150 px-3 py-1 rounded-2xl ${
              highlightIndex === 0
                ? 'bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-300 bg-clip-text text-transparent scale-110 drop-shadow-[0_0_25px_rgba(52,211,153,0.8)]'
                : 'text-slate-400 opacity-50 scale-95'
            }`}
          >
            Scan it.
          </span>
          <span
            className={`inline-block transition-all duration-150 px-3 py-1 rounded-2xl ${
              highlightIndex === 1
                ? 'bg-gradient-to-r from-cyan-400 via-sky-300 to-blue-400 bg-clip-text text-transparent scale-110 drop-shadow-[0_0_25px_rgba(56,189,248,0.8)]'
                : 'text-slate-400 opacity-50 scale-95'
            }`}
          >
            Cook it.
          </span>
          <span
            className={`inline-block transition-all duration-150 px-3 py-1 rounded-2xl ${
              highlightIndex === 2
                ? 'bg-gradient-to-r from-purple-400 via-pink-400 to-rose-400 bg-clip-text text-transparent scale-110 drop-shadow-[0_0_25px_rgba(236,72,153,0.8)]'
                : 'text-slate-400 opacity-50 scale-95'
            }`}
          >
            Understand it.
          </span>
        </h1>

        <p className="max-w-2xl mx-auto text-base sm:text-lg text-slate-300 font-medium leading-relaxed">
          Your cute & smart AI kitchen copilot for turning pantry ingredients into delicious, healthy meals! 🥗✨
        </p>

        {/* Primary Quote Box */}
        <div className="max-w-xl mx-auto bg-slate-900/90 border border-slate-800 p-4 rounded-3xl text-slate-300 text-sm italic shadow-2xl hover-glow transition-all">
          <p className="text-emerald-400 font-bold not-italic text-xs uppercase tracking-wider mb-1 flex items-center justify-center gap-1">
            <span>💡</span> Core Philosophy
          </p>
          "Most recipe apps ask what you want to eat. <span className="text-white font-bold not-italic">NutriScan asks what you already have!</span>"
        </div>

        {/* Hero CTA Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
          <button
            onClick={() => setCurrentPage('scan')}
            className="w-full sm:w-auto px-8 py-4 rounded-2xl bg-slate-800/90 hover:bg-slate-800 text-white font-black text-base border border-slate-700 hover:border-emerald-400/50 shadow-xl hover:scale-105 transition-all flex items-center justify-center gap-3 group"
          >
            <InstagramCameraIcon size="sm" />
            <span>Scan Ingredients</span>
          </button>

          <button
            onClick={() => setCurrentPage('pantry')}
            className="w-full sm:w-auto px-8 py-4 rounded-2xl bg-slate-800/90 hover:bg-slate-800 text-white font-bold text-base border border-slate-700 hover:border-emerald-500/40 transition-all flex items-center justify-center gap-3 hover:scale-105"
          >
            <Refrigerator className="w-5 h-5 text-emerald-400" />
            <span>🧺 Open Pantry</span>
          </button>
        </div>

        {/* One-Click Hackathon Demo Shortcut */}
        <div className="pt-4">
          <button
            onClick={handleQuickDemo}
            className="text-xs text-slate-400 hover:text-emerald-300 font-bold transition-colors inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-emerald-500/30 shadow"
          >
            <span>🚀 Instant Hackathon Demo Mode (Paneer, Potato, Tomato)</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </section>

      {/* Feature Cards Section */}
      <section className="space-y-8">
        <div className="text-center space-y-2">
          <h2 className="text-2xl sm:text-4xl font-extrabold text-white">
            What can NutriScan do? 🌟
          </h2>
          <p className="text-slate-400 text-sm max-w-lg mx-auto">
            From smart vision identification to guided cooking timers and nutrition insights.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {featureCards.map((card, idx) => {
            const Icon = card.icon;
            return (
              <div key={idx} className="glass-card p-6 rounded-3xl space-y-4 border border-slate-800/80 hover:border-emerald-400/40 hover-glow transition-all">
                <div className={`w-14 h-14 rounded-2xl bg-gradient-to-tr ${card.color} p-0.5 shadow-lg cute-icon-badge`}>
                  <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center text-2xl">
                    <span>{card.emoji}</span>
                  </div>
                </div>
                <h3 className="text-lg font-extrabold text-white">{card.title}</h3>
                <p className="text-slate-400 text-xs leading-relaxed">{card.desc}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Primary User Journey Walkthrough */}
      <section className="bg-slate-900/80 border border-slate-800/80 rounded-3xl p-6 sm:p-10 space-y-8 shadow-2xl">
        <div className="text-center space-y-2">
          <span className="text-xs font-extrabold uppercase tracking-wider text-emerald-400 badge-pulse">Step by Step</span>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white">How NutriScan Works 🪄</h2>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
          {[
            { step: '1. SCAN', label: 'Take/Upload Photo', icon: '📸' },
            { step: '2. DETECT', label: 'AI Identifies Food', icon: '🧠' },
            { step: '3. CONFIRM', label: 'Adjust Quantities', icon: '⚖️' },
            { step: '4. MATCH', label: 'Find Recipe Match', icon: '🍳' },
            { step: '5. IMPROVE', label: 'Enjoy Healthy Meal', icon: '✨' },
          ].map((item, i) => (
            <div key={i} className="bg-slate-950/80 p-5 rounded-2xl border border-slate-800 hover:border-emerald-500/40 space-y-2 transition-all hover:scale-105 shadow">
              <span className="text-3xl block cute-float" style={{ animationDelay: `${i * 0.3}s` }}>{item.icon}</span>
              <div className="text-xs font-black text-emerald-400">{item.step}</div>
              <div className="text-[11px] text-slate-300 font-bold">{item.label}</div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
