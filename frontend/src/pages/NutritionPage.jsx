import React, { useState, useEffect } from 'react';
import { PieChart as PieIcon, Plus, Flame, Clock, Calendar, CheckCircle2, AlertCircle } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';
import { api } from '../services/api';

export default function NutritionPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showLogModal, setShowLogModal] = useState(false);

  const [mealName, setMealName] = useState('');
  const [mealType, setMealType] = useState('Lunch');
  const [calories, setCalories] = useState(450);
  const [protein, setProtein] = useState(25);
  const [carbs, setCarbs] = useState(45);
  const [fat, setFat] = useState(15);
  const [fiber, setFiber] = useState(5);

  const loadTodayNutrition = async () => {
    setLoading(true);
    try {
      const res = await api.getTodayNutrition();
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTodayNutrition();
  }, []);

  const handleLogMealSubmit = async (e) => {
    e.preventDefault();
    if (!mealName.trim()) return;

    try {
      await api.logMeal({
        meal_name: mealName.trim(),
        meal_type: mealType,
        servings: 1.0,
        calories: parseFloat(calories) || 0,
        protein: parseFloat(protein) || 0,
        carbs: parseFloat(carbs) || 0,
        fat: parseFloat(fat) || 0,
        fiber: parseFloat(fiber) || 0
      });
      setShowLogModal(false);
      setMealName('');
      loadTodayNutrition();
    } catch (err) {
      console.error(err);
    }
  };

  if (loading || !data) {
    return <div className="text-center py-20 text-slate-400 text-xs">Loading today's nutrition dashboard...</div>;
  }

  const chartData = [
    { name: 'Protein', current: data.totals.protein, target: data.targets.protein, fill: '#10b981' },
    { name: 'Carbs', current: data.totals.carbs, target: data.targets.carbs, fill: '#06b6d4' },
    { name: 'Fat', current: data.totals.fat, target: data.targets.fat, fill: '#f59e0b' },
    { name: 'Fiber', current: data.totals.fiber, target: data.targets.fiber, fill: '#8b5cf6' },
  ];

  return (
    <div className="max-w-5xl mx-auto py-8 px-4 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20 mb-2">
            <PieIcon className="w-3.5 h-3.5" />
            <span>Daily Tracker</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white">
            Today's Nutrition
          </h1>
          <p className="text-slate-400 text-xs sm:text-sm mt-1">
            Summary of logged meals and estimated macronutrient intake.
          </p>
        </div>

        <button
          onClick={() => setShowLogModal(true)}
          className="px-5 py-3 rounded-2xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-extrabold text-xs shadow-lg shadow-emerald-500/20 flex items-center justify-center gap-2 shrink-0"
        >
          <Plus className="w-4 h-4" />
          <span>Log Custom Meal</span>
        </button>
      </div>

      {/* Primary Macro Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-4 text-center">
        <div className="glass-card p-4 rounded-2xl border border-slate-800 col-span-2 sm:col-span-1">
          <div className="text-xs text-slate-400 font-medium">Calories</div>
          <div className="text-2xl font-black text-white mt-1">{data.totals.calories}</div>
          <div className="text-[10px] text-slate-500 mt-1">/ {data.targets.calories} kcal</div>
          <div className="w-full bg-slate-950 h-1.5 rounded-full mt-2 overflow-hidden">
            <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${data.progress.calories_pct}%` }}></div>
          </div>
        </div>

        <div className="glass-card p-4 rounded-2xl border border-slate-800">
          <div className="text-xs text-slate-400 font-medium">Protein</div>
          <div className="text-2xl font-black text-emerald-400 mt-1">{data.totals.protein}g</div>
          <div className="text-[10px] text-slate-500 mt-1">/ {data.targets.protein}g</div>
          <div className="w-full bg-slate-950 h-1.5 rounded-full mt-2 overflow-hidden">
            <div className="bg-emerald-400 h-full rounded-full" style={{ width: `${data.progress.protein_pct}%` }}></div>
          </div>
        </div>

        <div className="glass-card p-4 rounded-2xl border border-slate-800">
          <div className="text-xs text-slate-400 font-medium">Carbs</div>
          <div className="text-2xl font-black text-cyan-400 mt-1">{data.totals.carbs}g</div>
          <div className="text-[10px] text-slate-500 mt-1">/ {data.targets.carbs}g</div>
          <div className="w-full bg-slate-950 h-1.5 rounded-full mt-2 overflow-hidden">
            <div className="bg-cyan-400 h-full rounded-full" style={{ width: `${data.progress.carbs_pct}%` }}></div>
          </div>
        </div>

        <div className="glass-card p-4 rounded-2xl border border-slate-800">
          <div className="text-xs text-slate-400 font-medium">Fat</div>
          <div className="text-2xl font-black text-amber-400 mt-1">{data.totals.fat}g</div>
          <div className="text-[10px] text-slate-500 mt-1">/ {data.targets.fat}g</div>
          <div className="w-full bg-slate-950 h-1.5 rounded-full mt-2 overflow-hidden">
            <div className="bg-amber-400 h-full rounded-full" style={{ width: `${data.progress.fat_pct}%` }}></div>
          </div>
        </div>

        <div className="glass-card p-4 rounded-2xl border border-slate-800">
          <div className="text-xs text-slate-400 font-medium">Fiber</div>
          <div className="text-2xl font-black text-violet-400 mt-1">{data.totals.fiber}g</div>
          <div className="text-[10px] text-slate-500 mt-1">/ {data.targets.fiber}g</div>
          <div className="w-full bg-slate-950 h-1.5 rounded-full mt-2 overflow-hidden">
            <div className="bg-violet-400 h-full rounded-full" style={{ width: `${data.progress.fiber_pct}%` }}></div>
          </div>
        </div>
      </div>

      {/* Chart Section */}
      <div className="glass-panel p-6 rounded-3xl space-y-4">
        <h3 className="text-base font-bold text-white">Macronutrient Intake vs Benchmark</h3>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }} />
              <Bar dataKey="current" radius={[8, 8, 0, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Today's Logged Meals Timeline */}
      <div className="glass-panel p-6 rounded-3xl space-y-4">
        <h3 className="text-base font-bold text-white">Logged Meals Timeline</h3>
        {data.logged_meals.length === 0 ? (
          <p className="text-slate-400 text-xs italic py-4">No meals logged today yet. Cook a recipe or log a custom meal above!</p>
        ) : (
          <div className="space-y-3">
            {data.logged_meals.map((m) => (
              <div key={m.id} className="bg-slate-950 p-4 rounded-2xl border border-slate-800 flex items-center justify-between text-xs">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-white text-sm">{m.meal_name}</span>
                    <span className="px-2 py-0.5 rounded-md bg-slate-800 text-slate-400 text-[10px]">{m.meal_type}</span>
                  </div>
                  <div className="text-slate-400 text-[11px] font-mono">
                    {m.calories} kcal • {m.protein}g P • {m.carbs}g C • {m.fat}g F • {m.fiber}g Fib
                  </div>
                </div>
                <div className="text-slate-500 font-mono text-[11px]">{m.time}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Manual Meal Modal */}
      {showLogModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 max-w-md w-full space-y-4 shadow-2xl">
            <h3 className="text-lg font-bold text-white">Log Meal</h3>

            <form onSubmit={handleLogMealSubmit} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 font-medium mb-1">Meal / Dish Name</label>
                <input
                  type="text"
                  value={mealName}
                  onChange={(e) => setMealName(e.target.value)}
                  placeholder="e.g. Oatmeal with Banana"
                  className="w-full bg-slate-950 text-white px-3 py-2.5 rounded-xl border border-slate-800 focus:outline-none focus:border-emerald-500"
                  required
                />
              </div>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Meal Category</label>
                <select
                  value={mealType}
                  onChange={(e) => setMealType(e.target.value)}
                  className="w-full bg-slate-950 text-white px-3 py-2.5 rounded-xl border border-slate-800"
                >
                  <option value="Breakfast">Breakfast</option>
                  <option value="Lunch">Lunch</option>
                  <option value="Snack">Snack</option>
                  <option value="Dinner">Dinner</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Calories (kcal)</label>
                  <input
                    type="number"
                    value={calories}
                    onChange={(e) => setCalories(e.target.value)}
                    className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Protein (g)</label>
                  <input
                    type="number"
                    value={protein}
                    onChange={(e) => setProtein(e.target.value)}
                    className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Carbs (g)</label>
                  <input
                    type="number"
                    value={carbs}
                    onChange={(e) => setCarbs(e.target.value)}
                    className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Fat (g)</label>
                  <input
                    type="number"
                    value={fat}
                    onChange={(e) => setFat(e.target.value)}
                    className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowLogModal(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 font-semibold rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-emerald-500 text-slate-950 font-bold rounded-xl"
                >
                  Save Log
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
