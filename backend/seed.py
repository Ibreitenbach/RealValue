# backend/seed.py
from backend.app import create_app, db
from backend.app.models import (
    User,
    UserProfile,
    Skill,  # Added for skill seeding
    ExchangeOffer,  # Added for exchange offer seeding
    OfferStatusEnum,  # Added for exchange offer seeding
    PracticeChallengeTemplate,
    ChallengeType,
    DifficultyLevel,
    Donation,  # Added for donation seeding
    JournalEntry, # Added for Mind progress seeding
    MindsetChallengeTemplate, # Added for Mind progress seeding
    UserMindsetCompletion, # Added for Mind progress seeding
    MindfulMomentTemplate, # Added for Mind progress seeding
    UserReminderSetting, # Added for Mind progress seeding
    MindContent, # Added for Mind Content Library seeding
    MindContentCategory, # Added for Mind Content Library seeding
    ShowcaseItem, # Added for Showcase seeding
    Post, # Added for Need/Offer board seeding
    PostType, # Added for Need/Offer board seeding
    Favor, # Added for Favor seeding
    Circle, CircleMember, # Added for Crew Circles seeding
    Event # Added for Event seeding
)
from datetime import datetime, timedelta # Will use if needed

def seed_users():
    """Seeds sample users and their profiles."""
    print("--- Seeding Users ---")
    users_data = [
        {
            "username": "alice_servicer",
            "email": "alice@example.com",
            "password": "password123",
            "display_name": "Alice S.",
            "bio": "Expert in Python and graphic design.",
        },
        {
            "username": "bob_seeker",
            "email": "bob@example.com",
            "password": "password123",
            "display_name": "Bob J.",
            "bio": "Always learning, currently need help with moving.",
        },
        {
            "username": "charlie_exchanger",
            "email": "charlie@example.com",
            "password": "password123",
            "display_name": "Charlie X.",
            "bio": "Happy to exchange skills!",
        },
        {
            "username": "seeduser1", # From main
            "email": "seeduser1@example.com",
            "password": "password123",
            "display_name": "Seed User One",
            "bio": "A generic seeded user.",
        },
        {
            "username": "seeduser2", # From main
            "email": "seeduser2@example.com",
            "password": "password456",
            "display_name": "Seed User Two",
            "bio": "Another generic seeded user.",
        },
    ]

    created_users = []
    for user_data in users_data:
        existing_user = User.query.filter(
            (User.username == user_data["username"]) | (User.email == user_data["email"])
        ).first()

        if not existing_user:
            user = User(username=user_data["username"], email=user_data["email"])
            user.set_password(user_data["password"])
            db.session.add(user)
            db.session.flush() # Flush to get user.id before profile creation

            profile = UserProfile(
                user_id=user.id, # Link profile to user
                display_name=user_data.get("display_name", user.username),
                bio=user_data.get("bio", f"Hello, I am {user.username}"),
            )
            db.session.add(profile)
            created_users.append(user)
            print(f"Added user: {user_data['username']} with profile.")
        else:
            created_users.append(existing_user)
            print(f"User '{user_data['username']}' already exists. Skipping creation.")

    try:
        db.session.commit()
        print("Users and profiles seeded successfully.")
        return created_users
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding users: {e}")
        return []


def seed_skills():
    """Seeds sample skills."""
    print("--- Seeding Skills ---")
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
    print("--- Seeding Exchange Offers ---")
    if not users or not skills:
        print("Cannot seed exchange offers without users and skills.")
        return

    # Ensure we have enough users and skills for varied offers
    user1, user2, user3 = (
        users[0],
        users[1] if len(users) > 1 else users[0],
        users[2] if len(users) > 2 else users[0],
    )
    # Safely get skills, fallback to first available if not found by name
    skill_py = next((s for s in skills if s.name == "Python Programming"), skills[0])
    skill_design = next((s for s in skills if s.name == "Graphic Design"), skills[1 % len(skills)])
    skill_furn = next((s for s in skills if s.name == "Furniture Assembly"), skills[2 % len(skills)])
    skill_dog = next((s for s in skills if s.name == "Dog Walking"), skills[3 % len(skills)])
    skill_lang = next((s for s in skills if s.name == "Language Tutoring (Spanish)"), skills[4 % len(skills)])


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
    """Seeds sample practice challenge templates."""
    print("--- Seeding Practice Challenges ---")
    templates_data = [
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
                associated_skill_id=data.get("associated_skill_id"), # Use .get for optional key
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
    print("--- Seeding Donations ---")
    # Ensure users are retrieved from the database session to avoid DetachedInstanceError
    user1 = User.query.get(users[0].id) if users and len(users) > 0 else None
    user2 = User.query.get(users[1].id) if users and len(users) > 1 else None

    donations_data = [
        {
            "user_id": user1.id if user1 else None,
            "amount": 25.00,
            "currency": "USD",
            "is_anonymous": False,
            "transaction_id": "SEED_TXN_001",
        },
        {
            "user_id": user2.id if user2 else None,
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
            "user_id": user1.id if user1 else None,
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

        if data["user_id"]: # Only check if user_id is provided
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
            status="completed", # Assumed status for seeded data
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


def seed_journal_entries(users):
    """Seeds sample journal entries."""
    print("--- Seeding Journal Entries ---")
    if not users:
        print("Cannot seed journal entries without users.")
        return

    user1 = users[0]
    user2 = users[1] if len(users) > 1 else users[0]

    entries_data = [
        {
            "user_id": user1.id,
            "title": "Gratitude Practice",
            "content": "Today I am grateful for the warm sun and a quiet moment to reflect.",
            "prompt": "What are you grateful for today?",
            "reflection_tags": "gratitude",
        },
        {
            "user_id": user2.id,
            "title": "Reframing a Challenge",
            "content": "My car broke down, but it gave me a chance to practice patience and walk, discovering a new path.",
            "prompt": "How can you reframe a recent challenge?",
            "reflection_tags": "reframing, patience",
        },
    ]

    for data in entries_data:
        existing_entry = JournalEntry.query.filter_by(
            user_id=data["user_id"], title=data["title"]
        ).first()
        if not existing_entry:
            entry = JournalEntry(**data, is_private=True)
            db.session.add(entry)
            print(f"Added journal entry: {data['title']} for user {data['user_id']}")
        else:
            print(f"Journal entry '{data['title']}' for user {data['user_id']} already exists. Skipping.")

    try:
        db.session.commit()
        print("Journal entries seeded successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding journal entries: {e}")


def seed_mindset_challenges():
    """Seeds sample mindset challenge templates."""
    print("--- Seeding Mindset Challenges ---")
    templates_data = [
        {
            "title": "Practice Not Giving A Fuck (About Small Things)",
            "description": "Choose one minor inconvenience today (e.g., slow internet, spilled coffee) and consciously decide not to let it affect your mood. Observe your reaction.",
            "category": "stoicism",
            "frequency": "daily",
            "is_active": True,
        },
        {
            "title": "Find Unexpected Beauty",
            "description": "Look for one moment of unexpected beauty or humor in your day – a cloud formation, a child's laugh, a funny typo. Capture it if you can.",
            "category": "mindfulness, humor",
            "frequency": "daily",
            "is_active": True,
        },
    ]
    existing_titles = {t.title for t in MindsetChallengeTemplate.query.all()}
    for data in templates_data:
        if data["title"] not in existing_titles:
            template = MindsetChallengeTemplate(**data)
            db.session.add(template)
            print(f"Added mindset challenge: {data['title']}")
        else:
            print(f"Mindset challenge '{data['title']}' already exists. Skipping.")
    try:
        db.session.commit()
        print("Mindset challenges seeded successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding mindset challenges: {e}")


def seed_mindful_moments():
    """Seeds sample mindful moment templates."""
    print("--- Seeding Mindful Moments ---")
    templates_data = [
        {"text": "Be a rock.", "category": "focus", "is_active": True},
        {"text": "Find one unexpected beauty.", "category": "mindfulness", "is_active": True},
        {"text": "Practice gratitude.", "category": "gratitude", "is_active": True},
    ]
    existing_texts = {t.text for t in MindfulMomentTemplate.query.all()}
    for data in templates_data:
        if data["text"] not in existing_texts:
            template = MindfulMomentTemplate(**data)
            db.session.add(template)
            print(f"Added mindful moment: {data['text']}")
        else:
            print(f"Mindful moment '{data['text']}' already exists. Skipping.")
    try:
        db.session.commit()
        print("Mindful moments seeded successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding mindful moments: {e}")


def seed_mind_content_categories():
    """Seeds sample mind content categories."""
    print("--- Seeding Mind Content Categories ---")
    categories_data = ["Stoicism", "CBT", "Mindfulness", "Philosophical Resilience", "Humor"]
    existing_names = {c.name for c in MindContentCategory.query.all()}
    for name in categories_data:
        if name not in existing_names:
            category = MindContentCategory(name=name)
            db.session.add(category)
            print(f"Added mind content category: {name}")
        else:
            print(f"Mind content category '{name}' already exists. Skipping.")
    try:
        db.session.commit()
        print("Mind content categories seeded successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding mind content categories: {e}")


def seed_mind_content(users):
    """Seeds sample mind content items."""
    print("--- Seeding Mind Content Items ---")
    if not users:
        print("Cannot seed mind content without users.")
        return
    
    cat_stoicism = MindContentCategory.query.filter_by(name="Stoicism").first()
    cat_mindfulness = MindContentCategory.query.filter_by(name="Mindfulness").first()

    content_data = [
        {
            "title": "The Daily Stoic: Morning Meditation",
            "description": "A short article on daily stoic practices.",
            "url": "https://dailystoic.com/morning-meditation-2/",
            "mind_content_category_id": cat_stoicism.id if cat_stoicism else None,
            "content_type": "article",
            "author_name": "Ryan Holiday",
            "read_time_minutes": 5,
            "is_active": True,
        },
        {
            "title": "Guided Mindfulness Meditation (10 Mins)",
            "description": "A beginner-friendly audio guide to mindfulness.",
            "url": "https://www.headspace.com/meditation/mindfulness-meditation-for-beginners", # Placeholder URL
            "mind_content_category_id": cat_mindfulness.id if cat_mindfulness else None,
            "content_type": "podcast",
            "author_name": "Andy Puddicombe",
            "duration_minutes": 10,
            "is_active": True,
        },
    ]

    existing_titles = {item.title for item in MindContent.query.all()}
    for data in content_data:
        if data["title"] not in existing_titles:
            # Add a user_id if needed, assuming first user is content suggester
            item = MindContent(**data) # No added_by_user_id yet in the model, just content
            db.session.add(item)
            print(f"Added mind content: {data['title']}")
        else:
            print(f"Mind content '{data['title']}' already exists. Skipping.")
    try:
        db.session.commit()
        print("Mind content items seeded successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding mind content items: {e}")


def seed_showcase_items(users, skills):
    """Seeds sample showcase items."""
    print("--- Seeding Showcase Items ---")
    if not users or not skills:
        print("Cannot seed showcase items without users and skills.")
        return

    user_alice = users[0]
    skill_py = next((s for s in skills if s.name == "Python Programming"), skills[0])
    skill_furn = next((s for s in skills if s.name == "Furniture Assembly"), skills[0])

    showcase_data = [
        {
            "user_id": user_alice.id,
            "title": "My First Python Script",
            "description": "A simple script to automate file organization.",
            "associated_skill_id": skill_py.id if skill_py else None,
            "media_url": "/uploads/placeholder_python.png", # Placeholder URL
            "media_type": "image",
        },
        {
            "user_id": user_alice.id,
            "title": "Assembled IKEA Bookshelf",
            "description": "Successfully put together a challenging IKEA bookshelf.",
            "associated_skill_id": skill_furn.id if skill_furn else None,
            "media_url": "/uploads/placeholder_bookshelf.jpg", # Placeholder URL
            "media_type": "image",
        },
    ]

    existing_titles = {item.title for item in ShowcaseItem.query.all()}
    for data in showcase_data:
        if data["title"] not in existing_titles:
            item = ShowcaseItem(**data)
            db.session.add(item)
            print(f"Added showcase item: {data['title']}")
        else:
            print(f"Showcase item '{data['title']}' already exists. Skipping.")
    try:
        db.session.commit()
        print("Showcase items seeded successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding showcase items: {e}")


def seed_post_types():
    """Seeds sample post types (Need, Offer)."""
    print("--- Seeding Post Types ---")
    post_types_data = ["Need", "Offer"]
    existing_types = {pt.name for pt in PostType.query.all()}
    for name in post_types_data:
        if name not in existing_types:
            post_type = PostType(name=name)
            db.session.add(post_type)
            print(f"Added post type: {name}")
        else:
            print(f"Post type '{name}' already exists. Skipping.")
    try:
        db.session.commit()
        print("Post types seeded successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding post types: {e}")


def seed_posts(users):
    """Seeds sample posts for Need/Offer Board."""
    print("--- Seeding Posts ---")
    if not users:
        print("Cannot seed posts without users.")
        return

    user1 = users[0]
    user2 = users[1] if len(users) > 1 else users[0]

    post_type_need = PostType.query.filter_by(name="Need").first()
    post_type_offer = PostType.query.filter_by(name="Offer").first()

    posts_data = [
        {
            "user_id": user1.id,
            "post_type_id": post_type_need.id if post_type_need else None,
            "title": "Need help moving couch",
            "description": "Looking for help moving a heavy couch this Saturday.",
            "location": "Downtown OKC",
            "latitude": 35.4676, "longitude": -97.5164,
            "status": "active",
        },
        {
            "user_id": user2.id,
            "post_type_id": post_type_offer.id if post_type_offer else None,
            "title": "Offering gardening tools",
            "description": "Have extra gardening tools to lend for small projects.",
            "location": "Midtown OKC",
            "latitude": 35.4851, "longitude": -97.5256,
            "status": "active",
        },
    ]

    existing_titles = {p.title for p in Post.query.all()}
    for data in posts_data:
        if data["title"] not in existing_titles:
            post = Post(**data)
            db.session.add(post)
            print(f"Added post: {data['title']}")
        else:
            print(f"Post '{data['title']}' already exists. Skipping.")
    try:
        db.session.commit()
        print("Posts seeded successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding posts: {e}")


def seed_favors(users):
    """Seeds sample favors."""
    print("--- Seeding Favors ---")
    if not users or len(users) < 2:
        print("Cannot seed favors without at least two users.")
        return

    user1 = users[0]
    user2 = users[1]

    favors_data = [
        {
            "giver_id": user1.id,
            "receiver_id": user2.id,
            "description": "Helped move boxes",
            "status": "completed",
        },
        {
            "giver_id": user2.id,
            "receiver_id": user1.id,
            "description": "Lent car tools",
            "status": "completed",
        },
    ]
    
    for data in favors_data:
        existing_favor = Favor.query.filter_by(
            giver_id=data['giver_id'],
            receiver_id=data['receiver_id'],
            description=data['description']
        ).first()
        if not existing_favor:
            favor = Favor(**data, requested_at=datetime.utcnow(), completed_at=datetime.utcnow())
            db.session.add(favor)
            print(f"Added favor: {data['description']} from {user1.username} to {user2.username}")
        else:
            print(f"Favor '{data['description']}' between {data['giver_id']} and {data['receiver_id']} already exists. Skipping.")

    try:
        db.session.commit()
        print("Favors seeded successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding favors: {e}")


def seed_circles(users):
    """Seeds sample Crew Circles."""
    print("--- Seeding Crew Circles ---")
    if not users or len(users) < 3:
        print("Cannot seed circles without at least three users.")
        return

    user1 = users[0]
    user2 = users[1]
    user3 = users[2]

    circles_data = [
        {
            "name": "Neighborhood DIY Crew",
            "description": "For DIY projects and tool sharing.",
            "creator_id": user1.id,
        },
        {
            "name": "OKC Garden Enthusiasts",
            "description": "Sharing tips and produce from our gardens.",
            "creator_id": user2.id,
        },
    ]

    for data in circles_data:
        existing_circle = Circle.query.filter_by(name=data["name"]).first()
        if not existing_circle:
            circle = Circle(name=data["name"], description=data["description"], creator_id=data["creator_id"])
            db.session.add(circle)
            db.session.flush() # To get circle ID for members
            
            # Add creator as admin
            member = CircleMember(circle_id=circle.id, user_id=data["creator_id"], role="admin")
            db.session.add(member)
            
            # Add other members
            if data["name"] == "Neighborhood DIY Crew":
                member2 = CircleMember(circle_id=circle.id, user_id=user2.id, role="member")
                db.session.add(member2)
            elif data["name"] == "OKC Garden Enthusiasts":
                member3 = CircleMember(circle_id=circle.id, user_id=user3.id, role="member")
                db.session.add(member3)
            
            print(f"Added circle: {data['name']}")
        else:
            print(f"Circle '{data['name']}' already exists. Skipping.")
            
    try:
        db.session.commit()
        print("Crew Circles seeded successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding circles: {e}")


def seed_events(users):
    """Seeds sample events."""
    print("--- Seeding Events ---")
    if not users or len(users) < 1:
        print("Cannot seed events without users.")
        return

    user1 = users[0]

    events_data = [
        {
            "user_id": user1.id,
            "title": "Community Garden Day",
            "description": "Help us prepare the community garden beds for spring planting.",
            "start_time": datetime.utcnow() + timedelta(days=7, hours=10),
            "end_time": datetime.utcnow() + timedelta(days=7, hours=14),
            "location_name": "Central Park Community Garden",
            "latitude": 35.5, "longitude": -97.5,
            "is_public": True,
            "status": "active",
        },
        {
            "user_id": user1.id,
            "title": "Basic Bike Maintenance Workshop",
            "description": "Learn how to fix a flat tire and adjust brakes.",
            "start_time": datetime.utcnow() + timedelta(days=14, hours=18),
            "end_time": datetime.utcnow() + timedelta(days=14, hours=20),
            "location_name": "Local Bike Shop",
            "latitude": 35.4, "longitude": -97.6,
            "is_public": True,
            "status": "active",
        },
    ]

    for data in events_data:
        existing_event = Event.query.filter_by(title=data["title"], user_id=data["user_id"]).first()
        if not existing_event:
            event = Event(**data)
            db.session.add(event)
            print(f"Added event: {data['title']}")
        else:
            print(f"Event '{data['title']}' already exists. Skipping.")
    try:
        db.session.commit()
        print("Events seeded successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding events: {e}")


def seed_all_data():
    """Seeds all application data."""
    app = create_app()
    with app.app_context():
        db.create_all() # Ensure all tables are created

        print("Starting all data seeding processes...")

        seeded_users = seed_users()
        seeded_skills = seed_skills()
        
        # Ensure users and skills are available before dependent seeding
        if not seeded_users:
            print("Skipping dependent seeding as no users were available.")
            return
        if not seeded_skills:
            print("Skipping skill-dependent seeding as no skills were available.")


        seed_exchange_offers(seeded_users, seeded_skills)
        seed_practice_challenges()
        seed_donations(seeded_users)
        seed_journal_entries(seeded_users)
        seed_mindset_challenges()
        seed_mindful_moments()
        seed_mind_content_categories()
        seed_mind_content(seeded_users)
        seed_showcase_items(seeded_users, seeded_skills)
        seed_post_types()
        seed_posts(seeded_users)
        seed_favors(seeded_users)
        seed_circles(seeded_users)
        seed_events(seeded_users)

        print("All data seeding processes completed.")


if __name__ == "__main__":
    seed_all_data()
    print("Database seeding finished.")