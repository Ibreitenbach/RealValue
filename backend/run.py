# backend/run.py
from app import create_app, db

app = create_app()


@app.before_request
def create_tables():
    # This will create tables if they don't exist
    # In a real app, you'd use Flask-Migrate or similar for migrations
    with app.app_context():
        db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
