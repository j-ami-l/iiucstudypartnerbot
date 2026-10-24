"""Unit tests for GemmaClient retry behavior and error handling."""

import unittest
from unittest.mock import AsyncMock, patch
import httpx
from app.ai.gemma_client import GemmaAuthError, GemmaClient, GemmaTimeout


class TestGemmaClientRetry(unittest.IsolatedAsyncioTestCase):
    """Test suite for GemmaClient error handling and retry policy."""

    async def test_transient_retry_success(self):
        client = GemmaClient(api_key="test_key")

        # Mock 429 followed by 200 OK
        mock_response_429 = httpx.Response(
            status_code=429,
            content=b'{"error": "rate limited"}',
            request=httpx.Request("POST", "https://api.test"),
        )
        mock_response_200 = httpx.Response(
            status_code=200,
            json={"choices": [{"message": {"content": '{"summary": "ok"}'}}]},
            request=httpx.Request("POST", "https://api.test"),
        )

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = [mock_response_429, mock_response_200]
            with patch("asyncio.sleep", new_callable=AsyncMock):
                result = await client.analyze_note(b"fake_image_bytes", language="en")
                self.assertEqual(result, '{"summary": "ok"}')
                self.assertEqual(mock_post.call_count, 2)

    async def test_timeout_no_auto_retry(self):
        client = GemmaClient(api_key="test_key")

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = httpx.TimeoutException("Read timed out")
            with self.assertRaises(GemmaTimeout):
                await client.analyze_note(b"fake_image_bytes", language="en")
            # Must NOT retry on timeout (AGENT.md Sec 4.4 Rule 8)
            self.assertEqual(mock_post.call_count, 1)

    async def test_auth_error_no_retry(self):
        client = GemmaClient(api_key="bad_key")

        mock_response_401 = httpx.Response(
            status_code=401,
            content=b'{"error": "Unauthorized"}',
            request=httpx.Request("POST", "https://api.test"),
        )

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response_401
            with self.assertRaises(GemmaAuthError):
                await client.analyze_note(b"fake_image_bytes", language="en")
            self.assertEqual(mock_post.call_count, 1)


if __name__ == "__main__":
    unittest.main()
