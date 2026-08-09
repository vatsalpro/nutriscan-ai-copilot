# 🥗 NutriScan — AI Kitchen Copilot

> **"Most recipe apps ask what you want to eat. NutriScan asks what you already have."**

**Tagline**: *Scan it. Cook it. Understand it.*

NutriScan is an AI-powered kitchen copilot built for hackathons. It lets users photograph or upload ingredients they already have in their kitchen, uses a 3-provider multimodal vision AI failover stack (Groq Meta Llama 4 Scout -> OpenRouter Gemma 4 Free -> OpenRouter Free Router) to identify them, allows users to confirm/edit quantities, matches recipes they can actually cook, shows required vs available ingredient breakdowns, calculates deterministic nutrition, provides step-by-step interactive cooking instructions, suggests healthier meal improvements, estimates costs, and helps reduce food waste.

---

## 🌟 Key Features

1. **📸 Multimodal Vision Ingredient Detection**:
   - Uses **3-Provider AI Failover Stack** (Groq Llama 4 Scout → OpenRouter Gemma 4 → OpenRouter Free) for image understanding and ingredient identification.
   - Includes **DemoVisionProvider** fallback mode when AI providers are unavailable.
2. **⚖️ Estimated Quantity Confirmation**:
   - Honest AI representation labeled as "AI estimate ~200g".
   - Interactive quantity controls (`[-] 200g [+]`) & unit pickers.
3. **🍳 Smart Recipe Match Engine**:
   - Match score percentage (e.g. 92% match, 9 of 10 available).
   - Filter pills: Under 20 min, High Protein, Healthy, Budget, Vegetarian, Vegan, High Fiber, Low Calorie.
4. **📊 Deterministic Nutrition Engine**:
   - Calculated from SQLite database benchmark values per 100g.
   - Interactive Recharts visualization for Protein, Carbs, Fat, and Fiber per serving.
5. **✨ "Improve My Meal"**:
   - One-click health profile optimizer halving cooking oil, adding fresh greens, and boosting fiber/protein.
   - Before vs after nutrition comparison (% change).
6. **🔄 Healthier Ingredient Substitutions**:
   - Swaps Paneer for Tofu or Chickpeas with dynamic macro recalculations.
7. **🛒 Missing Ingredients & Shopping List**:
   - Auto-adds missing recipe items to shopping list with check/uncheck management.
8. **♻️ Pantry & Food Waste Reduction**:
   - Track inventory with freshness status ("Fresh", "Use Soon", "Expiring Soon").
   - "What Can I Cook?" prioritizes ingredients nearing expiration.
9. **👨🍳 Interactive Step-by-Step Cooking Mode**:
   - Distraction-free cooking view with progress indicator `STEP X OF Y`.
10. **🍽️ Prepared Meal Scanner (`/scan-meal`)**:
    - Upload cooked dish photo -> AI identifies dish, portion weight (~350g), and nutrition.
11. **👨🍳 Ask NutriScan (AI Kitchen Assistant)**:
    - Context-aware side drawer assistant for culinary tips and substitutions.

---

## 🏗️ Architecture

```text
User Image (Web / Mobile)
       ↓
React + Vite Frontend (Vercel)
       ↓
FastAPI Backend (Vercel Serverless /api)
       ↓
VisionService & AI Router (3-Provider Failover)
       ├── 1. Groq (Meta Llama 4 Scout)
       ├── 2. OpenRouter (Google Gemma 4 Free)
       └── 3. OpenRouter Free Router
       ↓
Deterministic Nutrition & Scoring Engine + SQLite DB
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Backend Setup
```bash
cd backend
python -m pip install -r requirements.txt
cp .env.example .env
```
*(Optional: Add your `GEMINI_API_KEY` in `backend/.env`. If left empty, NutriScan automatically runs in **Demo Mode** for seamless hackathon testing.)*

Run the FastAPI backend server:
```bash
python main.py
```
Backend API will run at `http://localhost:8000`. Database seeds automatically on startup.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend app will run at `http://localhost:5173`.

---

## 🔗 API Endpoints

- `POST /api/scan/ingredients` — Multimodal vision ingredient detection
- `POST /api/scan/meal` — Prepared meal dish scanner & nutrition estimation
- `POST /api/recipes/find` — Recipe matching engine with filters
- `GET /api/recipes/{id}` — Recipe detail, scaling servings, ingredient table
- `POST /api/recipes/{id}/improve` — Meal improvement calculation engine
- `GET /api/pantry` | `POST` | `PUT` | `DELETE` — Pantry inventory CRUD
- `GET /api/nutrition/today` | `POST /api/meals` — Daily macro tracking & meal logging
- `GET /api/shopping-list` | `POST` | `PUT` | `DELETE` — Missing ingredient shopping list
- `POST /api/assistant/ask` — Context-aware AI Kitchen Assistant

---

## ⚠️ Product Disclaimers & Limits

- **Quantities**: Quantities detected from photos are estimates. Confirm them for better nutrition accuracy.
- **Nutrition**: Nutrition values are estimates and vary by brand, preparation, and portion size.
- **Medical Notice**: NutriScan provides general food information and is not a substitute for professional medical or dietary advice.
