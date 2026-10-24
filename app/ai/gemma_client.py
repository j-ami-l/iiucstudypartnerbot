"""Client for communicating with the hosted Gemma model."""

import base64
import logging
import time
from pathlib import Path
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

PROMPT_FILE = Path(__file__).resolve().parent.parent / "prompts" / "study_prompt.md"


class GemmaError(Exception):
    """Base exception for all Gemma client errors."""

    pass


class GemmaTimeout(GemmaError):
    """Raised when the Gemma API request times out."""

    pass


class GemmaAuthError(GemmaError):
    """Raised when authentication with the Gemma API fails (401/403 or missing key)."""

    pass


class GemmaAPIError(GemmaError):
    """Raised when the Gemma API returns an error response."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class GemmaClient:
    """HTTP client for Gemma 4 via OpenAI-compatible endpoints (OpenRouter/custom)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        self.api_key = api_key if api_key is not None else settings.GEMMA_API_KEY
        self.base_url = (
            base_url if base_url is not None else settings.GEMMA_BASE_URL
        ).rstrip("/")
        self.model = model if model is not None else settings.GEMMA_MODEL
        self.timeout = (
            timeout if timeout is not None else settings.REQUEST_TIMEOUT_SECONDS
        )

    def _load_prompt(self, language: str) -> str:
        """Load study prompt from file and substitute target language."""
        if not PROMPT_FILE.exists():
            raise FileNotFoundError(f"Prompt template missing at {PROMPT_FILE}")

        lang_name = "Bangla" if language.lower() in ("bn", "bangla") else "English"
        template = PROMPT_FILE.read_text(encoding="utf-8")
        return template.replace("{language}", lang_name)

    async def analyze_note(self, image_bytes: bytes, language: str = "en") -> str:
        """Send note image and study prompt to Gemma and return raw model response text.

        Args:
            image_bytes: Raw bytes of the image file.
            language: Target language ('en' or 'bn').

        Returns:
            The raw text returned by the model.

        Raises:
            GemmaAuthError: Missing or invalid API key.
            GemmaTimeout: Request exceeded configured timeout.
            GemmaAPIError: Upstream API failure or bad HTTP status.
        """
        if not self.api_key:
            raise GemmaAuthError(
                "GEMMA_API_KEY is not set. Please add it to your .env file."
            )

        prompt_text = self._load_prompt(language)
        b64_image = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:image/jpeg;base64,{b64_image}"

        endpoint = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/j-ami-l/iiucstudypartnerbot",
            "X-Title": "SnapStudy AI",
        }
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {
                            "type": "image_url",
                            "image_url": {"url": data_url},
                        },
                    ],
                }
            ],
            "temperature": 0.2,
        }

        start_time = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(endpoint, headers=headers, json=payload)

            latency = time.perf_counter() - start_time
            logger.info("Gemma API call finished in %.2fs", latency)

            if response.status_code in (401, 403):
                logger.error("Gemma authentication error (HTTP %d)", response.status_code)
                raise GemmaAuthError(
                    f"Authentication failed with status {response.status_code}. Verify GEMMA_API_KEY."
                )

            if response.is_error:
                logger.error(
                    "Gemma API returned HTTP %d: %s",
                    response.status_code,
                    response.text[:300],
                )
                raise GemmaAPIError(
                    f"API returned status {response.status_code}: {response.text[:150]}",
                    status_code=response.status_code,
                )

            data = response.json()
            choices = data.get("choices", [])
            if not choices:
                raise GemmaAPIError("Gemma API response contained no choices")

            content = choices[0].get("message", {}).get("content", "")
            if not content:
                raise GemmaAPIError("Gemma API returned an empty message content")

            return content

        except httpx.TimeoutException as err:
            latency = time.perf_counter() - start_time
            logger.warning("Gemma request timed out after %.2fs", latency)
            raise GemmaTimeout(
                f"Gemma API request timed out after {latency:.2f}s"
            ) from err
        except httpx.RequestError as err:
            latency = time.perf_counter() - start_time
            logger.error("Gemma network request error after %.2fs: %s", latency, err)
            raise GemmaAPIError(f"Network error contacting Gemma API: {err}") from err
