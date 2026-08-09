import React from 'react';
import { Minus, Plus } from 'lucide-react';

export default function QuantityControlBar({
  quantity,
  unit = 'g',
  onQuantityChange,
  onUnitChange,
  max = 1000,
  min = 1,
  showSlider = true,
  showPresets = true,
  compact = false
}) {
  const isCount = unit === 'pcs' || unit === 'cloves' || unit === 'eggs' || unit === 'slice' || unit === 'tsp' || unit === 'tbsp';
  const sliderMax = isCount ? 20 : (unit === 'kg' || unit === 'l' ? 5 : 1000);
  const step = isCount ? 1 : (unit === 'kg' || unit === 'l' ? 0.1 : 25);

  const presets = isCount
    ? [1, 2, 4, 6, 12]
    : unit === 'kg' || unit === 'l'
    ? [0.25, 0.5, 1, 2, 5]
    : [50, 100, 250, 500, 1000];

  const handleStep = (delta) => {
    const nextVal = Math.max(min, Math.round((quantity + delta * step) * 100) / 100);
    onQuantityChange(nextVal);
  };

  const handleSliderChange = (e) => {
    onQuantityChange(parseFloat(e.target.value));
  };

  const fillPercentage = Math.min(100, Math.max(5, (quantity / sliderMax) * 100));

  return (
    <div className={`space-y-2.5 ${compact ? 'py-1' : 'py-2.5 px-3.5 bg-slate-950/70 rounded-2xl border border-slate-800/80 shadow-inner'}`}>
      {/* Upper Control Strip: Stepper & Display */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-1.5 bg-slate-900 p-1 rounded-xl border border-slate-800 shadow-sm">
          <button
            type="button"
            onClick={() => handleStep(-1)}
            className="w-8 h-8 rounded-lg bg-slate-800 hover:bg-emerald-500/20 hover:text-emerald-400 text-white font-extrabold text-sm flex items-center justify-center transition-all hover:scale-105 active:scale-95 shadow"
          >
            <Minus className="w-3.5 h-3.5" />
          </button>

          <div className="min-w-[70px] text-center px-2">
            <span className="text-sm font-extrabold text-white font-mono tracking-tight">
              {quantity}
            </span>
            <span className="text-xs text-emerald-400 font-bold ml-1">{unit}</span>
          </div>

          <button
            type="button"
            onClick={() => handleStep(1)}
            className="w-8 h-8 rounded-lg bg-slate-800 hover:bg-emerald-500/20 hover:text-emerald-400 text-white font-extrabold text-sm flex items-center justify-center transition-all hover:scale-105 active:scale-95 shadow"
          >
            <Plus className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Unit Selector Pills if onUnitChange is provided */}
        {onUnitChange && (
          <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-xl border border-slate-800">
            {['g', 'ml', 'pcs', 'kg'].map((u) => (
              <button
                key={u}
                type="button"
                onClick={() => onUnitChange(u)}
                className={`px-2 py-1 rounded-lg text-[11px] font-bold transition-all ${
                  unit === u
                    ? 'bg-emerald-500 text-slate-950 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                {u}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Visual Fill Gauge & Range Slider */}
      {showSlider && (
        <div className="space-y-1">
          <div className="relative w-full h-2 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
            <div
              className="h-full bg-gradient-to-r from-emerald-500 via-teal-400 to-cyan-400 rounded-full transition-all duration-300 shadow-sm shadow-emerald-500/50"
              style={{ width: `${fillPercentage}%` }}
            />
          </div>

          <input
            type="range"
            min={min}
            max={sliderMax}
            step={step}
            value={quantity}
            onChange={handleSliderChange}
            className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-400 focus:outline-none"
          />
        </div>
      )}

      {/* Quick Presets Bar */}
      {showPresets && (
        <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-none pt-0.5">
          <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider mr-1 shrink-0">Presets:</span>
          {presets.map((preset) => (
            <button
              key={preset}
              type="button"
              onClick={() => onQuantityChange(preset)}
              className={`px-2 py-0.5 rounded-lg text-[11px] font-mono font-medium border transition-all shrink-0 ${
                quantity === preset
                  ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 font-bold'
                  : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-white hover:border-slate-700'
              }`}
            >
              {preset}{unit}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
