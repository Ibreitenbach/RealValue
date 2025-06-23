# backend/seed.py
from backend.app import create_app, db
from backend.app.models import PracticeChallengeTemplate, ChallengeType, DifficultyLevel


def seed_data():
    app = create_app()
    with app.app_context():
        # Clear existing data (optional, use with caution)
        # PracticeChallengeTemplate.query.delete()
        # db.session.commit()

        # Sample Practice Challenge Templates
        templates_data = [
            {
                "title": "Mindful Minute",
                "description": "Take 60 seconds to focus on your breath. Notice the sensation of air entering and leaving your body. If your mind wanders, gently bring your attention back to your breath.",
                "challenge_type": ChallengeType.CHECKBOX_COMPLETION,
                "difficulty": DifficultyLevel.EASY,
                "is_active": True,
                "associated_skill_id": None,  # Or some skill ID if skills are seeded/known
            },
            {
                "title": "Identify 3 Local Edible Plants",
                "description": "Research and identify three edible plants that grow in your local area. Describe them or upload photos. (For this seed, we'll assume checkbox completion).",
                "challenge_type": ChallengeType.TEXT_RESPONSE,  # Changed to TEXT_RESPONSE for variety
                "difficulty": DifficultyLevel.MEDIUM,
                "is_active": True,
                "associated_skill_id": None,
            },
            {
                "title": "Fix a Virtual Leaky Faucet",
                "description": "Imagine you have a leaky faucet. Write down the steps you would take to fix it, or find a video tutorial and summarize the key steps.",
                "challenge_type": ChallengeType.TEXT_RESPONSE,
                "difficulty": DifficultyLevel.MEDIUM,
                "is_active": True,
                "associated_skill_id": None,
            },
            {
                "title": "Gratitude Journal Entry",
                "description": "Write down three things you are grateful for today and why.",
                "challenge_type": ChallengeType.TEXT_RESPONSE,
                "difficulty": DifficultyLevel.EASY,
                "is_active": True,
                "associated_skill_id": None,
            },
            {
                "title": "Share a Photo of Nature",
                "description": "Go outside, take a photo of something in nature that you find beautiful or interesting, and share it (simulated by text response for now).",
                "challenge_type": ChallengeType.PHOTO_UPLOAD,  # Represents photo upload
                "difficulty": DifficultyLevel.EASY,
                "is_active": True,
                "associated_skill_id": None,
            },
            {
                "title": "Plan a Healthy Meal",
                "description": "Plan a balanced and healthy meal for dinner tonight. List the main ingredients and why it's a healthy choice.",
                "challenge_type": ChallengeType.TEXT_RESPONSE,
                "difficulty": DifficultyLevel.MEDIUM,
                "is_active": False,  # Example of an inactive challenge
                "associated_skill_id": None,
            },
        ]

        existing_titles = {
            template.title for template in PracticeChallengeTemplate.query.all()
        }

        for data in templates_data:
            if data["title"] not in existing_titles:
                template = PracticeChallengeTemplate(
                    title=data["title"],
                    description=data["description"],
                    challenge_type=data["challenge_type"],
                    difficulty=data["difficulty"],
                    is_active=data["is_active"],
                    associated_skill_id=data["associated_skill_id"],
                )
                db.session.add(template)
                print(f"Added challenge: {data['title']}")
            else:
                print(f"Challenge '{data['title']}' already exists. Skipping.")

        try:
            db.session.commit()
            print("Sample practice challenge templates seeded successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error seeding data: {e}")


if __name__ == "__main__":
    print("Seeding database...")
    seed_data()
    print("Seeding complete.")
