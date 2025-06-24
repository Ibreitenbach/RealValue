# backend/seed.py
from backend.app import create_app, db
from backend.app.models import (
    User,
    UserProfile,
    Skill,
    ExchangeOffer,
    OfferStatusEnum,
    PracticeChallengeTemplate,
    ChallengeType,
    DifficultyLevel,
)


def seed_users():
    """Seeds sample users."""
    print("Seeding users...")
    users_data = [
        {
            "username": "alice_servicer",
            "email": "alice@example.com",
            "password": "password123",
        },
        {
            "username": "bob_seeker",
            "email": "bob@example.com",
            "password": "password123",
        },
        {
            "username": "charlie_exchanger",
            "email": "charlie@example.com",
            "password": "password123",
        },
    ]
    created_users = []
    for user_data in users_data:
        if not User.query.filter_by(email=user_data["email"]).first():
            user = User(username=user_data["username"], email=user_data["email"])
            user.set_password(user_data["password"])
            # Create a basic profile
            profile = UserProfile(
                user=user,
                display_name=user.username,
                bio=f"Hello, I am {user.username}",
            )
            db.session.add(user)
            db.session.add(profile)
            created_users.append(user)
            print(f"Added user: {user_data['username']}")
        else:
            print(f"User with email {user_data['email']} already exists. Skipping.")
            # Still add existing user to created_users for offer seeding
            created_users.append(User.query.filter_by(email=user_data["email"]).first())

    try:
        db.session.commit()
        print("Users seeded successfully.")
        return created_users
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding users: {e}")
        return []


def seed_skills():
    """Seeds sample skills."""
    print("Seeding skills...")
    skills_data = [
        "Python Programming",
        "Graphic Design",
        "Furniture Assembly",
        "Dog Walking",
        "Language Tutoring (Spanish)",
        "Copywriting",
        "Data Analysis",
        "Photography",
        "Car Maintenance Basics",
        "Computer Repair",
    ]
    created_skills = []
    for skill_name in skills_data:
        if not Skill.query.filter_by(name=skill_name).first():
            skill = Skill(name=skill_name)
            db.session.add(skill)
            created_skills.append(skill)
            print(f"Added skill: {skill_name}")
        else:
            print(f"Skill '{skill_name}' already exists. Skipping.")
            created_skills.append(Skill.query.filter_by(name=skill_name).first())

    try:
        db.session.commit()
        print("Skills seeded successfully.")
        return created_skills
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding skills: {e}")
        return []


def seed_exchange_offers(users, skills):
    """Seeds sample exchange offers."""
    if not users or not skills:
        print("Cannot seed exchange offers without users and skills.")
        return

    print("Seeding exchange offers...")
    # Make sure we have enough users and skills for varied offers
    user1, user2, user3 = (
        users[0],
        users[1] if len(users) > 1 else users[0],
        users[2] if len(users) > 2 else users[0],
    )
    skill_py, skill_design, skill_furn, skill_dog, skill_lang = (
        next((s for s in skills if s.name == "Python Programming"), skills[0]),
        next(
            (s for s in skills if s.name == "Graphic Design"), skills[1 % len(skills)]
        ),
        next(
            (s for s in skills if s.name == "Furniture Assembly"),
            skills[2 % len(skills)],
        ),
        next((s for s in skills if s.name == "Dog Walking"), skills[3 % len(skills)]),
        next(
            (s for s in skills if s.name == "Language Tutoring (Spanish)"),
            skills[4 % len(skills)],
        ),
    )

    offers_data = [
        {
            "user_id": user1.id,
            "offered_skill_id": skill_py.id,
            "desired_skill_id": skill_design.id,
            "desired_description": "Need a logo for my new project.",
            "description": "Expert Python developer, can build scripts, web backends, or help with data tasks.",
            "status": OfferStatusEnum.ACTIVE,
            "location_preference": "Remote",
        },
        {
            "user_id": user2.id,
            "offered_skill_id": skill_furn.id,
            "desired_description": "Help with moving a couch next weekend.",
            "description": "Strong and careful, can help with furniture assembly or moving heavy items.",
            "status": OfferStatusEnum.ACTIVE,
            "location_preference": "Local - Springfield",
        },
        {
            "user_id": user3.id,
            "offered_skill_id": skill_dog.id,
            "desired_skill_id": skill_lang.id,
            "desired_description": "Looking for Spanish conversation practice.",
            "description": "Friendly and reliable dog walker available on evenings and weekends.",
            "status": OfferStatusEnum.ACTIVE,
            "location_preference": "Remote or Local",
        },
        {
            "user_id": user1.id,
            "offered_skill_id": skill_design.id,  # Alice also offers design
            "desired_description": "Any help with gardening tasks.",
            "description": "I can create modern logos, brochures, or social media graphics.",
            "status": OfferStatusEnum.ACTIVE,
            "location_preference": "Remote",
        },
        {
            "user_id": user2.id,
            "offered_skill_id": skill_py.id,  # Bob also offers python
            "desired_skill_id": skill_furn.id,
            "desired_description": "I need someone to help me assemble a new IKEA bookshelf.",
            "description": "I'm a junior Python developer, I can help with small scripts or web scraping tasks.",
            "status": OfferStatusEnum.MATCHED,
            "location_preference": "Local - Springfield",
        },
    ]

    for offer_data in offers_data:
        # Check if a very similar offer exists (e.g. same user, offered skill, and desired description)
        # This is a simple check; more sophisticated checks might be needed for true idempotency
        existing_offer = ExchangeOffer.query.filter_by(
            user_id=offer_data["user_id"],
            offered_skill_id=offer_data["offered_skill_id"],
            desired_description=offer_data["desired_description"],
        ).first()

        if not existing_offer:
            offer = ExchangeOffer(**offer_data)
            db.session.add(offer)
            print(
                f"Added exchange offer: User {offer_data['user_id']} offering skill {offer_data['offered_skill_id']}"
            )
        else:
            print(
                f"Similar exchange offer already exists for user {offer_data['user_id']}. Skipping."
            )

    try:
        db.session.commit()
        print("Exchange offers seeded successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding exchange offers: {e}")


def seed_practice_challenges():
    """Seeds sample practice challenges."""
    print("Seeding practice challenges...")
    templates_data = [
        # ... (original templates_data remains here) ...
        {
            "title": "Mindful Minute",
            "description": "Take 60 seconds to focus on your breath. Notice the sensation of air entering and leaving your body. If your mind wanders, gently bring your attention back to your breath.",
            "challenge_type": ChallengeType.CHECKBOX_COMPLETION,
            "difficulty": DifficultyLevel.EASY,
            "is_active": True,
            "associated_skill_id": None,
        },
        {
            "title": "Identify 3 Local Edible Plants",
            "description": "Research and identify three edible plants that grow in your local area. Describe them or upload photos. (For this seed, we'll assume checkbox completion).",
            "challenge_type": ChallengeType.TEXT_RESPONSE,
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
                associated_skill_id=data.get("associated_skill_id"),
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


def seed_all():
    app = create_app()
    with app.app_context():
        # Clear existing data (optional, use with caution for specific models if needed)
        # Example: ExchangeOffer.query.delete()
        # Skill.query.delete()
        # User.query.delete() # Be very careful with deleting users if other data depends on them
        # db.session.commit()

        created_users = seed_users()
        created_skills = seed_skills()
        seed_exchange_offers(created_users, created_skills)
        seed_practice_challenges()  # Keep existing seeding for practice challenges

        print("All data seeding attempts completed.")


if __name__ == "__main__":
    print("Seeding database...")
    seed_all()
    print("Seeding complete.")
