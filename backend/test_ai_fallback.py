import base64
import io
import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
from fastapi.testclient import TestClient

from config import settings
from main import app
from services.ai_router import AIRouter, AIProviderError, AIRequestValidationError, ai_router
from services.vision_service import vision_service


def _mock_http_response(status_code=200, json_data=None, text=""):
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status_code
    resp.ok = 200 <= status_code < 300
    resp.text = text or (json.dumps(json_data) if json_data is not None else "")
    if json_data is not None:
        resp.json.return_value = json_data
    else:
        resp.json.side_effect = ValueError("No JSON body")
    return resp


def _openai_payload(content_text: str):
    return {"choices": [{"message": {"content": content_text}}]}


def _gemini_payload(content_text: str):
    return {"candidates": [{"content": {"parts": [{"text": content_text}]}}]}


class TestSequentialAIFallback(unittest.TestCase):
    def setUp(self):
        self.router = AIRouter()
        self.orig_keys = (
            settings.OPENROUTER_API_KEY,
            settings.GROQ_API_KEY,
            settings.GEMINI_API_KEY,
        )
        self.orig_models = (
            settings.OPENROUTER_MODEL,
            settings.OPENROUTER_VISION_MODEL,
            settings.GROQ_MODEL,
            settings.GROQ_VISION_MODEL,
            settings.GEMINI_MODEL,
            settings.GEMINI_VISION_MODEL,
        )
        settings.OPENROUTER_API_KEY = "sk-or-v1-testopenrouterkey12345"
        settings.GROQ_API_KEY = "gsk_testgroqkey12345"
        settings.GEMINI_API_KEY = "AIzaTestGeminiKey12345"
        settings.OPENROUTER_MODEL = "google/gemma-4-26b-a4b-it:free"
        settings.OPENROUTER_VISION_MODEL = "google/gemma-4-26b-a4b-it:free"
        settings.GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
        settings.GROQ_VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
        settings.GEMINI_MODEL = "gemini-2.5-flash"
        settings.GEMINI_VISION_MODEL = "gemini-2.5-flash"

    def tearDown(self):
        (
            settings.OPENROUTER_API_KEY,
            settings.GROQ_API_KEY,
            settings.GEMINI_API_KEY,
        ) = self.orig_keys
        (
            settings.OPENROUTER_MODEL,
            settings.OPENROUTER_VISION_MODEL,
            settings.GROQ_MODEL,
            settings.GROQ_VISION_MODEL,
            settings.GEMINI_MODEL,
            settings.GEMINI_VISION_MODEL,
        ) = self.orig_models

    def test_provider_priority_order(self):
        """Verify exact provider priority order: OpenRouter -> Groq -> Gemini."""
        names = [name for name, _ in self.router.get_providers()]
        self.assertEqual(names, ["openrouter", "groq", "gemini"])

    @patch("services.ai_router.requests.post")
    def test_1_openrouter_succeeds_only_openrouter_called(self, mock_post):
        """1. OpenRouter succeeds: only OpenRouter is called; Groq and Gemini are NOT called."""
        mock_post.return_value = _mock_http_response(
            200, _openai_payload("Use fresh spinach and lemon juice.")
        )

        result = self.router.text("How do I brighten this soup?")

        self.assertEqual(result["provider"], "openrouter")
        self.assertFalse(result["is_fallback"])
        self.assertEqual(result["text"], "Use fresh spinach and lemon juice.")
        self.assertEqual(mock_post.call_count, 1)
        called_url = mock_post.call_args_list[0][0][0]
        self.assertIn("openrouter.ai", called_url)

    @patch("services.ai_router.requests.post")
    def test_2_openrouter_fails_groq_succeeds_gemini_not_called(self, mock_post):
        """2. OpenRouter fails (e.g., 429 rate limit) and Groq succeeds: Gemini is not called."""
        mock_post.side_effect = [
            _mock_http_response(429, {"error": "Rate limit reached"}, text="Rate limit reached"),
            _mock_http_response(200, _openai_payload("Add boiled chickpeas for protein.")),
        ]

        result = self.router.text("How to add protein?")

        self.assertEqual(result["provider"], "groq")
        self.assertTrue(result["is_fallback"])
        self.assertEqual(result["text"], "Add boiled chickpeas for protein.")
        self.assertEqual(mock_post.call_count, 2)
        self.assertIn("openrouter.ai", mock_post.call_args_list[0][0][0])
        self.assertIn("api.groq.com", mock_post.call_args_list[1][0][0])

    @patch("services.ai_router.requests.post")
    def test_3_openrouter_and_groq_fail_gemini_succeeds(self, mock_post):
        """3. OpenRouter and Groq fail and Gemini succeeds in exact sequential order."""
        mock_post.side_effect = [
            requests.Timeout("OpenRouter timed out"),
            _mock_http_response(503, text="Groq service outage"),
            _mock_http_response(200, _gemini_payload("Roast garlic for deeper flavor.")),
        ]

        result = self.router.text("Any flavor tips?", system="You are a chef.")

        self.assertEqual(result["provider"], "gemini")
        self.assertTrue(result["is_fallback"])
        self.assertEqual(result["text"], "Roast garlic for deeper flavor.")
        self.assertEqual(mock_post.call_count, 3)
        self.assertIn("openrouter.ai", mock_post.call_args_list[0][0][0])
        self.assertIn("api.groq.com", mock_post.call_args_list[1][0][0])
        self.assertIn("generativelanguage.googleapis.com", mock_post.call_args_list[2][0][0])

    @patch("services.ai_router.requests.post")
    def test_4_all_three_fail_returns_clear_sanitized_error(self, mock_post):
        """4. All three fail: raises a clear error indicating all three failed without leaking keys."""
        mock_post.side_effect = [
            _mock_http_response(
                401,
                text=f"Invalid key {settings.OPENROUTER_API_KEY}",
            ),
            _mock_http_response(
                429,
                text=f"Quota exceeded for {settings.GROQ_API_KEY}",
            ),
            _mock_http_response(
                500,
                text=f"Gemini internal error with key {settings.GEMINI_API_KEY}",
            ),
        ]

        with self.assertRaises(AIProviderError) as ctx:
            self.router.text("Test all failing")

        err_msg = str(ctx.exception)
        self.assertIn("All configured AI providers failed (openrouter, groq, gemini)", err_msg)
        self.assertNotIn(settings.OPENROUTER_API_KEY, err_msg)
        self.assertNotIn(settings.GROQ_API_KEY, err_msg)
        self.assertNotIn(settings.GEMINI_API_KEY, err_msg)
        self.assertIn("[REDACTED]", err_msg)
        self.assertEqual(mock_post.call_count, 3)

    @patch("services.ai_router.requests.post")
    def test_5_empty_and_malformed_responses_trigger_fallback(self, mock_post):
        """5. Empty responses, malformed JSON, and schema-invalid JSON trigger fallback."""
        valid_recipe_json = json.dumps({
            "name": "Gemini Emerald Spinach Bowl",
            "description": "Healthy spinach & paneer bowl",
            "prep_time": 10,
            "cook_time": 15,
            "servings": 2,
            "difficulty": "Easy",
            "estimated_cost": 110.0,
            "tags": ["AI Created", "Healthy"],
            "ingredients": [{"ingredient": "spinach", "quantity": 150, "unit": "g"}],
            "steps": ["Wash spinach", "Saute with garlic"],
            "substitutions": [],
        })

        # OpenRouter returns empty string -> Groq returns malformed JSON -> Gemini returns valid JSON
        mock_post.side_effect = [
            _mock_http_response(200, _openai_payload("   ")),
            _mock_http_response(200, _openai_payload("{not valid json:")),
            _mock_http_response(200, _gemini_payload(valid_recipe_json)),
        ]

        result = self.router.json_text(
            "Generate recipe JSON",
            validator=lambda d: isinstance(d, dict) and "name" in d and "steps" in d,
        )
        self.assertEqual(result["provider"], "gemini")
        self.assertEqual(result["json"]["name"], "Gemini Emerald Spinach Bowl")
        self.assertEqual(mock_post.call_count, 3)

    @patch("services.ai_router.requests.post")
    def test_6_image_recognition_payloads_and_vision_model_compatibility(self, mock_post):
        """6. Image recognition formats payloads per provider and skips incompatible text-only models."""
        fake_image = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        expected_b64 = base64.b64encode(fake_image).decode("utf-8")

        # Configure Groq with a text-only model so it is treated as unavailable for vision
        settings.GROQ_VISION_MODEL = "llama-3.3-70b-versatile"

        gemini_vision_json = json.dumps({
            "ingredients": [
                {"name": "tomato", "estimated_quantity": 3, "unit": "pcs", "confidence": 0.96}
            ]
        })

        # OpenRouter returns unusable JSON (empty ingredients list), Groq is skipped due to text-only model,
        # Gemini succeeds with proper inline_data image format.
        mock_post.side_effect = [
            _mock_http_response(200, _openai_payload(json.dumps({"ingredients": []}))),
            _mock_http_response(200, _gemini_payload(gemini_vision_json)),
        ]

        scan_res = unittest.IsolatedAsyncioTestCase()
        import asyncio
        result = asyncio.run(
            vision_service.scan_ingredients(fake_image, "tomatoes.jpg", mime_type="image/jpeg")
        )

        self.assertFalse(result["is_demo"])
        self.assertIn("gemini", result["provider"])
        self.assertEqual(len(result["ingredients"]), 1)
        self.assertEqual(result["ingredients"][0]["name"], "tomato")

        # Verify OpenRouter was called first with OpenAI data URL format,
        # Groq was skipped without making a network request because its model was text-only,
        # and Gemini was called with inline_data format.
        self.assertEqual(mock_post.call_count, 2)

        openrouter_body = mock_post.call_args_list[0][1]["json"]
        user_content = openrouter_body["messages"][-1]["content"]
        self.assertEqual(user_content[1]["type"], "image_url")
        self.assertEqual(
            user_content[1]["image_url"]["url"],
            f"data:image/jpeg;base64,{expected_b64}",
        )

        gemini_body = mock_post.call_args_list[1][1]["json"]
        gemini_parts = gemini_body["contents"][0]["parts"]
        self.assertEqual(gemini_parts[0]["inline_data"]["mime_type"], "image/jpeg")
        self.assertEqual(gemini_parts[0]["inline_data"]["data"], expected_b64)

    @patch("services.ai_router.requests.post")
    def test_7_missing_api_keys_skip_only_affected_provider(self, mock_post):
        """7. Missing API keys skip only the affected provider and continue to the next configured provider."""
        # Case A: OpenRouter key missing -> starts directly with Groq
        settings.OPENROUTER_API_KEY = ""
        mock_post.return_value = _mock_http_response(
            200, _openai_payload("Groq handled request directly.")
        )

        res_a = self.router.text("Quick tip")
        self.assertEqual(res_a["provider"], "groq")
        self.assertFalse(res_a["is_fallback"])
        self.assertEqual(mock_post.call_count, 1)
        self.assertIn("api.groq.com", mock_post.call_args_list[0][0][0])

        # Case B: Groq key missing, OpenRouter fails -> skips Groq and calls Gemini
        mock_post.reset_mock()
        settings.OPENROUTER_API_KEY = "sk-or-v1-testopenrouterkey12345"
        settings.GROQ_API_KEY = ""
        mock_post.side_effect = [
            _mock_http_response(500, text="OpenRouter down"),
            _mock_http_response(200, _gemini_payload("Gemini handled fallback.")),
        ]

        res_b = self.router.text("Quick tip")
        self.assertEqual(res_b["provider"], "gemini")
        self.assertTrue(res_b["is_fallback"])
        self.assertEqual(mock_post.call_count, 2)
        self.assertIn("openrouter.ai", mock_post.call_args_list[0][0][0])
        self.assertIn("generativelanguage.googleapis.com", mock_post.call_args_list[1][0][0])

    @patch("services.ai_router.requests.post")
    def test_8_request_validation_prevents_wasted_fallback_calls(self, mock_post):
        """8. Permanent shared request errors fail immediately before calling any provider."""
        with self.assertRaises(AIRequestValidationError):
            self.router.text("   ")

        with self.assertRaises(AIRequestValidationError):
            self.router.image(b"", "image/jpeg", "Scan this")

        with self.assertRaises(AIRequestValidationError):
            self.router.image(b"123", "application/pdf", "Scan this")

        self.assertEqual(mock_post.call_count, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
