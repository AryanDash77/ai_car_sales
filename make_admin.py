from db.database import SessionLocal
from db.models import User

# Open a connection to your local database
db = SessionLocal()

# Search for your specific user account by the email you signed up with
# (Change the email below to the exact one you used)
user_email = "aryan@example.com" 
user = db.query(User).filter(User.email == user_email).first()

if user:
    user.role = "admin"
    db.commit()
    print(f"Success! {user.name} is now an admin.")
else:
    print("User not found. Check the email address.")

db.close()

