import React, { useState, useEffect } from 'react';
import { Clock, Users, Flame, ChefHat, Sparkles, CheckCircle2, XCircle, ShoppingBag, ArrowLeft, RefreshCw, BarChart2, AlertCircle } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { api } from '../services/api';

export default function RecipeDetailPage({ recipeId, setCurrentPage, onStartCooking }) {
  const [recipe, setRecipe] = useState(null);
  const [servings, setServings] = useState(2);
  const [loading, setLoading] = useState(true);
  const [improvingMeal, setImprovingMeal] = useState(false);
  const [improvementResult, setImprovementResult] = useState(null);
  const [activeSubstitutions, setActiveSubstitutions] = useState({});
  const [addedToShopping, setAddedToShopping] = useState(false);

  const fetchRecipe = async (servingsCount) => {
    setLoading(true);
    try {
      const data = await api.getRecipeDetails(recipeId, servingsCount);
      setRecipe(data);
      if (data && data.servings) {
        setServings(data.servings);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (recipeId) {
      fetchRecipe(servings);
    }
  }, [recipeId]);

  const handleServingsChange = (delta) => {
    const newCount = Math.max(1, servings + delta);
    setServings(newCount);
    fetchRecipe(newCount);
  };

  const handleAddMissingToShopping = async () => {
    if (!recipe) return;
    const missing = recipe.ingredient_table.filter(item => !item.is_available);
    if (missing.length === 0) return;

    try {
      const batchItems = missing.map(item => ({
        ingredient: item.ingredient,
        quantity: item.required_quantity,
        unit: item.unit
      }));
      await api.addBatchShoppingItems(batchItems);
      setAddedToShopping(true);
      setTimeout(() => setAddedToShopping(false), 3000);
    } catch (err) {
      console.error(err);
    }
  };

  const handleImproveMeal = async () => {
    setImprovingMeal(true);
    try {
      const result = await api.improveMeal(recipeId, {
        servings: servings,
        reduce_oil: true,
        add_veggies: true,
        boost_protein: true,
        substitutions: activeSubstitutions
      });
      setImprovementResult(result);
    } catch (err) {
      console.error(err);
    } finally {
      setImprovingMeal(false);
    }
  };

  const handleSelectSubstitution = (fromIng, toIng) => {
    setActiveSubstitutions(prev => ({ ...prev, [fromIng.toLowerCase()]: toIng.toLowerCase() }));
  };

  if (loading || !recipe) {
    return (
      <div className="max-w-4xl mx-auto py-16 px-4 text-center space-y-4">
        <div className="w-12 h-12 rounded-full border-4 border-emerald-500/20 border-t-emerald-500 animate-spin mx-auto"></div>
        <p className="text-slate-400 text-sm">Loading recipe details...</p>
      </div>
    );
  }

  const macroData = [
    { name: 'Protein', value: recipe.per_serving_nutrition.protein, color: '#10b981' },
    { name: 'Carbs', value: recipe.per_serving_nutrition.carbs, color: '#06b6d4' },
    { name: 'Fat', value: recipe.per_serving_nutrition.fat, color: '#f59e0b' },
    { name: 'Fiber', value: recipe.per_serving_nutrition.fiber, color: '#8b5cf6' },
  ];

  return (
    <div className="max-w-5xl mx-auto py-6 px-4 space-y-8">
      {/* Top Back Navigation */}
      <button
        onClick={() => setCurrentPage('recipes')}
        className="inline-flex items-center gap-2 text-slate-400 hover:text-white text-xs font-semibold bg-slate-900 px-3 py-2 rounded-xl border border-slate-800 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Recipes</span>
      </button>

      {/* Hero Header Card */}
      <div className="relative rounded-3xl overflow-hidden glass-panel border border-slate-800">
        <div className="relative h-64 sm:h-80 w-full overflow-hidden">
          <img
            src={recipe.image_url}
            alt={recipe.name}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/60 to-transparent"></div>

          <div className="absolute bottom-6 left-6 right-6 space-y-3">
            <div className="flex flex-wrap gap-2">
              <span className="bg-emerald-500 text-slate-950 font-bold text-xs px-3 py-1 rounded-full">
                {recipe.match_percentage}% Ingredient Match
              </span>
              <span className="bg-slate-900/80 backdrop-blur-md text-white font-semibold text-xs px-3 py-1 rounded-full border border-slate-700">
                {recipe.difficulty}
              </span>
              <span className="bg-amber-500/20 text-amber-300 font-semibold text-xs px-3 py-1 rounded-full border border-amber-500/30">
                Est. ₹{recipe.estimated_cost} (~₹{recipe.cost_per_serving}/serving)
              </span>
            </div>

            <h1 className="text-3xl sm:text-4xl font-extrabold text-white">
              {recipe.name}
            </h1>
            <p className="text-slate-300 text-xs sm:text-sm max-w-2xl">
              {recipe.description}
            </p>
          </div>
        </div>

        {/* Serving Size & Quick Meta Bar */}
        <div className="p-6 bg-slate-900/80 border-t border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-6 text-xs text-slate-300">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-emerald-400" />
              <span>{recipe.total_time} mins ({recipe.prep_time}m prep + {recipe.cook_time}m cook)</span>
            </div>
            <div className="flex items-center gap-2">
              <Flame className="w-4 h-4 text-amber-400" />
              <span>{recipe.per_serving_nutrition.calories} kcal / serving</span>
            </div>
          </div>

          {/* Servings Modifier */}
          <div className="flex items-center gap-3 bg-slate-950 px-4 py-2 rounded-2xl border border-slate-800">
            <span className="text-xs font-bold text-slate-400">Servings:</span>
            <button
              onClick={() => handleServingsChange(-1)}
              className="w-7 h-7 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-bold text-sm flex items-center justify-center"
            >
              −
            </button>
            <span className="w-10 text-center font-bold text-white text-sm font-mono">{servings}</span>
            <button
              onClick={() => handleServingsChange(1)}
              className="w-7 h-7 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-bold text-sm flex items-center justify-center"
            >
              +
            </button>
          </div>
        </div>
      </div>

      {/* Start Cooking CTA Button */}
      <div className="flex justify-end">
        <button
          onClick={() => onStartCooking(recipeId)}
          className="w-full sm:w-auto px-8 py-4 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-extrabold text-base shadow-xl shadow-emerald-500/25 hover:scale-105 transition-all flex items-center justify-center gap-3"
        >
          <ChefHat className="w-5 h-5" />
          <span>👨🍳 Start Interactive Cooking Mode</span>
        </button>
      </div>

      {/* Ingredients Required vs Available Table */}
      <div className="glass-panel p-6 rounded-3xl space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div>
            <h2 className="text-xl font-bold text-white">Ingredients Breakdown</h2>
            <p className="text-xs text-slate-400 mt-0.5">{recipe.match_summary}</p>
          </div>

          {recipe.ingredient_table.some(item => !item.is_available) && (
            <button
              onClick={handleAddMissingToShopping}
              className={`px-4 py-2.5 rounded-xl font-bold text-xs flex items-center gap-2 transition-all ${
                addedToShopping
                  ? 'bg-emerald-500 text-slate-950'
                  : 'bg-amber-500/20 text-amber-300 hover:bg-amber-500/30 border border-amber-500/40'
              }`}
            >
              <ShoppingBag className="w-4 h-4" />
              <span>{addedToShopping ? '✓ Added to Shopping List!' : '🛒 Add Missing Ingredients'}</span>
            </button>
          )}
        </div>

        {/* Ingredient Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="text-slate-400 border-b border-slate-800">
                <th className="py-3 px-4 font-semibold">Ingredient</th>
                <th className="py-3 px-4 font-semibold text-right">Required ({servings} serv)</th>
                <th className="py-3 px-4 font-semibold">Status in Kitchen</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {recipe.ingredient_table.map((item, idx) => (
                <tr key={idx} className="hover:bg-slate-900/40 transition-colors">
                  <td className="py-3.5 px-4 font-bold text-white capitalize flex items-center gap-2">
                    {item.ingredient}
                  </td>
                  <td className="py-3.5 px-4 text-right font-mono font-semibold text-slate-300">
                    {item.required_quantity} {item.unit}
                  </td>
                  <td className="py-3.5 px-4">
                    {item.is_available ? (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-300 font-semibold border border-emerald-500/20">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                        {item.available_status}
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-rose-500/10 text-rose-300 font-semibold border border-rose-500/20">
                        <XCircle className="w-3.5 h-3.5 text-rose-400" />
                        Missing
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* "✨ Improve My Meal" & Healthier Substitutions Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Improve My Meal Box */}
        <div className="glass-panel p-6 rounded-3xl space-y-4 border border-emerald-500/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-emerald-400 font-bold text-base">
              <Sparkles className="w-5 h-5" />
              <h3>Improve My Meal</h3>
            </div>
            <button
              onClick={handleImproveMeal}
              disabled={improvingMeal}
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-bold text-xs shadow-md shadow-emerald-500/20 hover:scale-105 transition-all"
            >
              {improvingMeal ? 'Calculating...' : '✨ Improve Profile'}
            </button>
          </div>

          <p className="text-slate-300 text-xs leading-relaxed">
            Optimize oil/fat content, add fresh nutrient-dense greens, and boost fiber and protein ratios.
          </p>

          {/* Before vs After Comparison Card */}
          {improvementResult && (
            <div className="bg-slate-950 p-4 rounded-2xl border border-emerald-500/30 space-y-4 text-xs animate-fade-in">
              <div className="font-bold text-emerald-400 flex items-center justify-between">
                <span>Applied Optimizations:</span>
                <span className="text-slate-400 text-[10px]">NutriScore: {improvementResult.original_health_score} → <strong className="text-emerald-400">{improvementResult.improved_health_score}</strong></span>
              </div>

              <ul className="space-y-1.5 text-slate-300 text-[11px] list-disc list-inside">
                {improvementResult.applied_changes.map((change, i) => (
                  <li key={i}>{change}</li>
                ))}
              </ul>

              <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-800 text-center font-bold">
                <div className="bg-slate-900 p-2 rounded-xl text-emerald-400">
                  {improvementResult.changes_summary.calories_label}
                </div>
                <div className="bg-slate-900 p-2 rounded-xl text-teal-400">
                  {improvementResult.changes_summary.protein_label}
                </div>
                <div className="bg-slate-900 p-2 rounded-xl text-cyan-400">
                  {improvementResult.changes_summary.fiber_label}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Substitutions & Alternatives Box */}
        <div className="glass-panel p-6 rounded-3xl space-y-4">
          <h3 className="font-bold text-white text-base flex items-center gap-2">
            <RefreshCw className="w-4 h-4 text-emerald-400" />
            Healthier Ingredient Substitutions
          </h3>
          <p className="text-slate-400 text-xs">
            Missing an item or looking for higher fiber / lower fat? Select an alternative:
          </p>

          <div className="space-y-3">
            {recipe.substitutions.map((sub, idx) => (
              <div key={idx} className="bg-slate-950 p-3 rounded-2xl border border-slate-800 text-xs space-y-2">
                <div className="flex items-center justify-between font-bold text-slate-200">
                  <span>Replace <strong className="text-amber-400 capitalize">{sub.from}</strong></span>
                  <button
                    onClick={() => handleSelectSubstitution(sub.from, sub.to)}
                    className="px-3 py-1 rounded-lg bg-emerald-500/20 text-emerald-400 text-[11px] hover:bg-emerald-500/30 border border-emerald-500/30"
                  >
                    Swap with {sub.to}
                  </button>
                </div>
                <p className="text-slate-400 text-[11px]">{sub.notes}</p>
              </div>
            ))}

            {recipe.substitutions.length === 0 && (
              <p className="text-slate-500 text-xs italic">No specific substitutions required for this recipe.</p>
            )}
          </div>
        </div>
      </div>

      {/* Nutrition Engine & NutriScore Section */}
      <div className="glass-panel p-6 sm:p-8 rounded-3xl space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div>
            <h2 className="text-xl font-bold text-white">Nutrition Engine</h2>
            <p className="text-xs text-slate-400">Values per serving ({servings} total servings)</p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-black text-emerald-400">{recipe.health_score.score} / 100</div>
            <div className="text-[10px] text-slate-400 font-semibold">{recipe.health_score.label}</div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
          {/* Macro Cards Grid */}
          <div className="grid grid-cols-2 gap-4 text-center">
            <div className="bg-slate-950 p-4 rounded-2xl border border-slate-800">
              <div className="text-xs text-slate-400 font-medium">🔥 Calories</div>
              <div className="text-2xl font-extrabold text-white mt-1">{recipe.per_serving_nutrition.calories} <span className="text-xs font-normal text-slate-400">kcal</span></div>
            </div>
            <div className="bg-slate-950 p-4 rounded-2xl border border-slate-800">
              <div className="text-xs text-slate-400 font-medium">💪 Protein</div>
              <div className="text-2xl font-extrabold text-emerald-400 mt-1">{recipe.per_serving_nutrition.protein} <span className="text-xs font-normal text-slate-400">g</span></div>
            </div>
            <div className="bg-slate-950 p-4 rounded-2xl border border-slate-800">
              <div className="text-xs text-slate-400 font-medium">🍚 Carbs</div>
              <div className="text-2xl font-extrabold text-cyan-400 mt-1">{recipe.per_serving_nutrition.carbs} <span className="text-xs font-normal text-slate-400">g</span></div>
            </div>
            <div className="bg-slate-950 p-4 rounded-2xl border border-slate-800">
              <div className="text-xs text-slate-400 font-medium">🌾 Fiber</div>
              <div className="text-2xl font-extrabold text-violet-400 mt-1">{recipe.per_serving_nutrition.fiber} <span className="text-xs font-normal text-slate-400">g</span></div>
            </div>
          </div>

          {/* Recharts Macro Breakdown */}
          <div className="h-56 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={macroData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {macroData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Mandatory Nutrition Disclaimer */}
        <div className="text-[11px] text-slate-500 italic pt-2 border-t border-slate-800/60">
          Nutrition values are estimates and vary by ingredient, brand, preparation, and portion size.
        </div>
      </div>

      {/* Cooking Instructions Preview */}
      <div className="glass-panel p-6 rounded-3xl space-y-4">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <ChefHat className="w-5 h-5 text-emerald-400" />
          Step-by-step Instructions ({recipe.steps.length} steps)
        </h2>

        <ol className="space-y-3">
          {recipe.steps.map((step, idx) => (
            <li key={idx} className="flex gap-3 text-xs text-slate-300 bg-slate-950/60 p-3.5 rounded-2xl border border-slate-800">
              <span className="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 font-bold flex items-center justify-center shrink-0">
                {idx + 1}
              </span>
              <span className="leading-relaxed mt-0.5">{step}</span>
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
}
