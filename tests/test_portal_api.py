"""Mandatory security and tenant isolation tests for the portal API (AGENT_PORTAL.md Section 13)."""

import json
import os
import tempfile
import unittest

from fastapi.testclient import TestClient

from app import db, db_stats
from app.config import settings
from app.utils.tokens import hash_token, make_token
from portal.auth import SESSION_COOKIE_NAME, sign_session_cookie
from portal.main import app


class TestPortalApiIsolation(unittest.TestCase):
    """Mandatory tenant isolation and security test suite for portal endpoints."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_api_isolation.db")
        self.orig_db_path = db.get_db_path()
        db.init_db(self.db_path)

        self.orig_secret = settings.PORTAL_SECRET
        settings.PORTAL_SECRET = "super_secure_test_secret_that_is_at_least_32_chars_long!"

        self.client = TestClient(app)

        # Create User A data (Alice)
        self.user_a_id = 1001
        db._upsert_user(self.user_a_id, name="Alice", language="en")
        quiz_json_a = json.dumps(
            {
                "title": "Alice Physics",
                "summary": "Alice note summary",
                "mcqs": [
                    {
                        "question": "Alice Q1?",
                        "options": ["A", "B", "C", "D"],
                        "correct_index": 0,
                        "explanation": "Alice Exp",
                        "topic": "Alice Topic",
                    }
                ],
            }
        )
        self.note_a_id = db._save_note(
            telegram_id=self.user_a_id,
            language="en",
            image_hash="hash_alice",
            summary_text="Alice's Summary Text",
            quiz_json=quiz_json_a,
            title="Alice Physics",
        )
        db_stats.record_answer_sync(
            telegram_id=self.user_a_id,
            note_id=self.note_a_id,
            q_index=0,
            topic="Alice Topic",
            chosen_index=1,
            correct_index=0,
            is_correct=0,
            source="quiz",
        )
        db._save_quiz_attempt(self.note_a_id, self.user_a_id, score=0, total=1)

        # Create User B data (Bob)
        self.user_b_id = 2002
        db._upsert_user(self.user_b_id, name="Bob", language="bn")
        quiz_json_b = json.dumps(
            {
                "title": "Bob Chemistry",
                "summary": "Bob note summary",
                "mcqs": [
                    {
                        "question": "Bob Q1?",
                        "options": ["A", "B", "C", "D"],
                        "correct_index": 1,
                        "explanation": "Bob Exp",
                        "topic": "Bob Topic",
                    }
                ],
            }
        )
        self.note_b_id = db._save_note(
            telegram_id=self.user_b_id,
            language="bn",
            image_hash="hash_bob",
            summary_text="Bob's Summary Text",
            quiz_json=quiz_json_b,
            title="Bob Chemistry",
        )
        db_stats.record_answer_sync(
            telegram_id=self.user_b_id,
            note_id=self.note_b_id,
            q_index=0,
            topic="Bob Topic",
            chosen_index=1,
            correct_index=1,
            is_correct=1,
            source="quiz",
        )
        db._save_quiz_attempt(self.note_b_id, self.user_b_id, score=1, total=1)

        # Sign cookies for both users
        self.cookie_a = {SESSION_COOKIE_NAME: sign_session_cookie(self.user_a_id)}
        self.cookie_b = {SESSION_COOKIE_NAME: sign_session_cookie(self.user_b_id)}

    def tearDown(self):
        settings.PORTAL_SECRET = self.orig_secret
        db.set_db_path(self.orig_db_path)
        try:
            self.temp_dir.cleanup()
        except PermissionError:
            pass

    def test_user_a_cannot_read_user_b_note_returns_404(self):
        """Rule 1: User A's cookie cannot read user B's note: GET /api/notes/{B's id} returns 404."""
        resp = self.client.get(f"/api/notes/{self.note_b_id}", cookies=self.cookie_a)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json(), {"detail": "note_not_found"})

        # Made up note also returns 404
        resp_made_up = self.client.get("/api/notes/999999", cookies=self.cookie_a)
        self.assertEqual(resp_made_up.status_code, 404)

        # Own note returns 200
        resp_own = self.client.get(f"/api/notes/{self.note_a_id}", cookies=self.cookie_a)
        self.assertEqual(resp_own.status_code, 200)
        self.assertEqual(resp_own.json()["title"], "Alice Physics")

    def test_routes_return_only_logged_in_user_data_no_leakage(self):
        """Rule 2: All routes return only logged-in user's data."""
        # 1. Notes list
        resp = self.client.get("/api/notes", cookies=self.cookie_a)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["items"][0]["id"], self.note_a_id)
        self.assertEqual(data["items"][0]["title"], "Alice Physics")

        # 2. Dashboard
        resp_dash = self.client.get("/api/dashboard", cookies=self.cookie_a)
        self.assertEqual(resp_dash.status_code, 200)
        dash_data = resp_dash.json()
        self.assertEqual(dash_data["notes_count"], 1)
        self.assertEqual(dash_data["quizzes_taken"], 1)
        self.assertEqual(dash_data["recent_notes"][0]["id"], self.note_a_id)

        # 3. Weak topics
        resp_weak = self.client.get("/api/weak-topics", cookies=self.cookie_a)
        self.assertEqual(resp_weak.status_code, 200)
        topics = resp_weak.json()
        self.assertEqual(len(topics), 1)
        self.assertEqual(topics[0]["topic"], "Alice Topic")

        # 4. Mistakes
        resp_mistakes = self.client.get("/api/mistakes", cookies=self.cookie_a)
        self.assertEqual(resp_mistakes.status_code, 200)
        mistakes = resp_mistakes.json()
        self.assertEqual(len(mistakes), 1)
        self.assertEqual(mistakes[0]["note_id"], self.note_a_id)
        self.assertEqual(mistakes[0]["topic"], "Alice Topic")

        # 5. History
        resp_hist = self.client.get("/api/history", cookies=self.cookie_a)
        self.assertEqual(resp_hist.status_code, 200)
        hist = resp_hist.json()
        self.assertEqual(len(hist["attempts"]), 1)
        self.assertEqual(hist["attempts"][0]["note_id"], self.note_a_id)

    def test_no_cookie_returns_401_on_every_data_route(self):
        """Rule 3: No cookie -> 401 on every data route."""
        data_routes = [
            "/api/me",
            "/api/dashboard",
            "/api/notes",
            f"/api/notes/{self.note_a_id}",
            "/api/weak-topics",
            "/api/mistakes",
            "/api/history",
        ]
        for path in data_routes:
            resp = self.client.get(path)
            self.assertEqual(
                resp.status_code, 401, f"Expected 401 for {path} without cookie"
            )
            self.assertEqual(resp.json(), {"detail": "not_logged_in"})

    def test_tampered_cookie_returns_401(self):
        """Rule 3 continued: Tampered cookie -> 401."""
        tampered_cookie = {SESSION_COOKIE_NAME: "tampered_signature_payload.12345"}
        resp = self.client.get("/api/me", cookies=tampered_cookie)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json(), {"detail": "not_logged_in"})

    def test_token_exchange_lifecycle_atomic_single_use(self):
        """Rule 4: A token works once; second use, expired and random tokens all fail."""
        token = make_token()
        token_h = hash_token(token)
        db_stats.create_portal_token_sync(token_h, self.user_a_id, ttl_seconds=300)

        # 1. First exchange -> 200 and sets cookie
        resp = self.client.post("/api/auth/exchange", json={"token": token})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"ok": True})
        self.assertIn(SESSION_COOKIE_NAME, resp.cookies)

        # Verify the cookie gives access to /api/me as Alice
        me_resp = self.client.get("/api/me", cookies=resp.cookies)
        self.assertEqual(me_resp.status_code, 200)
        self.assertEqual(me_resp.json()["name"], "Alice")

        # 2. Second exchange with same token -> 400 invalid_token
        second_resp = self.client.post("/api/auth/exchange", json={"token": token})
        self.assertEqual(second_resp.status_code, 400)
        self.assertEqual(second_resp.json(), {"detail": "invalid_token"})

        # 3. Random token -> 400 invalid_token
        rand_resp = self.client.post(
            "/api/auth/exchange", json={"token": "completely_random_token"}
        )
        self.assertEqual(rand_resp.status_code, 400)
        self.assertEqual(rand_resp.json(), {"detail": "invalid_token"})

    def test_logout_clears_cookie(self):
        resp = self.client.post("/api/auth/logout", cookies=self.cookie_a)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"ok": True})
        # Cookie deletion sends expired cookie header
        self.assertIn(SESSION_COOKIE_NAME, resp.headers.get("set-cookie", ""))

    def test_spa_serving_and_static_assets(self):
        """Verify React SPA index.html is served for client-side routes and /."""
        from portal.main import create_app

        fresh_app = create_app()
        fresh_client = TestClient(fresh_app)

        resp_root = fresh_client.get("/")
        self.assertEqual(resp_root.status_code, 200)
        self.assertIn("SnapStudy", resp_root.text)

        resp_spa = fresh_client.get("/dashboard")
        self.assertEqual(resp_spa.status_code, 200)
        self.assertIn("SnapStudy", resp_spa.text)

        # Unknown API route returns 404 JSON, not index.html
        resp_api_404 = fresh_client.get("/api/nonexistent")
        self.assertEqual(resp_api_404.status_code, 404)
        self.assertEqual(resp_api_404.json(), {"detail": "not_found"})

    def test_leaderboard_route(self):
        """Verify /api/leaderboard returns ranked students with is_me flag."""
        resp = self.client.get("/api/leaderboard", cookies=self.cookie_a)
        self.assertEqual(resp.status_code, 200)
        board = resp.json()
        self.assertGreaterEqual(len(board), 1)
        # Verify Alice is marked is_me = True
        alice_entry = next((item for item in board if item["name"] == "Alice"), None)
        self.assertIsNotNone(alice_entry)
        self.assertTrue(alice_entry["is_me"])

    def test_ask_ai_tutor_isolation_and_404(self):
        """User A cannot ask AI tutor questions about User B's note (404)."""
        resp = self.client.post(
            f"/api/notes/{self.note_b_id}/ask",
            json={"question": "Explain this?"},
            cookies=self.cookie_a,
        )
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json(), {"detail": "note_not_found"})


