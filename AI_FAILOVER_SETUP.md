# NutriScan — Sequential Three-Provider AI Failover Setup

NutriScan uses a strictly sequential AI provider fallback system across all AI-powered features (ingredient image recognition, meal nutrition scan, AI recipe generation, and the AI kitchen assistant):

1. **OpenRouter (Primary)**
   - Model: `openrouter/free` (configurable via `OPENROUTER_MODEL` / `OPENROUTER_VISION_MODEL`)
2. **Groq (Secondary Fallback)**
   - Model: `qwen/qwen3.8-27b` (configurable via `GROQ_MODEL` / `GROQ_VISION_MODEL`)
3. **Google Gemini (Final Fallback)**
   - Model: `gemini-3.8-flash` (configurable via `GEMINI_MODEL` / `GEMINI_VISION_MODEL`)

## Failover Behavior

- Every AI request validates shared parameters first, then calls **OpenRouter** first.
- If OpenRouter returns a valid, usable response, NutriScan returns it immediately without calling Groq or Gemini.
- If OpenRouter fails, times out, returns an empty response, or returns malformed/unusable JSON, NutriScan automatically tries **Groq**.
- If Groq also fails, NutriScan tries **Google Gemini**.
- If all configured providers fail, NutriScan logs sanitized provider errors (never exposing API keys) and raises a clear error or falls back gracefully.
- Missing API keys skip only the unconfigured provider and proceed to the next configured provider in order.

## Backend & Vercel Environment Variables

Configure these environment variables on your backend host (e.g., Vercel Project Settings → Environment Variables, Render, or `backend/.env` locally):

```env
# 1) OpenRouter (Primary)
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openrouter/free
OPENROUTER_VISION_MODEL=openrouter/free
OPENROUTER_SITE_URL=https://nutriscan-ai.vercel.app

# 2) Groq (Secondary Fallback)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=qwen/qwen3.8-27b
GROQ_VISION_MODEL=qwen/qwen3.8-27b

# 3) Google Gemini (Final Fallback)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.8-flash
GEMINI_VISION_MODEL=gemini-3.8-flash

# Timeout & Server Settings
AI_TIMEOUT_SECONDS=20
PORT=8000
HOST=0.0.0.0
```

## Security Notice

- Read API keys exclusively from backend environment variables.
- Never expose `OPENROUTER_API_KEY`, `GROQ_API_KEY`, or `GEMINI_API_KEY` in frontend `VITE_*` variables, API responses, browser logs, or Git commits.
