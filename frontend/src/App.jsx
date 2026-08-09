import React, { useState, lazy, Suspense } from 'react';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import AssistantDrawer from './components/AssistantDrawer';
import FunFactPopup from './components/FunFactPopup';
import FruitBurstOverlay from './components/FruitBurstOverlay';
import BackgroundDecorations from './components/BackgroundDecorations';

// Eagerly loaded primary pages for instant initial load
import HomePage from './pages/HomePage';
import ScanPage from './pages/ScanPage';
import DetectedPage from './pages/DetectedPage';
import RecipesPage from './pages/RecipesPage';

// Lazy loaded secondary pages to cut initial bundle size by >80%
const RecipeDetailPage = lazy(() => import('./pages/RecipeDetailPage'));
const CookPage = lazy(() => import('./pages/CookPage'));
const PantryPage = lazy(() => import('./pages/PantryPage'));
const NutritionPage = lazy(() => import('./pages/NutritionPage'));
const ShoppingPage = lazy(() => import('./pages/ShoppingPage'));
const MealScanPage = lazy(() => import('./pages/MealScanPage'));

const PageLoader = () => (
  <div className="py-20 text-center text-slate-400 text-sm animate-pulse flex items-center justify-center gap-2">
    <div className="w-4 h-4 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin" />
    <span>Loading page...</span>
  </div>
);


export default function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [ingredients, setIngredients] = useState([
    // Default initial demo set for instant preview if needed
    { name: 'paneer', estimated_quantity: 200, unit: 'g', confidence: 0.94 },
    { name: 'potato', estimated_quantity: 250, unit: 'g', confidence: 0.92 },
    { name: 'tomato', estimated_quantity: 150, unit: 'g', confidence: 0.91 },
    { name: 'onion', estimated_quantity: 100, unit: 'g', confidence: 0.89 },
    { name: 'capsicum', estimated_quantity: 80, unit: 'g', confidence: 0.87 }
  ]);
  const [selectedRecipeId, setSelectedRecipeId] = useState('paneer-masala');
  const [assistantOpen, setAssistantOpen] = useState(false);

  const handleStartCooking = (recipeId) => {
    setSelectedRecipeId(recipeId);
    setCurrentPage('cook');
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col justify-between selection:bg-emerald-500 selection:text-slate-950 bg-grid bg-cute-mesh relative overflow-x-hidden">
      {/* Populated Ambient Background Light Orbs & Floating Emojis */}
      <BackgroundDecorations />

      {/* Global Interactive Fruit Burst Popping Animation on Clicks */}
      <FruitBurstOverlay />

      <div>
        <Navbar
          currentPage={currentPage}
          setCurrentPage={setCurrentPage}
          onOpenAssistant={() => setAssistantOpen(true)}
        />

        <main className="pb-12">
          <Suspense fallback={<PageLoader />}>
            <div key={currentPage} className="page-enter">
              {currentPage === 'home' && (
                <HomePage
                  setCurrentPage={setCurrentPage}
                  onSelectDemoIngredients={(items) => setIngredients(items)}
                />
              )}

              {currentPage === 'scan' && (
                <ScanPage
                  setCurrentPage={setCurrentPage}
                  setDetectedIngredients={setIngredients}
                  setSelectedRecipeId={setSelectedRecipeId}
                />
              )}

              {currentPage === 'detected' && (
                <DetectedPage
                  ingredients={ingredients}
                  setIngredients={setIngredients}
                  setCurrentPage={setCurrentPage}
                />
              )}

              {currentPage === 'recipes' && (
                <RecipesPage
                  ingredients={ingredients}
                  setSelectedRecipeId={setSelectedRecipeId}
                  setCurrentPage={setCurrentPage}
                />
              )}

              {currentPage === 'recipe-detail' && (
                <RecipeDetailPage
                  recipeId={selectedRecipeId}
                  setCurrentPage={setCurrentPage}
                  onStartCooking={handleStartCooking}
                />
              )}

              {currentPage === 'cook' && (
                <CookPage
                  recipeId={selectedRecipeId}
                  setCurrentPage={setCurrentPage}
                />
              )}

              {currentPage === 'pantry' && (
                <PantryPage
                  setCurrentPage={setCurrentPage}
                  setIngredients={setIngredients}
                />
              )}

              {currentPage === 'nutrition' && (
                <NutritionPage />
              )}

              {currentPage === 'shopping' && (
                <ShoppingPage />
              )}

              {currentPage === 'scan-meal' && (
                <MealScanPage setCurrentPage={setCurrentPage} />
              )}
            </div>
          </Suspense>
        </main>

      </div>

      <Footer />

      <FunFactPopup />

      {/* Floating AI Kitchen Assistant Drawer */}
      <AssistantDrawer
        isOpen={assistantOpen}
        onClose={() => setAssistantOpen(false)}
        currentRecipe={selectedRecipeId}
        userIngredients={ingredients}
      />
    </div>
  );
}
