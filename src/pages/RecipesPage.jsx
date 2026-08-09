import React, { useState, useEffect } from 'react';
import { Clock, Flame, Users, Sparkles, Search, Zap } from 'lucide-react';
import { api } from '../services/api';


export default function RecipesPage({ ingredients, setSelectedRecipeId, setCurrentPage }) {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilters, setActiveFilters] = useState({
    under_20: false,
    high_protein: false,
    budget: false,
    vegetarian: false,
    vegan: false,
    high_fiber: false,
    low_calorie: false,
  });
  const [maxBudget, setMaxBudget] = useState(null);
  const [aiRecipeGenerated, setAiRecipeGenerated] = useState(false);

  const filterOptions = [
    { key: 'under_20', label: '⚡ Under 20 min' },
    { key: 'high_protein', label: '💪 High Protein' },
    { key: 'budget', label: '💰 Budget Friendly' },
    { key: 'vegetarian', label: '🌱 Vegetarian' },
    { key: 'vegan', label: '🌿 Vegan' },
    { key: 'high_fiber', label: '🌾 High Fiber' },
    { key: 'low_calorie', label: '🔥 Low Calorie' },
  ];

  const budgetTiers = [
    { label: 'All Budgets', value: null },
    { label: 'Under ₹75', value: 75 },
    { label: 'Under ₹100', value: 100 },
    { label: 'Under ₹150', value: 150 },
  ];

  const loadRecipes = async () => {
    setLoading(true);
    try {
      const filterPayload = { ...activeFilters, max_budget: maxBudget };
      const res = await api.findRecipes(ingredients, filterPayload, true);
      setRecipes(res.recipes || []);
      setAiRecipeGenerated(Boolean(res.ai_recipe_generated));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRecipes();
  }, [activeFilters, maxBudget, ingredients]);

  const toggleFilter = (key) => {
    setActiveFilters(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const filteredRecipes = recipes.filter(r => 
    r.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.tags.some(t => t.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 space-y-8">
      {/* Header */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Smart Ingredient Matcher</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white">
          What can you cook?
        </h1>
        <p className="text-slate-300 text-sm max-w-xl">
          Recipes matched against your scanned ingredients and pantry items.
        </p>
        {aiRecipeGenerated && (
          <div className="inline-flex items-center gap-2 rounded-xl border border-violet-500/30 bg-violet-500/10 px-3 py-2 text-xs text-violet-200">
            <Sparkles className="w-4 h-4 text-violet-300" />
            Your scanned ingredient was new, so AI created and saved a recipe for it.
          </div>
        )}
      </div>

      {/* Search & Filter Controls Bar */}
      <div className="space-y-4">
        <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
          {/* Search bar */}
          <div className="relative w-full md:w-80">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search recipes (e.g. Paneer, Chicken, Fried Rice)..."
              className="w-full bg-slate-900 text-white placeholder-slate-500 text-xs pl-10 pr-4 py-3 rounded-2xl border border-slate-800 focus:outline-none focus:border-emerald-500"
            />
          </div>

          {/* Budget Selector */}
          <div className="flex items-center gap-2 overflow-x-auto w-full md:w-auto scrollbar-none">
            <span className="text-xs font-semibold text-slate-400 shrink-0">Budget:</span>
            {budgetTiers.map((tier, idx) => (
              <button
                key={idx}
                onClick={() => setMaxBudget(tier.value)}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all shrink-0 ${
                  maxBudget === tier.value
                    ? 'bg-amber-500 text-slate-950 shadow-md shadow-amber-500/20'
                    : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
                }`}
              >
                {tier.label}
              </button>
            ))}
          </div>
        </div>

        {/* Filter Pills */}
        <div className="flex flex-wrap items-center gap-2">
          {filterOptions.map((f) => {
            const isActive = activeFilters[f.key];
            return (
              <button
                key={f.key}
                onClick={() => toggleFilter(f.key)}
                className={`px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-emerald-500 text-slate-950 shadow-md shadow-emerald-500/30'
                    : 'bg-slate-900 text-slate-300 hover:bg-slate-800 border border-slate-800'
                }`}
              >
                {f.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Recipe Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((n) => (
            <div key={n} className="glass-card rounded-3xl h-96 animate-pulse bg-slate-900/60 p-4"></div>
          ))}
        </div>
      ) : filteredRecipes.length === 0 ? (
        <div className="glass-panel rounded-3xl p-12 text-center space-y-3">
          <p className="text-slate-400 text-sm">No recipes match the selected filters or search query.</p>
          <button
            onClick={() => {
              setActiveFilters({ under_20: false, high_protein: false, budget: false, vegetarian: false, vegan: false, high_fiber: false, low_calorie: false });
              setMaxBudget(null);
              setSearchQuery('');
            }}
            className="px-4 py-2 bg-slate-800 text-emerald-400 font-semibold text-xs rounded-xl border border-slate-700"
          >
            Clear Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredRecipes.map((recipe) => (
            <div
              key={recipe.id}
              onClick={() => {
                setSelectedRecipeId(recipe.id);
                setCurrentPage('recipe-detail');
              }}
              className="glass-card rounded-3xl overflow-hidden border border-slate-800 hover:border-emerald-500/50 flex flex-col justify-between cursor-pointer group"
            >
              {/* Image & Match Badge Header */}
              <div className="relative h-48 overflow-hidden">
                <img
                  src={recipe.image_url}
                  alt={recipe.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/20 to-transparent"></div>

                {/* Match Percentage Badge */}
                <div className="absolute top-3 left-3 bg-emerald-500 text-slate-950 font-extrabold text-xs px-3 py-1 rounded-full shadow-lg flex items-center gap-1">
                  <Zap className="w-3.5 h-3.5 fill-slate-950" />
                  <span>{recipe.match_percentage}% match</span>
                </div>

                {/* Cost Tag */}
                <div className="absolute top-3 right-3 bg-slate-950/80 backdrop-blur-md text-amber-400 font-bold text-xs px-2.5 py-1 rounded-full border border-amber-500/30">
                  ₹{recipe.estimated_cost} (~₹{recipe.cost_per_serving}/serv)
                </div>

                {/* Recipe Name Overlay */}
                <div className="absolute bottom-3 left-3 right-3">
                  <h3 className="text-xl font-bold text-white group-hover:text-emerald-300 transition-colors">
                    {recipe.name}
                  </h3>
                  <div className="text-emerald-400 font-medium text-xs mt-0.5">
                    {recipe.match_summary}
                  </div>
                </div>
              </div>

              {/* Recipe Body Info */}
              <div className="p-5 space-y-4 flex-1 flex flex-col justify-between">
                <p className="text-slate-400 text-xs line-clamp-2 leading-relaxed">
                  {recipe.description}
                </p>

                {/* Stats Row */}
                <div className="grid grid-cols-3 gap-2 bg-slate-950/60 p-2.5 rounded-2xl border border-slate-800 text-[11px] text-slate-300">
                  <div className="flex items-center gap-1.5 justify-center">
                    <Clock className="w-3.5 h-3.5 text-emerald-400" />
                    <span>{recipe.total_time} min</span>
                  </div>
                  <div className="flex items-center gap-1.5 justify-center border-x border-slate-800">
                    <Users className="w-3.5 h-3.5 text-cyan-400" />
                    <span>{recipe.servings} serv</span>
                  </div>
                  <div className="flex items-center gap-1.5 justify-center">
                    <Flame className="w-3.5 h-3.5 text-amber-400" />
                    <span>~{recipe.per_serving_nutrition.calories} kcal</span>
                  </div>
                </div>

                {/* Available & Missing Ingredients snippet */}
                <div className="space-y-2 text-[11px]">
                  {/* Available */}
                  <div className="flex flex-wrap gap-1.5 items-center">
                    <span className="text-slate-500 font-semibold text-[10px]">Available:</span>
                    {recipe.available_ingredients.slice(0, 4).map((ing, idx) => (
                      <span key={idx} className="px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 font-medium capitalize">
                        ✓ {ing.ingredient}
                      </span>
                    ))}
                    {recipe.available_ingredients.length > 4 && (
                      <span className="text-emerald-400 text-[10px]">+{recipe.available_ingredients.length - 4} more</span>
                    )}
                  </div>

                  {/* Missing */}
                  {recipe.missing_ingredients.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 items-center">
                      <span className="text-slate-500 font-semibold text-[10px]">Missing:</span>
                      {recipe.missing_ingredients.slice(0, 3).map((ing, idx) => (
                        <span key={idx} className="px-2 py-0.5 rounded-md bg-amber-500/10 text-amber-300 border border-amber-500/20 font-medium capitalize">
                          ⚠ {ing.ingredient}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Footer Action */}
                <div className="pt-2 flex items-center justify-between border-t border-slate-800 text-xs">
                  <div className="flex gap-1">
                    {recipe.tags.slice(0, 2).map((tag, idx) => (
                      <span key={idx} className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 text-[10px] capitalize">
                        {tag}
                      </span>
                    ))}
                  </div>
                  <span className="text-emerald-400 font-bold flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                    View Recipe →
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
