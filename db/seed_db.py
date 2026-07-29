from db.database import SessionLocal
from modules.inventory_module import add_car

def seed_database():
    db = SessionLocal()
    try:
        print("Seeding database with initial car records...")
        
        # Adding a Hatchback under ₹5,00,000 to match your previous search!
        add_car(db, brand="Tata", model="Tiago", year=2023, price=450000.0, fuel_type="Petrol", body_type="Hatchback", stock_qty=5)
        
        # Adding a few more diverse options for testing
        add_car(db, brand="Hyundai", model="Creta", year=2024, price=1200000.0, fuel_type="Diesel", body_type="SUV", stock_qty=2)
        add_car(db, brand="Honda", model="City", year=2023, price=1100000.0, fuel_type="Petrol", body_type="Sedan", stock_qty=3)
        add_car(db, brand="Tata", model="Nexon EV", year=2024, price=1500000.0, fuel_type="Electric", body_type="SUV", stock_qty=1)

        print("Success! Test cars have been added to the inventory.")
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()

    