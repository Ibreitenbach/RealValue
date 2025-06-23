# backend/run.py
from app import create_app, db
from app.models import User, UserProfile # Import models for CLI context

app = create_app()

# This makes 'app', 'db', 'User', 'UserProfile' available in `flask shell`
# and ensures the flask command line interface can find the app and models
# for `flask db` commands.
@app.shell_context_processor
def make_shell_context():
    return {'app': app, 'db': db, 'User': User, 'UserProfile': UserProfile}

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
