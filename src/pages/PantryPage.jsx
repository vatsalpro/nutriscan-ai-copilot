import React, { useState, useEffect } from 'react';
import { Plus, Trash2, Refrigerator, RefreshCw, ArrowRight, AlertCircle, Edit3 } from 'lucide-react';
import { api } from '../services/api';
import QuantityControlBar from '../components/QuantityControlBar';

export default function PantryPage({ setCurrentPage, setIngredients }) {
  const [pantry, setPantry] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newItem, setNewItem] = useState('');
  const [newQty, setNewQty] = useState(200);
  const [newUnit, setNewUnit] = useState('g');
  const [newFreshness, setNewFreshness] = useState('Fresh');

  const loadPantry = async () => {
    setLoading(true);
    try {
      const data = await api.getPantry();
      setPantry(data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPantry();
  }, []);

  const handleAddPantry = async (e) => {
    e.preventDefault();
    if (!newItem.trim()) return;

    try {
      await api.addPantryItem({
        ingredient: newItem.trim().toLowerCase(),
        quantity: newQty,
        unit: newUnit,
        freshness: newFreshness
      });
      setNewItem('');
      loadPantry();
    } catch (err) {
      console.error(err);
    }
  };

  const handleSetExactQty = async (item, updatedQty) => {
    try {
      await api.updatePantryItem(item.id, { quantity: updatedQty });
      setPantry(prev => prev.map(p => p.id === item.id ? { ...p, quantity: updatedQty } : p));
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpdateUnit = async (item, unit) => {
    try {
      await api.updatePantryItem(item.id, { unit });
      setPantry(prev => prev.map(p => p.id === item.id ? { ...p, unit } : p));
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpdateFreshness = async (id, freshness) => {
    try {
      await api.updatePantryItem(id, { freshness });
      setPantry(prev => prev.map(p => p.id === id ? { ...p, freshness } : p));
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id) => {
    try {
      await api.deletePantryItem(id);
      setPantry(prev => prev.filter(p => p.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  const handleCookFromPantry = () => {
    // Convert pantry items into user ingredient format for matching
    const converted = pantry.map(p => ({
      name: p.ingredient,
      estimated_quantity: p.quantity,
      unit: p.unit,
      confidence: 1.0
    }));
    setIngredients(converted);
    setCurrentPage('recipes');
  };

  const expiringItems = pantry.filter(p => p.freshness === 'Use Soon' || p.freshness === 'Expiring Soon');

  return (
    <div className="max-w-5xl mx-auto py-8 px-4 space-y-8 page-enter">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20 mb-2 badge-pulse">
            <Refrigerator className="w-3.5 h-3.5" />
            <span>Smart Kitchen Inventory</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            My Pantry
          </h1>
          <p className="text-slate-400 text-xs sm:text-sm mt-1">
            Manage your kitchen inventory and adjust item quantities with visual slider bars.
          </p>
        </div>

        <button
          onClick={handleCookFromPantry}
          disabled={pantry.length === 0}
          className="px-6 py-3.5 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-extrabold text-sm shadow-xl shadow-emerald-500/25 hover:scale-105 transition-all flex items-center justify-center gap-2 shrink-0 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span>🍳 What Can I Cook?</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Food Waste Feature Alert */}
      {expiringItems.length > 0 && (
        <div className="bg-emerald-950/40 border border-emerald-500/30 rounded-2xl p-4 flex items-start gap-3 text-xs text-emerald-200 shadow-md">
          <RefreshCw className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold text-white">♻️ Reduce Food Waste:</span> You have <strong className="text-emerald-300">{expiringItems.length} items</strong> marked "Use Soon" ({expiringItems.map(i => i.ingredient).join(', ')}). Recipe matching will prioritize recipes using them!
          </div>
        </div>
      )}

      {/* Add Item Card */}
      <div className="glass-panel p-6 rounded-3xl space-y-4 border border-slate-800">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Plus className="w-4 h-4 text-emerald-400" />
          Add Pantry Ingredient
        </h3>

        <form onSubmit={handleAddPantry} className="space-y-4">
          <div className="flex flex-wrap sm:flex-nowrap gap-3">
            <input
              type="text"
              value={newItem}
              onChange={(e) => setNewItem(e.target.value)}
              placeholder="Ingredient (e.g. Potato, Rice, Milk, Paneer)..."
              className="flex-1 bg-slate-950 text-white placeholder-slate-500 text-xs px-4 py-3 rounded-xl border border-slate-800 focus:outline-none focus:border-emerald-500 min-w-[180px]"
            />

            <select
              value={newFreshness}
              onChange={(e) => setNewFreshness(e.target.value)}
              className="bg-slate-950 text-white text-xs px-3 py-3 rounded-xl border border-slate-800"
            >
              <option value="Fresh">Fresh</option>
              <option value="Use Soon">Use Soon ♻️</option>
              <option value="Expiring Soon">Expiring Soon ⚠️</option>
            </select>

            <button
              type="submit"
              disabled={!newItem.trim()}
              className="px-6 py-3 rounded-xl bg-emerald-500 text-slate-950 font-bold text-xs shadow-lg shadow-emerald-500/20 disabled:opacity-40 disabled:cursor-not-allowed hover:scale-105 transition-all shrink-0"
            >
              + Add to Pantry
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

      {/* Pantry Items List */}
      {loading ? (
        <div className="text-center py-12 text-slate-400 text-xs">Loading pantry items...</div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {pantry.map((item) => (
            <div key={item.id} className="glass-card p-5 rounded-2xl border border-slate-800/80 hover:border-emerald-500/40 hover-glow transition-all space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">{item.icon || '🥗'}</span>
                  <div>
                    <h3 className="font-bold text-white text-base capitalize">{item.ingredient}</h3>
                    <div className="text-xs font-mono text-emerald-400 font-semibold">{item.quantity} {item.unit}</div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <select
                    value={item.freshness}
                    onChange={(e) => handleUpdateFreshness(item.id, e.target.value)}
                    className={`text-[10px] font-semibold px-2 py-1 rounded-lg border focus:outline-none ${
                      item.freshness === 'Fresh'
                        ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
                        : item.freshness === 'Use Soon'
                        ? 'bg-amber-500/10 text-amber-300 border-amber-500/30'
                        : 'bg-rose-500/10 text-rose-300 border-rose-500/30'
                    }`}
                  >
                    <option value="Fresh" className="bg-slate-900 text-emerald-400">Fresh</option>
                    <option value="Use Soon" className="bg-slate-900 text-amber-400">Use Soon</option>
                    <option value="Expiring Soon" className="bg-slate-900 text-rose-400">Expiring Soon</option>
                  </select>

                  <button
                    onClick={() => handleDelete(item.id)}
                    className="p-1.5 text-slate-500 hover:text-rose-400 rounded-lg hover:bg-rose-500/10 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Interactive Quantity Control Bar */}
              <QuantityControlBar
                quantity={item.quantity}
                unit={item.unit || 'g'}
                onQuantityChange={(val) => handleSetExactQty(item, val)}
                onUnitChange={(u) => handleUpdateUnit(item, u)}
                showSlider={true}
                showPresets={true}
                compact={true}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
