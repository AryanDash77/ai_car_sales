from sqlalchemy.orm import Session
from sqlalchemy import and_

from db.models import Car


def add_car(
    db: Session,
    brand: str,
    model: str,
    year: int,
    price: float,
    fuel_type: str = None,
    body_type: str = None,
    mileage: float = None,
    image_url: str = None,
    stock_qty: int = 0,
) -> Car:
    """Adds a new car to the inventory. Used by the admin module."""
    if not brand or not model or price is None:
        raise ValueError("Brand, model, and price are required.")
    if price < 0 or stock_qty < 0:
        raise ValueError("Price and stock quantity cannot be negative.")

    car = Car(
        brand=brand.strip(),
        model=model.strip(),
        year=year,
        price=price,
        fuel_type=fuel_type,
        body_type=body_type,
        mileage=mileage,
        image_url=image_url,
        stock_qty=stock_qty,
    )
    db.add(car)
    db.commit()
    db.refresh(car)
    return car


def update_car(db: Session, car_id: int, **fields) -> Car:
    """
    Updates one or more fields of an existing car.
    Usage: update_car(db, 3, price=1250000, stock_qty=4)
    """
    car = db.query(Car).filter(Car.id == car_id).first()
    if car is None:
        raise ValueError(f"No car found with id {car_id}.")

    for key, value in fields.items():
        if not hasattr(car, key):
            raise ValueError(f"Car has no field '{key}'.")
        setattr(car, key, value)

    db.commit()
    db.refresh(car)
    return car


def delete_car(db: Session, car_id: int) -> None:
    """Removes a car from inventory entirely."""
    car = db.query(Car).filter(Car.id == car_id).first()
    if car is None:
        raise ValueError(f"No car found with id {car_id}.")
    db.delete(car)
    db.commit()


def get_car_by_id(db: Session, car_id: int) -> Car | None:
    """Fetches a single car by ID — used by 'View Car Details'."""
    return db.query(Car).filter(Car.id == car_id).first()


def search_cars(
    db: Session,
    brand: str = None,
    body_type: str = None,
    fuel_type: str = None,
    min_price: float = None,
    max_price: float = None,
    only_in_stock: bool = True,
) -> list[Car]:
    """
    Returns cars matching the given filters. All filters are optional —
    calling search_cars(db) with no args returns everything in stock.
    """
    query = db.query(Car)
    conditions = []

    if brand:
        conditions.append(Car.brand.ilike(f"%{brand}%"))
    if body_type:
        conditions.append(Car.body_type == body_type)
    if fuel_type:
        conditions.append(Car.fuel_type == fuel_type)
    if min_price is not None:
        conditions.append(Car.price >= min_price)
    if max_price is not None:
        conditions.append(Car.price <= max_price)
    if only_in_stock:
        conditions.append(Car.stock_qty > 0)

    if conditions:
        query = query.filter(and_(*conditions))

    return query.all()


def list_all_cars(db: Session) -> list[Car]:
    """Returns every car, including out-of-stock ones — used by the admin dashboard."""
    return db.query(Car).all()


def decrement_stock(db: Session, car_id: int, quantity: int = 1) -> Car:
    """Reduces stock when an order is placed. Raises if not enough stock."""
    car = db.query(Car).filter(Car.id == car_id).first()
    if car is None:
        raise ValueError(f"No car found with id {car_id}.")
    if car.stock_qty < quantity:
        raise ValueError(f"Insufficient stock for {car.brand} {car.model}.")

    car.stock_qty -= quantity
    db.commit()
    db.refresh(car)
    return car


print("Inventory module , some changes.")