import React, { useState } from 'react';
import { Plus, Trash2, ArrowRight, Sparkles, Scale } from 'lucide-react';
import QuantityControlBar from '../components/QuantityControlBar';


export default function DetectedPage({ ingredients, setIngredients, setCurrentPage }) {
  const [newIngredient, setNewIngredient] = useState('');
  const [newQty, setNewQty] = useState(200);
  const [newUnit, setNewUnit] = useState('g');
  const [activeEditIndex, setActiveEditIndex] = useState(null);

  const getIconForIngredient = (name) => {
    const n = name.toLowerCase();
    if (n.includes('paneer') || n.includes('cheese')) return '🧀';
    if (n.includes('potato')) return '🥔';
    if (n.includes('tomato')) return '🍅';
    if (n.includes('onion')) return '🧅';
    if (n.includes('capsicum') || n.includes('pepper')) return '🫑';
    if (n.includes('rice')) return '🍚';
    if (n.includes('chicken')) return '🍗';
    if (n.includes('egg')) return '🥚';
    if (n.includes('milk')) return '🥛';
    if (n.includes('bread')) return '🍞';
    if (n.includes('spinach')) return '🥬';
    if (n.includes('carrot')) return '🥕';
    if (n.includes('chickpea')) return '🧆';
    if (n.includes('lentil') || n.includes('dal')) return '🍲';
    if (n.includes('oil')) return '🛢️';
    if (n.includes('butter')) return '🧈';
    if (n.includes('curd')) return '🥣';
    return '🥗';
  };

  const handleSetExactQty = (index, val) => {
    setIngredients(prev => prev.map((item, i) => {
      if (i === index) {
        return { ...item, estimated_quantity: val, quantity: val };
      }
      return item;
    }));
  };

  const handleUpdateUnit = (index, unit) => {
    setIngredients(prev => prev.map((item, i) => {
      if (i === index) {
        return { ...item, unit };
      }
      return item;
    }));
  };

  const handleDelete = (index) => {
    setIngredients(prev => prev.filter((_, i) => i !== index));
  };

  const handleAddManual = (e) => {
    e.preventDefault();
    if (!newIngredient.trim()) return;

    const item = {
      name: newIngredient.trim().toLowerCase(),
      estimated_quantity: newQty,
      unit: newUnit,
      confidence: 1.0
    };

    setIngredients(prev => [...prev, item]);
    setNewIngredient('');
  };

  const floatValue = (val) => {
    const parsed = parseFloat(val);
    return isNaN(parsed) ? 100 : parsed;
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 space-y-8 page-enter">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20 mb-2 badge-pulse">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Multimodal Vision Results</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
            Detected Ingredients
          </h1>
          <p className="text-slate-400 text-xs sm:text-sm mt-1">
            Review estimated quantities below and use the quantity adjustment bar to set exact amounts.
          </p>
        </div>

        <button
          onClick={() => setCurrentPage('recipes')}
          disabled={ingredients.length === 0}
          className="px-6 py-3.5 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-extrabold text-sm shadow-xl shadow-emerald-500/25 hover:scale-105 transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
        >
          <span>🍳 Find Matching Recipes</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Interactive Guidance Banner */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 flex items-start gap-3 text-xs text-slate-300 shadow-md">
        <Scale className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-white">Smart Quantity Adjustment:</span> Drag the slider bar or tap quick preset chips to instantly update weight/volume for maximum recipe accuracy.
        </div>
      </div>

      {/* Detected Ingredients Grid */}
      {ingredients.length === 0 ? (
        <div className="glass-panel p-8 text-center rounded-3xl space-y-3">
          <p className="text-slate-400 text-sm">No ingredients listed yet.</p>
          <button
            onClick={() => setCurrentPage('scan')}
            className="px-4 py-2 bg-slate-800 text-emerald-400 text-xs font-semibold rounded-xl border border-slate-700 hover:bg-slate-700 transition-colors"
          >
            ← Back to Vision Scan
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {ingredients.map((item, idx) => {
            const qty = floatValue(item.estimated_quantity || item.quantity || 100);
            const confPct = Math.round((item.confidence || 0.90) * 100);
            const icon = getIconForIngredient(item.name || item.ingredient || '');

            return (
              <div
                key={idx}
                className="glass-card p-5 rounded-2xl space-y-3 border border-slate-800/80 hover:border-emerald-500/40 hover-glow transition-all"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-2xl bg-slate-800/90 border border-slate-700 flex items-center justify-center text-2xl shadow-inner shrink-0">
                      {icon}
                    </div>

                    <div className="space-y-0.5">
                      <h3 className="font-bold text-white text-base capitalize">
                        {item.name || item.ingredient}
                      </h3>
                      <div className="flex items-center gap-2 text-[11px] text-slate-400">
                        <span className="text-emerald-400 font-semibold">{confPct}% confidence</span>
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={() => handleDelete(idx)}
                    className="p-2 text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 rounded-xl transition-colors"
                    title="Remove ingredient"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                {/* Interactive Quantity Control Bar */}
                <QuantityControlBar
                  quantity={qty}
                  unit={item.unit || 'g'}
                  onQuantityChange={(val) => handleSetExactQty(idx, val)}
                  onUnitChange={(u) => handleUpdateUnit(idx, u)}
                  showSlider={true}
                  showPresets={true}
                  compact={false}
                />
              </div>
            );
          })}
        </div>
      )}

      {/* Add Additional Ingredient Card with Live Quantity Control */}
      <div className="glass-panel p-6 rounded-3xl space-y-4 border border-slate-800">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Plus className="w-4 h-4 text-emerald-400" />
          Add More Ingredients
        </h3>

        <form onSubmit={handleAddManual} className="space-y-4">
          <div className="flex flex-wrap sm:flex-nowrap gap-3">
            <input
              type="text"
              value={newIngredient}
              onChange={(e) => setNewIngredient(e.target.value)}
              placeholder="Ingredient name (e.g. Garlic, Coriander, Salt)..."
              className="flex-1 bg-slate-950 text-white placeholder-slate-500 text-xs px-4 py-3 rounded-xl border border-slate-800 focus:outline-none focus:border-emerald-500 min-w-[200px]"
            />

            <button
              type="submit"
              disabled={!newIngredient.trim()}
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-bold text-xs shadow-lg shadow-emerald-500/20 disabled:opacity-40 disabled:cursor-not-allowed hover:scale-105 transition-all shrink-0"
            >
              + Add Ingredient
            </button>
          </div>

          <QuantityControlBar
            quantity={newQty}
            unit={newUnit}
            onQuantityChange={(val) => setNewQty(val)}
            onUnitChange={(u) => setNewUnit(u)}
            showSlider={true}
            showPresets={true}
          />
        </form>
      </div>

      {/* Bottom Floating CTA */}
      {ingredients.length > 0 && (
        <div className="pt-4 flex justify-end">
          <button
            onClick={() => setCurrentPage('recipes')}
            className="w-full sm:w-auto px-8 py-4 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-extrabold text-base shadow-xl shadow-emerald-500/30 hover:scale-105 transition-all flex items-center justify-center gap-3"
          >
            <span>🍳 Find Recipes ({ingredients.length} ingredients ready)</span>
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      )}
    </div>
  );
}
