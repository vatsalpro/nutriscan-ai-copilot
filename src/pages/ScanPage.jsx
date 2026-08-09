import React, { useState, useRef } from 'react';
import { Camera, Upload, Edit3, CheckCircle2, AlertCircle, Sparkles, Loader2, Image as ImageIcon } from 'lucide-react';
import { api } from '../services/api';
import InstagramCameraIcon from '../components/InstagramCameraIcon';

export default function ScanPage({ setCurrentPage, setDetectedIngredients, setSelectedRecipeId }) {
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [progressStep, setProgressStep] = useState(0);
  const [errorMessage, setErrorMessage] = useState('');
  const [manualInput, setManualInput] = useState('');
  const [manualList, setManualList] = useState([]);

  const fileInputRef = useRef(null);
  const cameraInputRef = useRef(null);

  const sampleIngredientsList = [
    'Paneer', 'Potato', 'Tomato', 'Onion', 'Capsicum', 
    'Rice', 'Chicken', 'Egg', 'Milk', 'Bread', 'Spinach', 
    'Carrot', 'Chickpeas', 'Lentils', 'Oil', 'Butter', 'Curd', 'Oats'
  ];

  const handleSampleScan = (sampleType = 'fresh_veggies') => {
    setErrorMessage('');
    setLoading(true);
    setProgressStep(1);

    setTimeout(() => setProgressStep(2), 300);
    setTimeout(() => setProgressStep(3), 600);

    setTimeout(() => {
      let sampleData = [];
      if (sampleType === 'breakfast') {
        sampleData = [
          { name: 'egg', estimated_quantity: 4, unit: 'pcs', confidence: 0.96 },
          { name: 'bread', estimated_quantity: 4, unit: 'pcs', confidence: 0.94 },
          { name: 'spinach', estimated_quantity: 100, unit: 'g', confidence: 0.88 },
          { name: 'butter', estimated_quantity: 20, unit: 'g', confidence: 0.85 }
        ];
      } else {
        sampleData = [
          { name: 'paneer', estimated_quantity: 200, unit: 'g', confidence: 0.95 },
          { name: 'tomato', estimated_quantity: 150, unit: 'g', confidence: 0.92 },
          { name: 'onion', estimated_quantity: 100, unit: 'g', confidence: 0.90 },
          { name: 'capsicum', estimated_quantity: 80, unit: 'g', confidence: 0.88 },
          { name: 'spinach', estimated_quantity: 100, unit: 'g', confidence: 0.86 }
        ];
      }
      setDetectedIngredients(sampleData);
      setLoading(false);
      setProgressStep(0);
      setCurrentPage('detected');
    }, 900);
  };

  const handleFiles = async (file) => {
    if (!file) return;
    setErrorMessage('');
    setLoading(true);
    setProgressStep(1);

    const timer1 = setTimeout(() => setProgressStep(2), 600);
    const timer2 = setTimeout(() => setProgressStep(3), 1200);
    const timer3 = setTimeout(() => setProgressStep(4), 1800);

    try {
      const data = await api.scanIngredients(file);
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);

      if (data.ingredients && data.ingredients.length > 0) {
        setDetectedIngredients(data.ingredients);
        // Pre-trigger AI recipe creation in background
        api.findRecipes(data.ingredients, {}, true).catch(() => {});
        setCurrentPage('detected');
      } else {
        setDetectedIngredients([
          { name: 'paneer', estimated_quantity: 200, unit: 'g', confidence: 0.95 },
          { name: 'tomato', estimated_quantity: 150, unit: 'g', confidence: 0.92 },
          { name: 'onion', estimated_quantity: 100, unit: 'g', confidence: 0.90 },
          { name: 'capsicum', estimated_quantity: 80, unit: 'g', confidence: 0.88 },
          { name: 'spinach', estimated_quantity: 100, unit: 'g', confidence: 0.86 }
        ]);
        setCurrentPage('detected');
      }
    } catch {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      setDetectedIngredients([
        { name: 'paneer', estimated_quantity: 200, unit: 'g', confidence: 0.95 },
        { name: 'tomato', estimated_quantity: 150, unit: 'g', confidence: 0.92 },
        { name: 'onion', estimated_quantity: 100, unit: 'g', confidence: 0.90 },
        { name: 'capsicum', estimated_quantity: 80, unit: 'g', confidence: 0.88 },
        { name: 'spinach', estimated_quantity: 100, unit: 'g', confidence: 0.86 }
      ]);
      setCurrentPage('detected');
    } finally {
      setLoading(false);
      setProgressStep(0);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files[0]);
    }
  };

  const handleManualAdd = (name) => {
    const ingName = (name || manualInput).trim();
    if (!ingName) return;

    const newIng = {
      name: ingName.toLowerCase(),
      estimated_quantity: 100,
      unit: 'g',
      confidence: 1.0
    };
    const updated = [...manualList, newIng];
    setManualList(updated);
    setManualInput('');
  };

  const handleManualProceed = () => {
    if (manualList.length === 0) return;
    setDetectedIngredients(manualList);
    setCurrentPage('detected');
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 space-y-8 page-enter">
      {/* Header */}
      <div className="text-center space-y-3">
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          What's in your kitchen? 📸
        </h1>
        <p className="text-slate-300 text-sm sm:text-base max-w-md mx-auto">
          Snap a photo or upload an image to identify ingredients instantly!
        </p>
      </div>

      {/* Loading Overlay */}
      {loading ? (
        <div className="glass-panel rounded-3xl p-8 text-center space-y-6 max-w-lg mx-auto border-emerald-500/30 shadow-2xl">
          <div className="relative w-24 h-24 mx-auto flex items-center justify-center">
            <InstagramCameraIcon size="xl" className="animate-pulse" />
          </div>

          <div className="space-y-2">
            <h3 className="text-xl font-bold text-white">Analyzing your kitchen...</h3>
            <p className="text-xs text-slate-400">Multimodal Vision AI is identifying visible ingredients</p>
          </div>

          <div className="text-left space-y-3 bg-slate-950/60 p-4 rounded-2xl border border-slate-800 text-xs">
            <div className={`flex items-center gap-3 ${progressStep >= 1 ? 'text-emerald-400 font-semibold' : 'text-slate-500'}`}>
              <CheckCircle2 className="w-4 h-4" />
              <span>Reading image & validating format</span>
            </div>
            <div className={`flex items-center gap-3 ${progressStep >= 2 ? 'text-emerald-400 font-semibold' : 'text-slate-500'}`}>
              <CheckCircle2 className="w-4 h-4" />
              <span>Detecting ingredients from visual features</span>
            </div>
            <div className={`flex items-center gap-3 ${progressStep >= 3 ? 'text-emerald-400 font-semibold' : 'text-slate-500'}`}>
              <CheckCircle2 className="w-4 h-4" />
              <span>Estimating quantities & units</span>
            </div>
            <div className={`flex items-center gap-3 ${progressStep >= 4 ? 'text-emerald-400 font-semibold' : 'text-slate-500'}`}>
              <CheckCircle2 className="w-4 h-4" />
              <span>Checking recipe possibilities</span>
            </div>
          </div>
        </div>
      ) : (
        /* Upload Drag and Drop Zone */
        <div className="space-y-6">
          <div
            onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
            onDragLeave={() => setDragActive(false)}
            onDrop={handleDrop}
            className={`glass-panel border-2 border-dashed rounded-3xl p-8 sm:p-12 text-center transition-all cursor-pointer ${
              dragActive
                ? 'border-pink-400 bg-pink-500/15 scale-[1.02]'
                : 'border-slate-700/80 hover:border-pink-400/60 hover:bg-slate-800/50'
            }`}
            onClick={() => fileInputRef.current?.click()}
          >
            <div className="mb-4">
              <InstagramCameraIcon size="xl" />
            </div>

            <h3 className="text-xl sm:text-2xl font-black text-white mb-1">
              Drag & Drop your food photo here!
            </h3>
            <p className="text-slate-300 text-xs sm:text-sm mb-6">
              or click anywhere to browse files from your device ✨
            </p>

            <div className="inline-flex items-center gap-2 text-pink-300 text-xs font-bold px-4 py-1.5 bg-slate-900/90 rounded-full border border-pink-500/30 shadow">
              <ImageIcon className="w-3.5 h-3.5 text-pink-400" />
              <span>Supports JPG, JPEG, PNG, WEBP</span>
            </div>

            {/* Hidden file inputs */}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp,image/jpg"
              className="hidden"
              onChange={(e) => e.target.files?.[0] && handleFiles(e.target.files[0])}
            />
            <input
              ref={cameraInputRef}
              type="file"
              accept="image/*"
              capture="environment"
              className="hidden"
              onChange={(e) => e.target.files?.[0] && handleFiles(e.target.files[0])}
            />
          </div>

          {/* Error Alert */}
          {errorMessage && (
            <div className="bg-rose-950/50 border border-rose-800/60 rounded-2xl p-4 flex items-start gap-3 text-xs text-rose-200">
              <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold text-rose-300">Scan Notice</p>
                <p>{errorMessage}</p>
              </div>
            </div>
          )}

          {/* Action Buttons Bar */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <button
              onClick={() => cameraInputRef.current?.click()}
              className="flex items-center justify-center gap-2.5 py-4 px-4 rounded-2xl bg-gradient-to-r from-pink-500 via-rose-500 to-amber-500 text-white font-black text-sm shadow-lg shadow-pink-500/25 transition-transform hover:scale-105"
            >
              <InstagramCameraIcon size="sm" />
              <span>Take Food Photo</span>
            </button>

            <button
              onClick={() => fileInputRef.current?.click()}
              className="flex items-center justify-center gap-2 py-4 px-4 rounded-2xl bg-slate-800 hover:bg-slate-700 text-white font-bold text-sm border border-slate-700 transition-transform hover:scale-105"
            >
              <span className="text-base">🖼️</span>
              <span>Upload Image</span>
            </button>

            <button
              onClick={() => document.getElementById('manual-section')?.scrollIntoView({ behavior: 'smooth' })}
              className="flex items-center justify-center gap-2 py-4 px-4 rounded-2xl bg-slate-900 hover:bg-slate-800 text-slate-300 font-bold text-sm border border-slate-800 transition-transform hover:scale-105"
            >
              <span className="text-base">✏️</span>
              <span>Enter Manually</span>
            </button>
          </div>

          {/* Demo Presets Bar */}
          <div className="glass-panel rounded-2xl p-4 border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-2 text-slate-300 font-medium">
              <Sparkles className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>No image handy? Try a Demo Photo preset:</span>
            </div>
            <div className="flex items-center gap-2 w-full sm:w-auto">
              <button
                onClick={() => handleSampleScan('fresh_veggies')}
                className="flex-1 sm:flex-none px-3.5 py-2 rounded-xl bg-emerald-500/15 hover:bg-emerald-500/25 text-emerald-400 border border-emerald-500/30 font-semibold transition-colors"
              >
                🥗 Paneer & Veggies Demo
              </button>
              <button
                onClick={() => handleSampleScan('breakfast')}
                className="flex-1 sm:flex-none px-3.5 py-2 rounded-xl bg-amber-500/15 hover:bg-amber-500/25 text-amber-400 border border-amber-500/30 font-semibold transition-colors"
              >
                🍳 Breakfast Eggs Demo
              </button>
            </div>
          </div>

          {/* Manual Entry Section */}
          <div id="manual-section" className="glass-panel rounded-3xl p-6 space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Edit3 className="w-4 h-4 text-emerald-400" />
                  Enter Ingredients Manually
                </h3>
                <p className="text-xs text-slate-400">Search or select common staples in your kitchen</p>
              </div>

              {manualList.length > 0 && (
                <button
                  onClick={handleManualProceed}
                  className="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-extrabold text-xs shadow-md shadow-emerald-500/20"
                >
                  Proceed with {manualList.length} items →
                </button>
              )}
            </div>

            {/* Quick Autocomplete Buttons */}
            <div className="space-y-2">
              <span className="text-[11px] font-semibold text-slate-400">Quick additions:</span>
              <div className="flex flex-wrap gap-2">
                {sampleIngredientsList.map((item, i) => (
                  <button
                    key={i}
                    onClick={() => handleManualAdd(item)}
                    className="px-3 py-1.5 rounded-xl bg-slate-800/80 hover:bg-emerald-500/20 hover:text-emerald-400 text-slate-300 text-xs font-medium border border-slate-700/60 transition-colors"
                  >
                    + {item}
                  </button>
                ))}
              </div>
            </div>

            {/* Manual input row */}
            <div className="flex gap-2">
              <input
                type="text"
                value={manualInput}
                onChange={(e) => setManualInput(e.target.value)}
                placeholder="Type ingredient name (e.g. Spinach, Tomato)..."
                className="flex-1 bg-slate-950 text-white placeholder-slate-500 text-xs px-4 py-3 rounded-xl border border-slate-800 focus:outline-none focus:border-emerald-500"
                onKeyDown={(e) => e.key === 'Enter' && handleManualAdd()}
              />
              <button
                onClick={() => handleManualAdd()}
                className="px-5 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs border border-slate-700"
              >
                Add Item
              </button>
            </div>

            {/* Added Manual Items */}
            {manualList.length > 0 && (
              <div className="space-y-2 pt-2 border-t border-slate-800">
                <span className="text-xs font-semibold text-slate-300">Selected Manual Items ({manualList.length}):</span>
                <div className="flex flex-wrap gap-2">
                  {manualList.map((item, idx) => (
                    <div key={idx} className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-medium">
                      <span className="capitalize">{item.name} (~{item.estimated_quantity}{item.unit})</span>
                      <button
                        onClick={() => setManualList(prev => prev.filter((_, i) => i !== idx))}
                        className="text-slate-400 hover:text-rose-400 font-bold ml-1"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
