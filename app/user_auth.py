from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import engine, User

Session = sessionmaker(bind=engine)
session = Session()

def register_user(username, email, password, vacation_days, role):
    print(f"Registering user {username} with {vacation_days} vacation days and role {role}")
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(username=username, email=email, hashed_password=hashed_password, vacation_days=vacation_days, role=role)
    session.add(new_user)
    session.commit()
    print(f"User {username} registered successfully.")

def login_user(username, password):
    print(f"Attempting login for {username}")
    user = session.query(User).filter_by(username=username).first()
    if user and check_password_hash(user.hashed_password, password):
        return user
    return None
