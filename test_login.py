from db.database import SessionLocal
from modules.user_module import register_user, authenticate_user

db = SessionLocal()

user = register_user(db, "Aryan Dash", "aryan@test.com", "test123")
print("Registered:", user.name, user.email)

result = authenticate_user(db, "aryan@test.com", "test123")
print("Login success:", result is not None)

db.close()