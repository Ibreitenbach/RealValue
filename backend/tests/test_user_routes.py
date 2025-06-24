# backend/tests/test_user_routes.py
import unittest
import json
from datetime import datetime, timedelta
from backend.app import create_app, db
from backend.app.models import (
    User,
    PracticeChallengeTemplate,
    UserChallengeCompletion,
    ChallengeType,
    DifficultyLevel,
    CompletionStatus,
)
from backend.app.utils import auth as real_auth  # To mock its @token_required
from backend.tests.mock_auth import (
    mock_token_required,
    get_mock_auth_token,
)  # Our mock decorator

# Monkey patch the actual decorator
real_auth.token_required = mock_token_required


class TestUserRoutes(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            self._seed_data()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _seed_data(self):
        user1_obj = User(
            username="user1", email="user1@example.com", password_hash="hash1"
        )
        user2_obj = User(
            username="user2", email="user2@example.com", password_hash="hash2"
        )
        db.session.add_all([user1_obj, user2_obj])
        db.session.commit()
        self.user1_id = user1_obj.id
        self.user2_id = user2_obj.id

        self.template1 = PracticeChallengeTemplate(
            title="Challenge A",
            description="Desc A",
            challenge_type=ChallengeType.TEXT_RESPONSE,
            difficulty=DifficultyLevel.EASY,
            is_active=True,
        )
        self.template2 = PracticeChallengeTemplate(
            title="Challenge B",
            description="Desc B",
            challenge_type=ChallengeType.CHECKBOX_COMPLETION,
            difficulty=DifficultyLevel.MEDIUM,
            is_active=True,
        )
        db.session.add_all([self.template1, self.template2])
        db.session.commit()

        completion1_user1 = UserChallengeCompletion(  # Made local, not self.
            user_id=self.user1_id,  # Use ID
            challenge_template_id=self.template1.id,
            status=CompletionStatus.COMPLETED,
            completed_at=datetime.utcnow() - timedelta(days=1),
            user_response="User1 response to A",
        )
        completion2_user1 = UserChallengeCompletion(  # Made local, not self.
            user_id=self.user1_id,  # Use ID
            challenge_template_id=self.template2.id,
            status=CompletionStatus.PENDING_REVIEW,
            completed_at=datetime.utcnow(),
            user_response="User1 response to B",
        )
        completion1_user2 = UserChallengeCompletion(  # Made local, not self.
            user_id=self.user2_id,  # Use ID
            challenge_template_id=self.template1.id,
            status=CompletionStatus.COMPLETED,
            completed_at=datetime.utcnow() - timedelta(hours=5),
            user_response="User2 response to A",
        )
        db.session.add_all([completion1_user1, completion2_user1, completion1_user2])
        db.session.commit()

        # g.current_user_id will be set in each test method.

    def test_get_my_challenge_completions(self):
        with self.app.app_context():
            from flask import g

            g.current_user_id = self.user1_id  # Test for user1

        headers = {"Authorization": f"Bearer {get_mock_auth_token(self.user1_id)}"}
        response = self.client.get(
            "/api/users/me/challenge_completions", headers=headers
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)

        response_template_ids = sorted([item["challenge_template_id"] for item in data])
        expected_template_ids = sorted([self.template1.id, self.template2.id])
        self.assertEqual(response_template_ids, expected_template_ids)

        for item in data:
            self.assertEqual(item["user_id"], self.user1_id)  # Compare with ID
            if item["challenge_template_id"] == self.template1.id:
                self.assertEqual(item["user_response"], "User1 response to A")
                self.assertEqual(item["status"], "completed")
            elif item["challenge_template_id"] == self.template2.id:
                self.assertEqual(item["user_response"], "User1 response to B")
                self.assertEqual(item["status"], "pending_review")

    def test_get_my_challenge_completions_no_completions(self):
        # Create a new user with no completions
        new_user_obj = User(username="user3_nocompletions", email="user3@example.com")
        new_user_id = None
        with self.app.app_context():  # Ensure this new user is added in an app context
            db.session.add(new_user_obj)
            db.session.commit()
            new_user_id = new_user_obj.id  # Get ID after commit

        with self.app.test_request_context():  # Use test_request_context for g
            from flask import g

            g.current_user_id = new_user_id  # Set current user to the new user's ID

        headers = {"Authorization": f"Bearer {get_mock_auth_token(new_user_id)}"}
        response = self.client.get(
            "/api/users/me/challenge_completions", headers=headers
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)


if __name__ == "__main__":
    unittest.main()
