import bcrypt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db.models import User


def _hash_password(plain_password: str) -> str:
    """Hashes a plain-text password using bcrypt. Returns a string safe to store in DB."""
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def _verify_password(plain_password: str, password_hash: str) -> bool:
    """Checks a plain-text password against the stored bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))


def register_user(db: Session, name: str, email: str, password: str, role: str = "customer") -> User:
    """
    Creates a new user record.
    Raises ValueError if the email is already registered or inputs are invalid.
    """
    if not name or not email or not password:
        raise ValueError("Name, email, and password are all required.")

    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters long.")

    new_user = User(
        name=name.strip(),
        email=email.strip().lower(),
        password_hash=_hash_password(password),
        role=role,
    )

    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise ValueError(f"An account with email '{email}' already exists.")

    return new_user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """
    Verifies login credentials.
    Returns the User object if valid, otherwise None.
    """
    user = db.query(User).filter(User.email == email.strip().lower()).first()

    if user is None:
        return None

    if not _verify_password(password, user.password_hash):
        return None

    return user


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Fetches a user by their ID — used to keep session state in Streamlit."""
    return db.query(User).filter(User.id == user_id).first()

