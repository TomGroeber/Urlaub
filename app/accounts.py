import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.user_auth import register_user

# Benutzer registrieren mit einer bestimmten Anzahl von Urlaubstagen und Rollen
register_user("user1", "user1@example.com", "user1pass", 14, "Dreher")
register_user("user2", "user2@example.com", "user2pass", 14, "Fräser")
register_user("user3", "user3@example.com", "user3pass", 14, "Alles")
register_user("admin", "admin@example.com", "adminpass", 0, "Admin")  # Admin hat keine Urlaubstage benötigt

print("Test users created successfully.")
