# backend/tests/test_donation_routes.py
import unittest
import json
from backend.app import create_app, db
from backend.app.models import User, Donation
from backend.app.utils import auth as real_auth  # To mock its @token_required
from backend.tests.mock_auth import mock_token_required, get_mock_auth_token

# Monkey patch the actual decorator before creating the app or importing routes
real_auth.token_required = mock_token_required


class TestDonationRoutes(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            self._seed_test_users()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _seed_test_users(self):
        user1 = User(username="testuser1", email="test1@example.com")
        user1.set_password("password123")
        user2 = User(username="testuser2", email="test2@example.com")
        user2.set_password("password456")
        db.session.add_all([user1, user2])
        db.session.commit()
        self.user1_id = user1.id
        self.user2_id = user2.id

    def _get_auth_headers(self, user_id):
        return {"Authorization": f"Bearer {get_mock_auth_token(user_id)}"}

    # --- Tests for POST /api/donations ---

    def test_record_donation_success(self):
        with self.app.test_request_context():
            from flask import g

            g.current_user_id = self.user1_id

            payload = {"amount": 50.00, "currency": "USD"}
            response = self.client.post(
                "/api/donations",
                headers=self._get_auth_headers(self.user1_id),
                data=json.dumps(payload),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["amount"], 50.00)
        self.assertEqual(data["currency"], "USD")
        self.assertEqual(data["user_id"], self.user1_id)
        self.assertFalse(data["is_anonymous"])
        self.assertEqual(data["status"], "completed")
        self.assertIsNotNone(data["id"])
        self.assertIsNotNone(data["timestamp"])

        with self.app.app_context():
            donation_in_db = db.session.get(Donation, data["id"])
            self.assertIsNotNone(donation_in_db)
            self.assertEqual(donation_in_db.amount, 50.00)
            self.assertEqual(donation_in_db.user_id, self.user1_id)

    def test_record_donation_anonymous_user(self):
        with self.app.test_request_context():
            from flask import g

            g.current_user_id = self.user2_id

            payload = {"amount": 25.00, "currency": "EUR", "is_anonymous": True}
            response = self.client.post(
                "/api/donations",
                headers=self._get_auth_headers(self.user2_id),
                data=json.dumps(payload),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["amount"], 25.00)
        self.assertEqual(data["currency"], "EUR")
        self.assertEqual(data["user_id"], self.user2_id)
        self.assertTrue(data["is_anonymous"])
        self.assertEqual(data["user_username"], "Anonymous")

        with self.app.app_context():
            donation_in_db = db.session.get(Donation, data["id"])
            self.assertTrue(donation_in_db.is_anonymous)

    def test_record_donation_missing_amount(self):
        with self.app.test_request_context():
            from flask import g

            g.current_user_id = self.user1_id

            payload = {"currency": "USD"}
            response = self.client.post(
                "/api/donations",
                headers=self._get_auth_headers(self.user1_id),
                data=json.dumps(payload),
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("Amount must be a positive number", data["message"])

    def test_record_donation_invalid_amount_zero(self):
        with self.app.test_request_context():
            from flask import g

            g.current_user_id = self.user1_id
            payload = {"amount": 0, "currency": "USD"}
            response = self.client.post(
                "/api/donations",
                headers=self._get_auth_headers(self.user1_id),
                data=json.dumps(payload),
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("Amount must be a positive number", data["message"])

    def test_record_donation_invalid_amount_negative(self):
        with self.app.test_request_context():
            from flask import g

            g.current_user_id = self.user1_id
            payload = {"amount": -10, "currency": "USD"}
            response = self.client.post(
                "/api/donations",
                headers=self._get_auth_headers(self.user1_id),
                data=json.dumps(payload),
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("Amount must be a positive number", data["message"])

    def test_record_donation_missing_currency(self):
        with self.app.test_request_context():
            from flask import g

            g.current_user_id = self.user1_id
            payload = {"amount": 10.0}
            response = self.client.post(
                "/api/donations",
                headers=self._get_auth_headers(self.user1_id),
                data=json.dumps(payload),
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("Currency must be a 3 or 4 letter string", data["message"])

    def test_record_donation_invalid_currency_short(self):
        with self.app.test_request_context():
            from flask import g

            g.current_user_id = self.user1_id
            payload = {"amount": 10.0, "currency": "US"}
            response = self.client.post(
                "/api/donations",
                headers=self._get_auth_headers(self.user1_id),
                data=json.dumps(payload),
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("Currency must be a 3 or 4 letter string", data["message"])

    def test_record_donation_invalid_currency_long(self):
        with self.app.test_request_context():
            from flask import g

            g.current_user_id = self.user1_id
            payload = {"amount": 10.0, "currency": "DOLLARS"}
            response = self.client.post(
                "/api/donations",
                headers=self._get_auth_headers(self.user1_id),
                data=json.dumps(payload),
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("Currency must be a 3 or 4 letter string", data["message"])

    def test_record_donation_invalid_is_anonymous_type(self):
        with self.app.test_request_context():
            from flask import g

            g.current_user_id = self.user1_id
            payload = {
                "amount": 10.0,
                "currency": "USD",
                "is_anonymous": "not-a-boolean",
            }
            response = self.client.post(
                "/api/donations",
                headers=self._get_auth_headers(self.user1_id),
                data=json.dumps(payload),
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("'is_anonymous' must be a boolean", data["message"])

    def test_record_donation_no_auth(self):
        with self.app.test_request_context():
            from flask import g

            g.current_user_id = None  # Explicitly set to None for mock_token_required

            payload = {"amount": 10.00, "currency": "USD"}
            response = self.client.post(
                "/api/donations",
                data=json.dumps(payload),
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn("Token is missing or invalid", data["message"])

    # --- Tests for GET /api/donations/total ---
    def _add_donation(
        self, user_id, amount, currency, is_anonymous=False, status="completed"
    ):
        # This helper is called within an app_context in the tests that use it
        donation = Donation(
            user_id=user_id,
            amount=amount,
            currency=currency,
            is_anonymous=is_anonymous,
            status=status,
        )
        db.session.add(donation)
        db.session.commit()
        return donation

    def test_get_total_donations_no_donations(self):
        response = self.client.get(
            "/api/donations/total"
        )  # This route does not require auth
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["total_donations"], 0.0)

    def test_get_total_donations_with_donations(self):
        with self.app.app_context():  # For DB operations
            self._add_donation(self.user1_id, 10.0, "USD")
            self._add_donation(self.user2_id, 20.5, "EUR")
            self._add_donation(self.user1_id, 5.0, "USD", status="completed")

        response = self.client.get("/api/donations/total")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertAlmostEqual(data["total_donations"], 35.5)

    def test_get_total_donations_only_sums_completed(self):
        with self.app.app_context():  # For DB operations
            self._add_donation(self.user1_id, 100.0, "USD", status="completed")
            self._add_donation(self.user2_id, 50.0, "USD", status="pending")
            self._add_donation(self.user1_id, 25.0, "USD", status="failed")
            self._add_donation(self.user1_id, 75.0, "USD", status="completed")

        response = self.client.get("/api/donations/total")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertAlmostEqual(data["total_donations"], 175.0)


if __name__ == "__main__":
    unittest.main()
