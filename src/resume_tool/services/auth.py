import bcrypt
from sqlalchemy.orm import Session
from models import User

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_user(db: Session, username, password):
    existing = db.query(User).filter(User.username == username).first()
    if existing: return None
    hashed = get_password_hash(password)
    db_user = User(username=username, password_hash=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def login_user(db: Session, username, password):
    user = db.query(User).filter(User.username == username).first()
    if not user: return None
    if not verify_password(password, user.password_hash): return None
    return user

def save_user_draft(db: Session, user_id, data):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.saved_name = data.get('name')
        user.saved_email = data.get('email')
        user.saved_phone = data.get('phone')
        user.saved_linkedin = data.get('linkedin')
        user.saved_summary = data.get('summary')
        user.saved_experience = data.get('experience')
        user.saved_skills = data.get('skills')
        user.saved_references = data.get('references')
        user.saved_role = data.get('role')
        db.commit()