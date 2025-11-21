from sqlalchemy.orm import Session
from model import User
from app.auth.security import verify_password, hash_password

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_admin(db: Session, username: str, email: str, password: str):
    hashed = hash_password(password)
    user = User(username=username, email=email, password=hashed, role="admin")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
