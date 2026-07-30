from datetime import datetime
from sqlalchemy.orm import Session

from db.models import Order, TestDrive, Car
from modules.inventory_module import decrement_stock

MAX_PENDING_TEST_DRIVES = 3


def book_test_drive(db: Session, user_id: int, car_id: int, slot_datetime: datetime) -> TestDrive:
    """
    Books a test drive for a customer.
    Enforces the business rule: max 3 pending test-drive bookings per customer.
    """
    car = db.query(Car).filter(Car.id == car_id).first()
    if car is None:
        raise ValueError(f"No car found with id {car_id}.")
    if car.stock_qty <= 0:
        raise ValueError(f"{car.brand} {car.model} is currently out of stock.")

    pending_count = (
        db.query(TestDrive)
        .filter(TestDrive.user_id == user_id, TestDrive.status == "booked")
        .count()
    )
    if pending_count >= MAX_PENDING_TEST_DRIVES:
        raise ValueError(
            f"You already have {MAX_PENDING_TEST_DRIVES} pending test drives. "
            "Please complete or cancel one before booking another."
        )

    booking = TestDrive(
        user_id=user_id,
        car_id=car_id,
        slot_datetime=slot_datetime,
        status="booked",
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def cancel_test_drive(db: Session, test_drive_id: int) -> TestDrive:
    """Cancels a booked test drive."""
    booking = db.query(TestDrive).filter(TestDrive.id == test_drive_id).first()
    if booking is None:
        raise ValueError(f"No test drive found with id {test_drive_id}.")

    booking.status = "cancelled"
    db.commit()
    db.refresh(booking)
    return booking


def list_test_drives_for_user(db: Session, user_id: int) -> list[TestDrive]:
    """Returns all test drive bookings for a given customer."""
    return db.query(TestDrive).filter(TestDrive.user_id == user_id).all()


def place_order(db: Session, user_id: int, car_id: int) -> Order:
    """
    Places a purchase order for a car and decrements inventory stock.
    Order status starts as 'pending' — actual payment is out of scope for now.
    """
    car = db.query(Car).filter(Car.id == car_id).first()
    if car is None:
        raise ValueError(f"No car found with id {car_id}.")
    if car.stock_qty <= 0:
        raise ValueError(f"{car.brand} {car.model} is out of stock.")

    order = Order(user_id=user_id, car_id=car_id, status="pending")
    db.add(order)

    # Reduce stock immediately to prevent overselling while order is pending
    decrement_stock(db, car_id, quantity=1)

    db.commit()
    db.refresh(order)
    return order


def update_order_status(db: Session, order_id: int, status: str) -> Order:
    """
    Updates an order's status. Used by admin for manual follow-up
    (e.g. 'pending' -> 'confirmed' or 'cancelled').
    """
    valid_statuses = {"pending", "confirmed", "cancelled"}
    if status not in valid_statuses:
        raise ValueError(f"Status must be one of {valid_statuses}.")

    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise ValueError(f"No order found with id {order_id}.")

    order.status = status
    db.commit()
    db.refresh(order)
    return order


def list_orders_for_user(db: Session, user_id: int) -> list[Order]:
    """Returns all orders placed by a given customer."""
    return db.query(Order).filter(Order.user_id == user_id).all()


def list_all_orders(db: Session) -> list[Order]:
    """Returns every order in the system — used by the admin module."""
    return db.query(Order).all()
print(aryan)
