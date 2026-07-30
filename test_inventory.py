from db.database import SessionLocal
from modules.inventory_module import add_car, search_cars, update_car

db = SessionLocal()

car = add_car(db, brand="Tata", model="Nexon", year=2024, price=1450000,
              fuel_type="Petrol", body_type="SUV", mileage=17.0, stock_qty=5)
print("Added:", car.brand, car.model, "| Stock:", car.stock_qty)

results = search_cars(db, body_type="SUV")
print("SUV search results:", [f"{c.brand} {c.model}" for c in results])

updated = update_car(db, car.id, price=1400000)
print("Updated price:", updated.price)

db.close()

