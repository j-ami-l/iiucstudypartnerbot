"""Study service orchestrating image analysis, Gemma LLM calls, and validation."""

import logging
from typing import Optional

from pydantic import ValidationError

from app.ai.gemma_client import GemmaClient
from app.ai.json_utils import extract_json
from app.schemas import StudyResult

logger = logging.getLogger(__name__)


class StudyServiceError(Exception):
    """Base exception for study service errors."""

    pass


class UnreadableNoteError(StudyServiceError):
    """Raised when the submitted image cannot be read or is not study material."""

    pass


class InvalidJSONError(StudyServiceError):
    """Raised when Gemma returns invalid JSON twice consecutively."""

    pass


class StudyService:
    """Service handling note analysis and study material generation."""

    def __init__(self, gemma_client: Optional[GemmaClient] = None):
        self.gemma_client = gemma_client or GemmaClient()

    async def analyze_note(
        self, image_bytes: bytes, language: str = "en"
    ) -> StudyResult:
        """Analyze note image with Gemma, extracting and validating structured study results.

        Retries once if JSON extraction or schema validation fails.

        Args:
            image_bytes: Compressed image bytes.
            language: Target output language ('en' or 'bn').

        Returns:
            Validated StudyResult object.

        Raises:
            UnreadableNoteError: Image marked unreadable by model.
            InvalidJSONError: Model failed to produce valid JSON twice.
            GemmaTimeout: Request timed out.
            GemmaAuthError: Authentication failure.
            GemmaAPIError: Upstream API failure.
        """
        attempts = 2
        last_error: Optional[Exception] = None
        last_raw_text = ""

        for attempt in range(1, attempts + 1):
            logger.info(
                "Analyzing note (attempt %d/%d, lang=%s)", attempt, attempts, language
            )
            raw_text = await self.gemma_client.analyze_note(
                image_bytes, language=language
            )
            last_raw_text = raw_text

            try:
                data = extract_json(raw_text)

                # Check if model detected unreadable / non-study image
                if data.get("error") == "unreadable":
                    logger.info("Gemma classified image as unreadable")
                    raise UnreadableNoteError("Image is unreadable or not study material")

                study_result = StudyResult.model_validate(data)
                return study_result

            except UnreadableNoteError:
                # Do not retry if model explicitly determined image is unreadable
                raise
            except (ValueError, ValidationError) as err:
                last_error = err
                logger.warning(
                    "JSON extraction/validation failed on attempt %d: %s",
                    attempt,
                    err,
                )
                if attempt < attempts:
                    logger.info("Retrying Gemma note analysis...")

        logger.error(
            "Failed to obtain valid StudyResult after %d attempts. Raw text preview: %s",
            attempts,
            last_raw_text[:200],
        )
        raise InvalidJSONError(
            f"Invalid JSON received from Gemma twice: {last_error}"
        ) from last_error
