from database import session, User
from user_auth import register_user

# Löschen Sie vorhandene Benutzer, falls vorhanden
session.query(User).delete()
session.commit()

register_user("user1", "user1@example.com", "user1pass", 14, "Dreher")
register_user("user2", "user2@example.com", "user2pass", 14, "Fräser")
register_user("user3", "user3@example.com", "user3pass", 14, "Dreher")
register_user("admin", "admin@example.com", "adminpass", 0, "Admin")
