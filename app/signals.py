# signals.py
from flask_login import user_logged_in
from datetime import datetime, timezone
from app import db
from app.models import UserDetails

@user_logged_in.connect
def update_last_login(sender, user, **extra):
    if user.details:
        user.details.last_login = datetime.now(timezone.utc)
        db.session.commit()
        print(f"{user.username} logged in at {user.details.last_login}")
