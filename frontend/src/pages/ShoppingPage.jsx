import React, { useState, useEffect } from 'react';
import { ShoppingBag, Plus, Trash2, CheckSquare, Square, RefreshCw } from 'lucide-react';
import { api } from '../services/api';

export default function ShoppingPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newItem, setNewItem] = useState('');
  const [newQty, setNewQty] = useState(1);
  const [newUnit, setNewUnit] = useState('g');

  const loadList = async () => {
    setLoading(true);
    try {
      const res = await api.getShoppingList();
      setItems(res || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadList();
  }, []);

  const handleTogglePurchased = async (item) => {
    const newStatus = !item.purchased;
    try {
      await api.updateShoppingItem(item.id, { purchased: newStatus });
      setItems(prev => prev.map(i => i.id === item.id ? { ...i, purchased: newStatus } : i));
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id) => {
    try {
      await api.deleteShoppingItem(id);
      setItems(prev => prev.filter(i => i.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddItem = async (e) => {
    e.preventDefault();
    if (!newItem.trim()) return;

    try {
      await api.addShoppingItem({
        ingredient: newItem.trim().toLowerCase(),
        quantity: newQty,
        unit: newUnit
      });
      setNewItem('');
      loadList();
    } catch (err) {
      console.error(err);
    }
  };

  const handleClearPurchased = async () => {
    const purchased = items.filter(i => i.purchased);
    for (const item of purchased) {
      await api.deleteShoppingItem(item.id);
    }
    loadList();
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20 mb-2">
            <ShoppingBag className="w-3.5 h-3.5" />
            <span>Missing Ingredients</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white">
            🛒 SHOPPING LIST
          </h1>
          <p className="text-slate-400 text-xs sm:text-sm mt-1">
            Keep track of missing spices and ingredients needed for your recipe plans.
          </p>
        </div>

        {items.some(i => i.purchased) && (
          <button
            onClick={handleClearPurchased}
            className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs border border-slate-700 shrink-0"
          >
            Clear Purchased Items
          </button>
        )}
      </div>

      {/* Manual Add Card */}
      <div className="glass-panel p-6 rounded-3xl space-y-4">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Plus className="w-4 h-4 text-emerald-400" />
          Add Item to Shopping List
        </h3>

        <form onSubmit={handleAddItem} className="flex gap-3">
          <input
            type="text"
            value={newItem}
            onChange={(e) => setNewItem(e.target.value)}
            placeholder="Item name (e.g. Cumin seeds, Coriander, Olive oil)..."
            className="flex-1 bg-slate-950 text-white placeholder-slate-500 text-xs px-4 py-3 rounded-xl border border-slate-800 focus:outline-none focus:border-emerald-500"
          />

          <input
            type="number"
            value={newQty}
            onChange={(e) => setNewQty(parseFloat(e.target.value) || 1)}
            className="w-20 bg-slate-950 text-white text-xs px-3 py-3 rounded-xl border border-slate-800 text-center font-mono"
          />

          <select
            value={newUnit}
            onChange={(e) => setNewUnit(e.target.value)}
            className="bg-slate-950 text-white text-xs px-3 py-3 rounded-xl border border-slate-800"
          >
            <option value="g">g</option>
            <option value="ml">ml</option>
            <option value="pcs">pcs</option>
            <option value="tsp">tsp</option>
            <option value="tbsp">tbsp</option>
          </select>

          <button
            type="submit"
            className="px-5 py-3 rounded-xl bg-emerald-500 text-slate-950 font-bold text-xs shrink-0"
          >
            Add Item
          </button>
        </form>
      </div>

      {/* List */}
      {loading ? (
        <div className="text-center py-12 text-slate-400 text-xs">Loading shopping list...</div>
      ) : items.length === 0 ? (
        <div className="glass-panel p-8 text-center rounded-3xl space-y-2">
          <p className="text-slate-400 text-sm">Your shopping list is empty!</p>
          <p className="text-slate-500 text-xs">Missing ingredients from recipe details will automatically appear here when added.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <div
              key={item.id}
              className={`glass-card p-4 rounded-2xl border flex items-center justify-between transition-all ${
                item.purchased ? 'bg-slate-950/40 border-slate-900 opacity-60' : 'border-slate-800'
              }`}
            >
              <div
                onClick={() => handleTogglePurchased(item)}
                className="flex items-center gap-3.5 cursor-pointer flex-1"
              >
                {item.purchased ? (
                  <CheckSquare className="w-5 h-5 text-emerald-400 shrink-0" />
                ) : (
                  <Square className="w-5 h-5 text-slate-500 shrink-0" />
                )}

                <span className={`text-sm font-bold capitalize ${item.purchased ? 'line-through text-slate-500' : 'text-white'}`}>
                  {item.ingredient}
                </span>

                <span className="text-xs font-mono text-slate-400 font-semibold">
                  ({item.quantity} {item.unit})
                </span>
              </div>

              <button
                onClick={() => handleDelete(item.id)}
                className="p-1.5 text-slate-500 hover:text-rose-400 rounded-lg"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
