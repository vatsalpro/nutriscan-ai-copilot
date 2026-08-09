# NutriScan — Three AI failover setup (no Gemini)

NutriScan now uses this failover order:

1. **Groq — Meta Llama 4 Scout**
   `meta-llama/llama-4-scout-17b-16e-instruct`
2. **OpenRouter — Google Gemma 4 26B A4B free**
   `google/gemma-4-26b-a4b-it:free`
3. **OpenRouter Free Models Router**
   `openrouter/free`

If #1 fails, the same request is sent to #2. If #2 fails, it is sent to #3.
The OpenRouter free router chooses from currently available free models and filters for capabilities needed by the request, including image understanding when the request contains an image.

## Vercel environment variables

```env
GROQ_API_KEY=your_groq_key
GROQ_MODEL=meta-llama/llama-4-scout-17b-16e-instruct

OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_MODEL=google/gemma-4-26b-a4b-it:free
OPENROUTER_FREE_MODEL=openrouter/free
OPENROUTER_SITE_URL=https://nutriscan-ai-copilot.onrender.com
```

Only server-side Vercel environment variables are needed. Do not expose API keys in client-side code.

## Important

Free hosted inference still has rate limits. This architecture improves resilience by using multiple providers/models, but it cannot guarantee unlimited free inference.
