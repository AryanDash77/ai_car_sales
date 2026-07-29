from uuid import uuid4

from db.database import SessionLocal, init_db
from modules.user_module import register_user, authenticate_user

init_db()
db = SessionLocal()

email = f"aryan_{uuid4().hex[:8]}@test.com"
user = register_user(db, "Aryan Dash", email, "test123")
print("Registered:", user.name, user.email)

result = authenticate_user(db, email, "test123")
print("Login success:", result is not None)

db.close()