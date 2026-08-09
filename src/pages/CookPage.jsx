import React, { useState, useEffect, useRef } from 'react';
import { ArrowLeft, CheckCircle, ChefHat, Clock, Sparkles, Play, Pause, RotateCcw } from 'lucide-react';
import { api } from '../services/api';


export default function CookPage({ recipeId, setCurrentPage }) {
  const [recipe, setRecipe] = useState(null);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [completed, setCompleted] = useState(false);
  const [loggingMeal, setLoggingMeal] = useState(false);
  const [logged, setLogged] = useState(false);

  /* Cooking Stopwatch Timer */
  const [timerSeconds, setTimerSeconds] = useState(0);
  const [isTimerRunning, setIsTimerRunning] = useState(false);
  const timerRef = useRef(null);

  useEffect(() => {
    if (isTimerRunning) {
      timerRef.current = setInterval(() => {
        setTimerSeconds(s => s + 1);
      }, 1000);
    } else {
      clearInterval(timerRef.current);
    }
    return () => clearInterval(timerRef.current);
  }, [isTimerRunning]);

  const formatTimer = (totalSeconds) => {
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  useEffect(() => {
    const fetchRecipe = async () => {
      try {
        const data = await api.getRecipeDetails(recipeId);
        setRecipe(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    if (recipeId) fetchRecipe();
  }, [recipeId]);

  if (loading || !recipe) {
    return (
      <div className="max-w-xl mx-auto py-20 px-4 text-center text-slate-400">
        Loading cooking instructions...
      </div>
    );
  }

  const steps = recipe.steps || [];
  const totalSteps = steps.length;
  const progressPct = Math.round(((currentStepIndex + 1) / totalSteps) * 100);

  const handleNext = () => {
    if (currentStepIndex < totalSteps - 1) {
      setCurrentStepIndex(prev => prev + 1);
    } else {
      setCompleted(true);
      setIsTimerRunning(false);
    }
  };

  const handlePrev = () => {
    if (completed) {
      setCompleted(false);
    } else if (currentStepIndex > 0) {
      setCurrentStepIndex(prev => prev - 1);
    }
  };

  const handleLogMeal = async () => {
    setLoggingMeal(true);
    try {
      await api.logMeal({
        recipe_id: recipe.id,
        meal_name: recipe.name,
        meal_type: "Lunch",
        servings: 1.0,
        calories: recipe.per_serving_nutrition.calories,
        protein: recipe.per_serving_nutrition.protein,
        carbs: recipe.per_serving_nutrition.carbs,
        fat: recipe.per_serving_nutrition.fat,
        fiber: recipe.per_serving_nutrition.fiber
      });
      setLogged(true);
    } catch (err) {
      console.error(err);
    } finally {
      setLoggingMeal(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-8 px-4 space-y-8 min-h-[80vh] flex flex-col justify-between page-enter">
      {/* Top Header */}
      <div className="flex flex-wrap items-center justify-between border-b border-slate-800 pb-4 gap-3">
        <button
          onClick={() => setCurrentPage('recipe-detail')}
          className="flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white bg-slate-900 px-3 py-2 rounded-xl border border-slate-800 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Exit Cooking Mode</span>
        </button>

        {/* Stopwatch Timer */}
        <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs">
          <Clock className="w-4 h-4 text-emerald-400" />
          <span className="font-mono font-bold text-white min-w-[38px]">{formatTimer(timerSeconds)}</span>
          <button
            onClick={() => setIsTimerRunning(!isTimerRunning)}
            className="p-1 rounded hover:bg-slate-800 text-slate-300 transition-colors"
            title={isTimerRunning ? "Pause timer" : "Start timer"}
          >
            {isTimerRunning ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
          </button>
          <button
            onClick={() => {
              setTimerSeconds(0);
              setIsTimerRunning(false);
            }}
            className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
            title="Reset timer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="flex items-center gap-2 text-xs font-bold text-emerald-400 bg-emerald-500/10 px-3 py-1.5 rounded-full border border-emerald-500/20">
          <ChefHat className="w-4 h-4" />
          <span>{recipe.name}</span>
        </div>
      </div>

      {!completed ? (
        /* Active Cooking Step Screen */
        <div className="glass-panel p-8 sm:p-12 rounded-3xl space-y-8 my-auto text-center border-emerald-500/30 shadow-2xl">
          {/* Progress Indicator */}
          <div className="space-y-3">
            <div className="flex items-center justify-between text-xs font-mono font-bold text-slate-400">
              <span className="text-emerald-400">STEP {currentStepIndex + 1} OF {totalSteps}</span>
              <span>{progressPct}% COMPLETE</span>
            </div>

            {/* Visual Progress Bar */}
            <div className="w-full h-3 bg-slate-950 rounded-full overflow-hidden border border-slate-800 p-0.5">
              <div
                className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full transition-all duration-500"
                style={{ width: `${progressPct}%` }}
              ></div>
            </div>
          </div>

          {/* Current Step Big Display */}
          <div className="space-y-4 py-6">
            <div className="w-16 h-16 rounded-2xl bg-emerald-500/20 text-emerald-400 font-black text-2xl mx-auto flex items-center justify-center border border-emerald-500/30">
              {currentStepIndex + 1}
            </div>
            <p className="text-xl sm:text-2xl font-bold text-white leading-relaxed max-w-xl mx-auto">
              {steps[currentStepIndex]}
            </p>
          </div>

          {/* Navigation Controls */}
          <div className="flex items-center justify-between gap-4 pt-4 border-t border-slate-800">
            <button
              onClick={handlePrev}
              disabled={currentStepIndex === 0}
              className="flex-1 max-w-[160px] py-3.5 px-4 rounded-2xl bg-slate-800 hover:bg-slate-700 text-white font-bold text-sm border border-slate-700 disabled:opacity-30 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Previous</span>
            </button>

            <button
              onClick={handleNext}
              className="flex-1 max-w-[200px] py-3.5 px-4 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-extrabold text-sm shadow-lg shadow-emerald-500/25 hover:scale-105 transition-all flex items-center justify-center gap-2"
            >
              <span>{currentStepIndex === totalSteps - 1 ? 'Finish Dish 🎉' : 'Next Step →'}</span>
            </button>
          </div>
        </div>
      ) : (
        /* Celebration Completed Screen */
        <div className="glass-panel p-10 rounded-3xl text-center space-y-6 my-auto border-emerald-500/40">
          <div className="w-20 h-20 rounded-full bg-emerald-500/20 text-emerald-400 mx-auto flex items-center justify-center border border-emerald-500/40 animate-bounce">
            <CheckCircle className="w-10 h-10" />
          </div>

          <div className="space-y-2">
            <h2 className="text-3xl font-extrabold text-white">Bon Appétit! 🍽️</h2>
            <p className="text-slate-300 text-sm max-w-md mx-auto">
              You cooked <strong className="text-emerald-400">{recipe.name}</strong>! Estimated nutrition: {recipe.per_serving_nutrition.calories} kcal, {recipe.per_serving_nutrition.protein}g protein.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <button
              onClick={handleLogMeal}
              disabled={logged || loggingMeal}
              className={`px-6 py-3.5 rounded-2xl font-bold text-sm transition-all flex items-center gap-2 ${
                logged
                  ? 'bg-emerald-500 text-slate-950'
                  : 'bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30 border border-emerald-500/40'
              }`}
            >
              <Sparkles className="w-4 h-4" />
              <span>{logged ? '✓ Logged to Today’s Nutrition!' : 'Log Meal to Dashboard'}</span>
            </button>

            <button
              onClick={() => setCurrentPage('home')}
              className="px-6 py-3.5 rounded-2xl bg-slate-800 text-white font-bold text-sm border border-slate-700"
            >
              Return Home
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
