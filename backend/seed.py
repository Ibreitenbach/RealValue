# backend/seed.py
from backend.app import create_app, db
from backend.app.models import (
    User,
    PracticeChallengeTemplate,
    ChallengeType,
    DifficultyLevel,
    Donation,
)

# from datetime import datetime, timedelta # Currently unused


def seed_users():
    """Seeds sample users if they don't already exist."""
    users_data = [
        {
            "username": "seeduser1",
            "email": "seeduser1@example.com",
            "password": "password123",
        },
        {
            "username": "seeduser2",
            "email": "seeduser2@example.com",
            "password": "password456",
        },
    ]

    created_users = []
    for user_data in users_data:
        existing_user = User.query.filter(
            (User.username == user_data["username"])
            | (User.email == user_data["email"])
        ).first()
        if not existing_user:
            user = User(username=user_data["username"], email=user_data["email"])
            user.set_password(user_data["password"])
            db.session.add(user)
            created_users.append(user)
            print(f"Added user: {user_data['username']}")
        else:
            created_users.append(existing_user)
            print(
                f"User '{user_data['username']}' or email "
                f"'{user_data['email']}' already exists. Skipping creation."
            )

    if created_users:
        try:
            db.session.commit()
            print("Users seeded/checked successfully.")
            for i, user_data in enumerate(users_data):
                u = User.query.filter_by(username=user_data["username"]).first()
                if u:
                    created_users[i] = u
        except Exception as e:
            db.session.rollback()
            print(f"Error seeding users: {e}")
    return created_users


def seed_practice_challenges():
    """Seeds sample practice challenge templates."""
    templates_data = [
        {
            "title": "Mindful Minute",
            "description": "Take 60 seconds to focus on your breath...",
            "challenge_type": ChallengeType.CHECKBOX_COMPLETION,
            "difficulty": DifficultyLevel.EASY,
            "is_active": True,
        },
        {
            "title": "Identify 3 Local Edible Plants",
            "description": "Research and identify three edible plants...",
            "challenge_type": ChallengeType.TEXT_RESPONSE,
            "difficulty": DifficultyLevel.MEDIUM,
            "is_active": True,
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
        print(f"Error seeding practice challenges: {e}")


def seed_donations(users):
    """Seeds sample donations."""
    user1_id = None
    user2_id = None
    if users and len(users) > 0 and hasattr(users[0], "id"):
        user1_id = users[0].id
    if users and len(users) > 1 and hasattr(users[1], "id"):
        user2_id = users[1].id

    donations_data = [
        {
            "user_id": user1_id,
            "amount": 25.00,
            "currency": "USD",
            "is_anonymous": False,
            "transaction_id": "SEED_TXN_001",
        },
        {
            "user_id": user2_id,
            "amount": 10.50,
            "currency": "EUR",
            "is_anonymous": True,  # User 2 wants to be anon
            "transaction_id": "SEED_TXN_002",
        },
        {
            "user_id": None,
            "amount": 5.00,
            "currency": "USD",  # Fully anonymous
            "is_anonymous": True,
            "transaction_id": "SEED_TXN_003",
        },
        {
            "user_id": user1_id,
            "amount": 15.00,
            "currency": "USD",
            "is_anonymous": False,
            "transaction_id": "SEED_TXN_004",
        },
    ]

    existing_txn_ids = {
        d.transaction_id for d in Donation.query.all() if d.transaction_id
    }

    for data in donations_data:
        if data["transaction_id"] in existing_txn_ids:
            print(
                f"Donation with transaction ID '{data['transaction_id']}' "
                f"already exists. Skipping."
            )
            continue

        if data["user_id"]:
            user_exists = User.query.get(data["user_id"])
            if not user_exists:
                print(
                    f"User with ID {data['user_id']} not found for donation. "
                    f"Skipping."
                )
                continue

        donation = Donation(
            user_id=data["user_id"],
            amount=data["amount"],
            currency=data["currency"],
            is_anonymous=data["is_anonymous"],
            transaction_id=data["transaction_id"],
            status="completed",
        )
        db.session.add(donation)
        print(
            f"Adding donation: {data['amount']} {data['currency']} "
            f"(TXN: {data['transaction_id']})"
        )

    try:
        db.session.commit()
        print("Sample donations seeded successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding donations: {e}")


def seed_all_data():
    app = create_app()
    with app.app_context():
        db.create_all()

        print("--- Seeding Users ---")
        seeded_users = seed_users()

        print("\n--- Seeding Practice Challenges ---")
        seed_practice_challenges()

        print("\n--- Seeding Donations ---")
        if seeded_users:
            seed_donations(seeded_users)
        else:
            print("Skipping donation seeding as no users were available.")

        print("\nAll seeding processes complete.")


if __name__ == "__main__":
    print("Starting database seeding process...")
    seed_all_data()
    print("Database seeding process finished.")
