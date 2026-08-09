"""
Three-provider AI failover for NutriScan.

Priority:
1. Groq - meta-llama/llama-4-scout-17b-16e-instruct
2. OpenRouter - google/gemma-4-26b-a4b-it:free
3. OpenRouter Free Models Router - openrouter/free
   Dynamically selects a currently available free model matching the request capabilities.

All providers are optional. If one key is missing, the router skips it.
If a provider errors, the next provider is tried automatically.
"""

import base64
import json
import logging
import re
from typing import Optional

import requests

from config import settings

logger = logging.getLogger(__name__)


class AIProviderError(Exception):
    pass


class AIRouter:
    def __init__(self):
        self.providers = []
        if settings.GROQ_API_KEY:
            self.providers.append(("groq", self._groq))
        if settings.OPENROUTER_API_KEY:
            self.providers.append(("openrouter", self._openrouter))
        if settings.OPENROUTER_API_KEY:
            self.providers.append(("openrouter_free", self._openrouter_free))

        logger.info("AI failover providers configured: %s", [p[0] for p in self.providers])

    @property
    def active(self):
        return bool(self.providers)

    @property
    def configured_models(self):
        return {
            "groq": settings.GROQ_MODEL,
            "openrouter": settings.OPENROUTER_MODEL,
            "openrouter_free": settings.OPENROUTER_FREE_MODEL,
        }

    def _headers(self, key, extra=None):
        h = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        if extra:
            h.update(extra)
        return h

    @staticmethod
    def _parse_json(text):
        text = (text or "").strip()
        if "```json" in text:
            text = text.split("```json", 1)[1].split("```", 1)[0].strip()
        elif "```" in text:
            text = text.split("```", 1)[1].split("```", 1)[0].strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            raise


    def _groq(self, messages, max_tokens, temperature):
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=self._headers(settings.GROQ_API_KEY),
            json={
                "model": settings.GROQ_MODEL,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=settings.AI_TIMEOUT_SECONDS,
        )
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]

    def _openrouter(self, messages, max_tokens, temperature):
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=self._headers(
                settings.OPENROUTER_API_KEY,
                {
                    "HTTP-Referer": settings.OPENROUTER_SITE_URL,
                    "X-Title": "NutriScan AI",
                },
            ),
            json={
                "model": settings.OPENROUTER_MODEL,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=settings.AI_TIMEOUT_SECONDS,
        )
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]

    def _openrouter_free(self, messages, max_tokens, temperature):
        """OpenRouter's free-model router. It filters for capabilities needed by the request."""
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=self._headers(
                settings.OPENROUTER_API_KEY,
                {
                    "HTTP-Referer": settings.OPENROUTER_SITE_URL,
                    "X-Title": "NutriScan AI Free Fallback",
                },
            ),
            json={
                "model": settings.OPENROUTER_FREE_MODEL,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=settings.AI_TIMEOUT_SECONDS,
        )
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]

    def _messages(self, prompt, system=None, image_bytes=None, mime_type="image/jpeg"):
        if image_bytes is not None:
            data_url = f"data:{mime_type};base64,{base64.b64encode(image_bytes).decode('utf-8')}"
            content = [
                {"type": "image_url", "image_url": {"url": data_url}},
                {"type": "text", "text": prompt},
            ]
        else:
            content = prompt

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": content})
        return messages

    def _try_all(self, messages, max_tokens=900, temperature=0.2):
        last_error = None
        for name, fn in self.providers:
            try:
                text = fn(messages, max_tokens, temperature)
                if text:
                    logger.info("AI request succeeded with %s", name)
                    return {
                        "text": text,
                        "provider": name,
                        "model": self.configured_models[name],
                        "is_fallback": name != self.providers[0][0],
                    }
            except Exception as exc:
                last_error = exc
                logger.warning("AI provider %s failed: %s", name, exc)
                continue
        raise AIProviderError(f"All configured AI providers failed. Last error: {last_error}")

    def text(self, prompt, system=None, max_tokens=900, temperature=0.2):
        return self._try_all(
            self._messages(prompt, system=system),
            max_tokens=max_tokens,
            temperature=temperature,
        )

    def image(self, image_bytes, mime_type, prompt, system=None, max_tokens=900, temperature=0.1):
        return self._try_all(
            self._messages(
                prompt,
                system=system,
                image_bytes=image_bytes,
                mime_type=mime_type,
            ),
            max_tokens=max_tokens,
            temperature=temperature,
        )

    def json_text(self, prompt, system=None, max_tokens=1200):
        result = self.text(prompt, system=system, max_tokens=max_tokens, temperature=0.2)
        result["json"] = self._parse_json(result["text"])
        return result


ai_router = AIRouter()
