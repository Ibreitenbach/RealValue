# backend/tests/test_practice_challenge_models.py
import unittest
from datetime import datetime
from backend.app import create_app, db
from backend.app.models import (
    User,
    PracticeChallengeTemplate,
    UserChallengeCompletion,
    ChallengeType,
    DifficultyLevel,
    CompletionStatus,
)


class TestPracticeChallengeModels(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            self._seed_test_user()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _seed_test_user(self):
        test_user_obj = User(username="testuser", email="test@example.com")
        db.session.add(test_user_obj)
        db.session.commit()
        self.test_user_id = test_user_obj.id  # Store ID

    def test_create_practice_challenge_template(self):
        with self.app.app_context():
            template = PracticeChallengeTemplate(
                title="Test Challenge",
                description="A challenge for testing.",
                challenge_type=ChallengeType.TEXT_RESPONSE,
                difficulty=DifficultyLevel.EASY,
                is_active=True,
                associated_skill_id=1,
            )
            db.session.add(template)
            db.session.commit()

            self.assertIsNotNone(template.id)
            self.assertEqual(template.title, "Test Challenge")
            self.assertEqual(template.challenge_type, ChallengeType.TEXT_RESPONSE)
            self.assertTrue(template.is_active)
            self.assertIsNotNone(template.created_at)
            self.assertIsNotNone(template.updated_at)

            retrieved_template = PracticeChallengeTemplate.query.get(template.id)
            self.assertEqual(retrieved_template.title, "Test Challenge")

    def test_practice_challenge_template_to_dict(self):
        with self.app.app_context():
            dt = datetime.utcnow()
            template = PracticeChallengeTemplate(
                title="Dict Test",
                description="Testing to_dict.",
                challenge_type=ChallengeType.PHOTO_UPLOAD,
                difficulty=DifficultyLevel.MEDIUM,
                is_active=False,
                created_at=dt,
                updated_at=dt,
            )
            db.session.add(template)
            db.session.commit()  # id is assigned after commit

            template_dict = template.to_dict()
            self.assertEqual(template_dict["title"], "Dict Test")
            self.assertEqual(template_dict["challenge_type"], "photo_upload")
            self.assertEqual(template_dict["difficulty"], "medium")
            self.assertFalse(template_dict["is_active"])
            self.assertEqual(template_dict["id"], template.id)
            self.assertIsNotNone(template_dict["created_at"])

    def test_create_user_challenge_completion(self):
        with self.app.app_context():
            test_user = db.session.get(User, self.test_user_id)  # Fetch user
            template = PracticeChallengeTemplate(
                title="Completion Test Challenge",
                description="A challenge for testing completion.",
                challenge_type=ChallengeType.CHECKBOX_COMPLETION,
                difficulty=DifficultyLevel.HARD,
            )
            db.session.add(template)
            db.session.commit()

            completion = UserChallengeCompletion(
                user_id=test_user.id,  # Use fetched user's ID
                challenge_template_id=template.id,
                status=CompletionStatus.COMPLETED,
                completed_at=datetime.utcnow(),
                user_response="Done",
            )
            db.session.add(completion)
            db.session.commit()

            self.assertIsNotNone(completion.id)
            self.assertEqual(
                completion.user_id, test_user.id
            )  # Compare with fetched user's ID
            self.assertEqual(completion.challenge_template_id, template.id)
            self.assertEqual(completion.status, CompletionStatus.COMPLETED)
            self.assertIsNotNone(completion.completed_at)
            self.assertEqual(completion.user_response, "Done")

            retrieved_completion = UserChallengeCompletion.query.get(completion.id)
            self.assertEqual(retrieved_completion.status, CompletionStatus.COMPLETED)

    def test_user_challenge_completion_to_dict(self):
        with self.app.app_context():
            test_user = db.session.get(User, self.test_user_id)  # Fetch user
            template = PracticeChallengeTemplate(
                title="Completion Dict Test",
                description="Testing completion to_dict.",
                challenge_type=ChallengeType.TEXT_RESPONSE,
                difficulty=DifficultyLevel.EASY,
            )
            db.session.add(template)
            db.session.commit()

            dt = datetime.utcnow()
            completion = UserChallengeCompletion(
                user_id=test_user.id,  # Use fetched user's ID
                challenge_template_id=template.id,
                status=CompletionStatus.PENDING_REVIEW,
                completed_at=dt,
                user_response="My thoughts.",
            )
            db.session.add(completion)
            db.session.commit()  # id is assigned after commit

            completion_dict = completion.to_dict()
            self.assertEqual(
                completion_dict["user_id"], test_user.id
            )  # Compare with fetched user's ID
            self.assertEqual(completion_dict["challenge_template_id"], template.id)
            self.assertEqual(completion_dict["challenge_title"], "Completion Dict Test")
            self.assertEqual(completion_dict["status"], "pending_review")
            self.assertEqual(completion_dict["user_response"], "My thoughts.")
            self.assertEqual(completion_dict["id"], completion.id)
            self.assertIsNotNone(completion_dict["completed_at"])

    def test_relationships(self):
        with self.app.app_context():
            test_user = db.session.get(User, self.test_user_id)  # Fetch user
            template = PracticeChallengeTemplate(
                title="Relationship Test",
                description="Testing model relationships.",
                challenge_type=ChallengeType.TEXT_RESPONSE,
                difficulty=DifficultyLevel.MEDIUM,
            )
            db.session.add(template)
            db.session.commit()

            completion = UserChallengeCompletion(
                user_id=test_user.id,  # Use fetched user's ID
                challenge_template_id=template.id,
                status=CompletionStatus.COMPLETED,
            )
            db.session.add(completion)
            db.session.commit()

            # Test template.completions
            self.assertIn(completion, template.completions)
            # Test completion.user
            self.assertEqual(completion.user, test_user)  # Compare with fetched user
            # Test completion.challenge_template
            self.assertEqual(completion.challenge_template, template)
            # Test user.challenge_completions (backref)
            # Need to refresh test_user to see the backref populated through the session
            db.session.refresh(test_user)
            self.assertIn(completion, test_user.challenge_completions)


if __name__ == "__main__":
    unittest.main()
