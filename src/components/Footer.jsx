import React from 'react';
import { AlertCircle, ShieldAlert, Sparkles } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="mt-20 border-t border-slate-800/80 bg-slate-950/80 pt-10 pb-20 md:pb-10 px-4">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 mb-8 text-slate-400 text-xs">
        <div className="md:col-span-1 space-y-3">
          <div className="flex items-center gap-2">
            <span className="text-xl">🥗</span>
            <span className="text-base font-bold text-white">NutriScan</span>
          </div>
          <p className="text-slate-400 leading-relaxed">
            Your AI kitchen copilot for turning the ingredients you already have into personalized meals.
          </p>
          <div className="text-slate-500 font-mono text-[11px]">
            Scan it. Cook it. Understand it.
          </div>
        </div>

        <div className="md:col-span-3 bg-slate-900/50 p-4 rounded-2xl border border-slate-800/60 space-y-3">
          <div className="flex items-center gap-2 text-emerald-400 font-semibold text-xs">
            <ShieldAlert className="w-4 h-4" />
            <span>Important Product Disclaimers</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-[11px] text-slate-400">
            <div>
              <span className="font-medium text-slate-300">Ingredient Quantities:</span> Quantities detected from photos are estimates. Please confirm or adjust them for accurate nutrition calculations.
            </div>
            <div>
              <span className="font-medium text-slate-300">Nutrition Engine:</span> Nutrition values are estimates calculated per 100g database benchmarks and vary by brand, preparation, and portion size.
            </div>
            <div>
              <span className="font-medium text-slate-300">Vision Recognition:</span> AI identification may occasionally misidentify items. Always review detected ingredients before cooking.
            </div>
            <div>
              <span className="font-medium text-slate-300">Medical Advice:</span> NutriScan provides general food guidance and is NOT a substitute for professional medical or dietary diagnosis/treatment.
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto pt-6 border-t border-slate-900 flex flex-col sm:flex-row items-center justify-between text-[11px] text-slate-500 gap-4">
        <div>© 2026 NutriScan AI. Powered by Multimodal Vision AI & Failover Stack.</div>
        <div className="flex items-center gap-4">
          <span>8-Hour Hackathon Edition</span>
          <span>•</span>
          <span className="text-emerald-400">FastAPI + React + SQLite</span>
        </div>
      </div>
    </footer>
  );
}
