# backend/tests/test_practice_challenge_routes.py
import unittest
import json
from backend.app import create_app, db
from backend.app.models import (
    User,
    PracticeChallengeTemplate,
    UserChallengeCompletion,
    ChallengeType,
    DifficultyLevel,
    # CompletionStatus, # Removed as unused
)
from backend.app.utils import auth as real_auth  # To mock its @token_required
from backend.tests.mock_auth import (
    mock_token_required,
    get_mock_auth_token,
)  # Our mock decorator

# Monkey patch the actual decorator with our mock before routes are imported by create_app indirectly
real_auth.token_required = mock_token_required


class TestPracticeChallengeRoutes(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        # self.app.config['SECRET_KEY'] = 'test_secret_key' # if needed for session or tokens
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            self._seed_data()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _seed_data(self):
        test_user_obj = User(
            username="testuser", email="test@example.com", password_hash="hashed"
        )
        db.session.add(test_user_obj)
        db.session.commit()
        self.test_user_id = test_user_obj.id  # Store ID instead of instance

        # Remove setting g.current_user here, will be done per test via g.current_user_id
        # with self.app.test_request_context():
        #     from flask import g
        #     g.current_user = self.test_user # This was problematic

        self.template1 = PracticeChallengeTemplate(
            title="Active Easy Challenge",
            description="Desc1",
            challenge_type=ChallengeType.TEXT_RESPONSE,
            difficulty=DifficultyLevel.EASY,
            is_active=True,
            associated_skill_id=101,
        )
        self.template2 = PracticeChallengeTemplate(
            title="Active Medium Challenge",
            description="Desc2",
            challenge_type=ChallengeType.PHOTO_UPLOAD,
            difficulty=DifficultyLevel.MEDIUM,
            is_active=True,
            associated_skill_id=102,
        )
        self.template3 = PracticeChallengeTemplate(
            title="Inactive Easy Challenge",
            description="Desc3",
            challenge_type=ChallengeType.CHECKBOX_COMPLETION,
            difficulty=DifficultyLevel.EASY,
            is_active=False,
            associated_skill_id=101,
        )
        self.template4 = PracticeChallengeTemplate(
            title="Active Hard Challenge Specific Skill",
            description="Desc4",
            challenge_type=ChallengeType.TEXT_RESPONSE,
            difficulty=DifficultyLevel.HARD,
            is_active=True,
            associated_skill_id=101,  # Same skill as template1
        )
        db.session.add_all(
            [self.template1, self.template2, self.template3, self.template4]
        )
        db.session.commit()

        # Pre-populate g.current_user for the mock decorator
        # This is a bit of a hack; ideally, the mock_token_required would handle user loading
        # or tests would set g.current_user before each request if it varies.
        # For these tests, we assume all @token_required routes are called by self.test_user
        # from flask import g # Removed, g.current_user_id will be set per test
        # g.current_user = self.test_user # Removed

    def test_get_active_practice_challenge_templates(self):
        with self.app.app_context(): # Ensure app context for g
            from flask import g
            g.current_user_id = self.test_user_id
        # Provide a mock token in headers, even if decorator is mocked, it's good practice
        headers = {"Authorization": f"Bearer {get_mock_auth_token(self.test_user_id)}"}
        response = self.client.get(
            "/api/practice_challenges/templates", headers=headers
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 3)  # template1, template2, template4 are active
        titles = [item["title"] for item in data]
        self.assertIn("Active Easy Challenge", titles)
        self.assertIn("Active Medium Challenge", titles)
        self.assertIn("Active Hard Challenge Specific Skill", titles)
        self.assertNotIn("Inactive Easy Challenge", titles)

    def test_get_templates_filtered_by_difficulty(self):
        with self.app.app_context():
            from flask import g
            g.current_user_id = self.test_user_id
        headers = {"Authorization": f"Bearer {get_mock_auth_token(self.test_user_id)}"}
        response = self.client.get(
            "/api/practice_challenges/templates?difficulty=EASY", headers=headers
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "Active Easy Challenge")

        response = self.client.get(
            "/api/practice_challenges/templates?difficulty=HARD", headers=headers
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "Active Hard Challenge Specific Skill")

        response = self.client.get(
            "/api/practice_challenges/templates?difficulty=UNKNOWN", headers=headers
        )
        self.assertEqual(response.status_code, 400)  # Invalid difficulty

    def test_get_templates_filtered_by_skill_id(self):
        with self.app.app_context():
            from flask import g
            g.current_user_id = self.test_user_id
        headers = {"Authorization": f"Bearer {get_mock_auth_token(self.test_user_id)}"}
        response = self.client.get(
            "/api/practice_challenges/templates?associated_skill_id=101",
            headers=headers,
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)  # template1 and template4
        titles = sorted([item["title"] for item in data])
        self.assertEqual(
            titles,
            sorted(["Active Easy Challenge", "Active Hard Challenge Specific Skill"]),
        )

    def test_get_specific_practice_challenge_template_detail(self):
        with self.app.app_context():
            from flask import g
            g.current_user_id = self.test_user_id
        headers = {"Authorization": f"Bearer {get_mock_auth_token(self.test_user_id)}"}
        response = self.client.get(
            f"/api/practice_challenges/templates/{self.template1.id}", headers=headers
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["title"], "Active Easy Challenge")

    def test_get_specific_template_not_found(self):
        with self.app.app_context():
            from flask import g
            g.current_user_id = self.test_user_id
        headers = {"Authorization": f"Bearer {get_mock_auth_token(self.test_user_id)}"}
        response = self.client.get(
            "/api/practice_challenges/templates/9999", headers=headers
        )
        self.assertEqual(response.status_code, 404)

    def test_complete_practice_challenge_success(self):
        with self.app.app_context():
            from flask import g
            g.current_user_id = self.test_user_id
        headers = {
            "Authorization": f"Bearer {get_mock_auth_token(self.test_user_id)}",
            "Content-Type": "application/json",
        }
        payload = {
            "challenge_template_id": self.template1.id,
            "user_response": "I completed this easy challenge!",
        }
        response = self.client.post(
            "/api/practice_challenges/complete",
            headers=headers,
            data=json.dumps(payload),
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["challenge_template_id"], self.template1.id)
        self.assertEqual(data["user_id"], self.test_user_id) # Compare with ID
        self.assertEqual(data["user_response"], "I completed this easy challenge!")
        self.assertEqual(data["status"], "completed")  # Default status in route

        completion_in_db = UserChallengeCompletion.query.filter_by(
            user_id=self.test_user_id, challenge_template_id=self.template1.id # Use ID
        ).first()
        self.assertIsNotNone(completion_in_db)
        self.assertEqual(
            completion_in_db.user_response, "I completed this easy challenge!"
        )

    def test_complete_challenge_template_not_found(self):
        with self.app.app_context():
            from flask import g
            g.current_user_id = self.test_user_id
        headers = {
            "Authorization": f"Bearer {get_mock_auth_token(self.test_user_id)}",
            "Content-Type": "application/json",
        }
        payload = {
            "challenge_template_id": 9999,
            "user_response": "Trying to complete non-existent.",
        }
        response = self.client.post(
            "/api/practice_challenges/complete",
            headers=headers,
            data=json.dumps(payload),
        )
        self.assertEqual(response.status_code, 404)

    def test_complete_challenge_inactive_template(self):
        with self.app.app_context():
            from flask import g
            g.current_user_id = self.test_user_id
        headers = {
            "Authorization": f"Bearer {get_mock_auth_token(self.test_user_id)}",
            "Content-Type": "application/json",
        }
        payload = {
            "challenge_template_id": self.template3.id,
            "user_response": "Trying to complete inactive.",
        }
        response = self.client.post(
            "/api/practice_challenges/complete",
            headers=headers,
            data=json.dumps(payload),
        )
        self.assertEqual(response.status_code, 400)  # As per route logic for inactive
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Cannot complete an inactive challenge")

    def test_complete_challenge_missing_template_id(self):
        with self.app.app_context():
            from flask import g
            g.current_user_id = self.test_user_id
        headers = {
            "Authorization": f"Bearer {get_mock_auth_token(self.test_user_id)}",
            "Content-Type": "application/json",
        }
        payload = {"user_response": "No template ID provided."}
        response = self.client.post(
            "/api/practice_challenges/complete",
            headers=headers,
            data=json.dumps(payload),
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "challenge_template_id is required")


if __name__ == "__main__":
    # Important: This setup allows running tests with `python -m unittest backend.tests.test_practice_challenge_routes`
    # or via a test runner. The monkeypatching needs to happen before Flask app creation.
    unittest.main()
