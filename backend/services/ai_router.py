"""
Strictly sequential three-provider AI fallback router for NutriScan.

Priority order (exact):
1. OpenRouter (primary)
2. Groq (secondary fallback)
3. Google Gemini (final fallback)

Behavior:
- Validates shared request parameters before starting the fallback chain.
- Calls OpenRouter first. If it returns a valid, usable response, returns immediately.
- If OpenRouter fails, times out, returns an empty response, or returns malformed/unusable data,
  falls back to Groq.
- If Groq also fails, falls back to Google Gemini.
- If all configured providers fail, raises AIProviderError with a sanitized summary.
- Never calls providers concurrently and never logs or exposes API keys.
"""

import base64
import json
import logging
import re
from typing import Any, Callable, Dict, List, Optional, Tuple

import requests

from config import settings

logger = logging.getLogger(__name__)

SUPPORTED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
}

# Models known to be text-only and incompatible with vision/image inputs
TEXT_ONLY_MODELS = {
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama-3.1-70b-versatile",
    "llama3-8b-8192",
    "llama3-70b-8192",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
}


class AIProviderError(Exception):
    """Raised when an AI provider attempt or the full fallback chain fails."""
    pass


class AIRequestValidationError(ValueError):
    """Raised when the caller passes an invalid request before any provider is called."""
    pass


class AIRouter:
    PROVIDER_ORDER = ("openrouter", "groq", "gemini")

    def get_providers(self) -> List[Tuple[str, Callable]]:
        """
        Returns configured providers in strict sequential priority order:
        1. OpenRouter -> 2. Groq -> 3. Google Gemini
        Missing API keys skip only the affected provider.
        """
        providers: List[Tuple[str, Callable]] = []
        if (settings.OPENROUTER_API_KEY or "").strip():
            providers.append(("openrouter", self._call_openrouter))
        if (settings.GROQ_API_KEY or "").strip():
            providers.append(("groq", self._call_groq))
        if (settings.GEMINI_API_KEY or "").strip():
            providers.append(("gemini", self._call_gemini))
        return providers

    @property
    def active(self) -> bool:
        return bool(self.get_providers())

    @property
    def providers(self) -> List[Tuple[str, Callable]]:
        return self.get_providers()

    @property
    def configured_models(self) -> Dict[str, str]:
        return {
            "openrouter": settings.OPENROUTER_MODEL,
            "groq": settings.GROQ_MODEL,
            "gemini": settings.GEMINI_MODEL,
        }

    @property
    def configured_vision_models(self) -> Dict[str, str]:
        return {
            "openrouter": getattr(settings, "OPENROUTER_VISION_MODEL", settings.OPENROUTER_MODEL) or settings.OPENROUTER_MODEL,
            "groq": getattr(settings, "GROQ_VISION_MODEL", settings.GROQ_MODEL) or settings.GROQ_MODEL,
            "gemini": getattr(settings, "GEMINI_VISION_MODEL", settings.GEMINI_MODEL) or settings.GEMINI_MODEL,
        }

    def _resolve_model(self, provider_name: str, is_image: bool = False) -> str:
        if is_image:
            model = self.configured_vision_models.get(provider_name, "").strip()
            if not model:
                model = self.configured_models.get(provider_name, "").strip()
            if not model or model.lower() in TEXT_ONLY_MODELS:
                raise AIProviderError(
                    f"Configured model '{model}' for provider '{provider_name}' does not support image recognition."
                )
            return model
        model = self.configured_models.get(provider_name, "").strip()
        if not model:
            raise AIProviderError(f"No model configured for provider '{provider_name}'.")
        return model

    @staticmethod
    def _sanitize_error(err: Any) -> str:
        """Remove any API keys or bearer tokens from error messages before logging or returning."""
        msg = str(err or "Unknown error")
        for secret in (
            getattr(settings, "OPENROUTER_API_KEY", ""),
            getattr(settings, "GROQ_API_KEY", ""),
            getattr(settings, "GEMINI_API_KEY", ""),
        ):
            secret_clean = (secret or "").strip()
            if secret_clean and secret_clean in msg:
                msg = msg.replace(secret_clean, "[REDACTED]")

        msg = re.sub(r"sk-or-v1-[A-Za-z0-9_-]+", "[REDACTED]", msg)
        msg = re.sub(r"gsk_[A-Za-z0-9_-]+", "[REDACTED]", msg)
        msg = re.sub(r"AIza[A-Za-z0-9_-]+", "[REDACTED]", msg)
        msg = re.sub(r"AQ\.[A-Za-z0-9_.-]+", "[REDACTED]", msg)
        msg = re.sub(r"Bearer\s+[A-Za-z0-9_.-]+", "Bearer [REDACTED]", msg, flags=re.IGNORECASE)
        msg = re.sub(r"([?&]key=)[A-Za-z0-9_.-]+", r"\1[REDACTED]", msg, flags=re.IGNORECASE)
        return msg

    @staticmethod
    def _validate_request(
        prompt: Any,
        image_bytes: Optional[bytes] = None,
        mime_type: Optional[str] = None,
        is_image: bool = False,
        max_tokens: int = 900,
        temperature: float = 0.2,
    ) -> str:
        """
        Validate shared request parameters before starting the provider fallback chain.
        Raises AIRequestValidationError on invalid shared inputs so we do not waste calls.
        Returns normalized mime_type.
        """
        if not isinstance(prompt, str) or not prompt.strip():
            raise AIRequestValidationError("Prompt must be a non-empty string.")
        if not isinstance(max_tokens, int) or max_tokens <= 0:
            raise AIRequestValidationError("max_tokens must be a positive integer.")
        if not isinstance(temperature, (int, float)) or not (0.0 <= float(temperature) <= 2.0):
            raise AIRequestValidationError("temperature must be between 0.0 and 2.0.")

        normalized_mime = (mime_type or "image/jpeg").strip().lower()
        if is_image:
            if not isinstance(image_bytes, (bytes, bytearray)) or len(image_bytes) == 0:
                raise AIRequestValidationError("image_bytes must be non-empty bytes for image requests.")
            if normalized_mime not in SUPPORTED_IMAGE_MIME_TYPES:
                raise AIRequestValidationError(
                    f"Unsupported image mime_type '{mime_type}'. Supported: {sorted(SUPPORTED_IMAGE_MIME_TYPES)}"
                )
            if normalized_mime == "image/jpg":
                normalized_mime = "image/jpeg"
        return normalized_mime

    def _headers(self, key: str, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        h = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        if extra:
            h.update(extra)
        return h

    @staticmethod
    def _parse_json(text: str) -> Any:
        text = (text or "").strip()
        if not text:
            raise json.JSONDecodeError("Empty response text", "", 0)
        # Strip reasoning <think>...</think> blocks if present
        cleaned_think = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
        if cleaned_think:
            text = cleaned_think
        if "```json" in text:
            text = text.split("```json", 1)[1].split("```", 1)[0].strip()
        elif "```" in text:
            text = text.split("```", 1)[1].split("```", 1)[0].strip()

        def _try_load(candidate: str) -> Any:
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                cleaned = re.sub(r",\s*([}\]])", r"\1", candidate)
                return json.loads(cleaned)

        try:
            return _try_load(text)
        except json.JSONDecodeError:
            match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
            if match:
                return _try_load(match.group(1))
            raise

    @staticmethod
    def _openai_messages(
        prompt: str,
        system: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        mime_type: str = "image/jpeg",
    ) -> List[Dict[str, Any]]:
        if image_bytes is not None:
            data_url = f"data:{mime_type};base64,{base64.b64encode(bytes(image_bytes)).decode('utf-8')}"
            content: Any = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": data_url}},
            ]
        else:
            content = prompt

        messages: List[Dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": content})
        return messages

    @staticmethod
    def _extract_openai_text(data: Any, provider_label: str) -> str:
        if not isinstance(data, dict):
            raise AIProviderError(f"{provider_label} returned a non-JSON-object payload.")
        if "error" in data and data["error"]:
            raise AIProviderError(f"{provider_label} error payload: {data['error']}")
        choices = data.get("choices")
        if not isinstance(choices, list) or not choices:
            raise AIProviderError(f"{provider_label} returned no choices.")
        first = choices[0] if isinstance(choices[0], dict) else {}
        message = first.get("message") if isinstance(first.get("message"), dict) else {}
        content = message.get("content")
        if isinstance(content, list):
            content = "".join(
                part.get("text", "") for part in content if isinstance(part, dict)
            )
        if not isinstance(content, str) or not content.strip():
            raise AIProviderError(f"{provider_label} returned an empty message content.")
        cleaned = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
        return cleaned if cleaned else content.strip()

    @staticmethod
    def _check_http_response(response: requests.Response, provider_label: str) -> Dict[str, Any]:
        status = getattr(response, "status_code", None)
        ok = getattr(response, "ok", status is not None and 200 <= status < 300)
        if not ok:
            reason = f"HTTP {status}"
            if status in (401, 403):
                reason = f"Authentication/authorization error (HTTP {status})"
            elif status == 429:
                reason = "Rate limit or quota exceeded (HTTP 429)"
            elif status is not None and status >= 500:
                reason = f"Provider server outage (HTTP {status})"
            body_preview = (getattr(response, "text", "") or "")[:300]
            raise AIProviderError(f"{provider_label} {reason}: {body_preview}")

        try:
            data = response.json()
        except Exception as exc:
            raise AIProviderError(f"{provider_label} returned invalid JSON response: {exc}") from exc
        return data

    def _call_openrouter(
        self,
        prompt: str,
        system: Optional[str],
        image_bytes: Optional[bytes],
        mime_type: str,
        max_tokens: int,
        temperature: float,
        require_json: bool = False,
    ) -> Tuple[str, str]:
        is_image = image_bytes is not None
        model = self._resolve_model("openrouter", is_image=is_image)
        messages = self._openai_messages(prompt, system=system, image_bytes=image_bytes, mime_type=mime_type)
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
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=settings.AI_TIMEOUT_SECONDS,
        )
        data = self._check_http_response(r, "OpenRouter")
        return self._extract_openai_text(data, "OpenRouter"), model

    def _call_groq(
        self,
        prompt: str,
        system: Optional[str],
        image_bytes: Optional[bytes],
        mime_type: str,
        max_tokens: int,
        temperature: float,
        require_json: bool = False,
    ) -> Tuple[str, str]:
        is_image = image_bytes is not None
        model = self._resolve_model("groq", is_image=is_image)
        messages = self._openai_messages(prompt, system=system, image_bytes=image_bytes, mime_type=mime_type)
        groq_max_tokens = min(max_tokens, 1200)
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=self._headers(settings.GROQ_API_KEY),
            json={
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": groq_max_tokens,
            },
            timeout=settings.AI_TIMEOUT_SECONDS,
        )
        data = self._check_http_response(r, "Groq")
        return self._extract_openai_text(data, "Groq"), model

    def _call_gemini(
        self,
        prompt: str,
        system: Optional[str],
        image_bytes: Optional[bytes],
        mime_type: str,
        max_tokens: int,
        temperature: float,
        require_json: bool = False,
    ) -> Tuple[str, str]:
        is_image = image_bytes is not None
        model = self._resolve_model("gemini", is_image=is_image)

        parts: List[Dict[str, Any]] = []
        if image_bytes is not None:
            parts.append(
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": base64.b64encode(bytes(image_bytes)).decode("utf-8"),
                    }
                }
            )
        parts.append({"text": prompt})

        gen_config: Dict[str, Any] = {
            "temperature": temperature,
            "maxOutputTokens": max(max_tokens, 2048) if require_json else max_tokens,
        }
        if require_json:
            gen_config["responseMimeType"] = "application/json"

        payload: Dict[str, Any] = {
            "contents": [{"role": "user", "parts": parts}],
            "generationConfig": gen_config,
        }
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        r = requests.post(
            url,
            headers={
                "x-goog-api-key": settings.GEMINI_API_KEY,
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=settings.AI_TIMEOUT_SECONDS,
        )
        data = self._check_http_response(r, "Gemini")
        if not isinstance(data, dict):
            raise AIProviderError("Gemini returned a non-JSON-object payload.")
        if "error" in data and data["error"]:
            raise AIProviderError(f"Gemini error payload: {data['error']}")

        candidates = data.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            raise AIProviderError("Gemini returned no candidates.")
        first = candidates[0] if isinstance(candidates[0], dict) else {}
        content = first.get("content") if isinstance(first.get("content"), dict) else {}
        resp_parts = content.get("parts") if isinstance(content.get("parts"), list) else []
        text = "".join(
            p.get("text", "") for p in resp_parts if isinstance(p, dict)
        ).strip()
        if not text:
            raise AIProviderError("Gemini returned an empty candidate text.")
        return text, model

    def _execute_with_fallback(
        self,
        prompt: str,
        system: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        mime_type: str = "image/jpeg",
        max_tokens: int = 900,
        temperature: float = 0.2,
        require_json: bool = False,
        validator: Optional[Callable[[Any], bool]] = None,
    ) -> Dict[str, Any]:
        """
        Centralized strictly sequential fallback executor:
        OpenRouter -> Groq -> Gemini.
        """
        is_image = image_bytes is not None
        normalized_mime = self._validate_request(
            prompt=prompt,
            image_bytes=image_bytes,
            mime_type=mime_type,
            is_image=is_image,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        active_providers = self.get_providers()
        if not active_providers:
            raise AIProviderError(
                "No AI API keys configured. Please set OPENROUTER_API_KEY, GROQ_API_KEY, "
                "or GEMINI_API_KEY in backend environment variables."
            )

        errors: List[str] = []
        for idx, (provider_name, provider_fn) in enumerate(active_providers):
            try:
                raw_text, model_used = provider_fn(
                    prompt=prompt,
                    system=system,
                    image_bytes=image_bytes,
                    mime_type=normalized_mime,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    require_json=require_json,
                )
                if not isinstance(raw_text, str) or not raw_text.strip():
                    raise AIProviderError(f"{provider_name} returned an empty response.")

                parsed_json = None
                if require_json:
                    try:
                        parsed_json = self._parse_json(raw_text)
                    except Exception as parse_exc:
                        raise AIProviderError(
                            f"{provider_name} returned malformed JSON: {parse_exc}"
                        ) from parse_exc
                    if parsed_json is None or (isinstance(parsed_json, (dict, list)) and len(parsed_json) == 0):
                        raise AIProviderError(f"{provider_name} returned empty JSON data.")

                target_for_validation = parsed_json if require_json else raw_text
                if validator is not None:
                    is_valid = validator(target_for_validation)
                    if not is_valid:
                        raise AIProviderError(
                            f"{provider_name} response did not pass schema validation."
                        )

                logger.info("AI request succeeded via provider '%s' (model=%s)", provider_name, model_used)
                result: Dict[str, Any] = {
                    "text": raw_text.strip(),
                    "provider": provider_name,
                    "model": model_used,
                    "is_fallback": idx > 0,
                }
                if require_json:
                    result["json"] = parsed_json
                return result

            except AIRequestValidationError:
                raise
            except requests.Timeout as exc:
                sanitized = self._sanitize_error(exc)
                logger.warning("AI provider '%s' timed out: %s", provider_name, sanitized)
                errors.append(f"{provider_name}: timeout ({sanitized})")
            except requests.RequestException as exc:
                sanitized = self._sanitize_error(exc)
                logger.warning("AI provider '%s' network/HTTP error: %s", provider_name, sanitized)
                errors.append(f"{provider_name}: network error ({sanitized})")
            except Exception as exc:
                sanitized = self._sanitize_error(exc)
                logger.warning("AI provider '%s' failed: %s", provider_name, sanitized)
                errors.append(f"{provider_name}: {sanitized}")

        attempted = ", ".join(name for name, _ in active_providers)
        details = "; ".join(errors)
        raise AIProviderError(
            f"All configured AI providers failed ({attempted}). Details: {details}"
        )

    def text(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 900,
        temperature: float = 0.2,
        validator: Optional[Callable[[str], bool]] = None,
    ) -> Dict[str, Any]:
        return self._execute_with_fallback(
            prompt=prompt,
            system=system,
            image_bytes=None,
            max_tokens=max_tokens,
            temperature=temperature,
            require_json=False,
            validator=validator,
        )

    def json_text(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 1200,
        temperature: float = 0.2,
        validator: Optional[Callable[[Any], bool]] = None,
    ) -> Dict[str, Any]:
        return self._execute_with_fallback(
            prompt=prompt,
            system=system,
            image_bytes=None,
            max_tokens=max_tokens,
            temperature=temperature,
            require_json=True,
            validator=validator,
        )

    def image(
        self,
        image_bytes: bytes,
        mime_type: str,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 900,
        temperature: float = 0.1,
        require_json: bool = False,
        validator: Optional[Callable[[Any], bool]] = None,
    ) -> Dict[str, Any]:
        return self._execute_with_fallback(
            prompt=prompt,
            system=system,
            image_bytes=image_bytes,
            mime_type=mime_type,
            max_tokens=max_tokens,
            temperature=temperature,
            require_json=require_json,
            validator=validator,
        )

    def json_image(
        self,
        image_bytes: bytes,
        mime_type: str,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 900,
        temperature: float = 0.1,
        validator: Optional[Callable[[Any], bool]] = None,
    ) -> Dict[str, Any]:
        return self.image(
            image_bytes=image_bytes,
            mime_type=mime_type,
            prompt=prompt,
            system=system,
            max_tokens=max_tokens,
            temperature=temperature,
            require_json=True,
            validator=validator,
        )


ai_router = AIRouter()
