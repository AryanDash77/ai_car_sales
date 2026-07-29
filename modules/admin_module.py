from sqlalchemy import func
from sqlalchemy.orm import Session

from db.models import Order, Car


def get_sales_summary(db: Session) -> dict:
    """Returns high-level sales metrics for the admin dashboard."""
    total_orders = db.query(func.count(Order.id)).scalar() or 0

    total_revenue = (
        db.query(func.sum(Car.price))
        .join(Order, Order.car_id == Car.id)
        .filter(Order.status != "cancelled")
        .scalar()
    ) or 0.0

    status_counts = (
        db.query(Order.status, func.count(Order.id))
        .group_by(Order.status)
        .all()
    )

    return {
        "total_orders": total_orders,
        "total_revenue": float(total_revenue),
        "orders_by_status": {status: count for status, count in status_counts},
    }


def get_popular_cars(db: Session, top_n: int = 5) -> list[dict]:
    """Returns the most-ordered cars, ranked by number of orders."""
    results = (
        db.query(Car, func.count(Order.id).label("order_count"))
        .join(Order, Order.car_id == Car.id)
        .group_by(Car.id)
        .order_by(func.count(Order.id).desc())
        .limit(top_n)
        .all()
    )

    return [
        {"car": car, "order_count": order_count}
        for car, order_count in results
    ]


def get_inventory_summary(db: Session) -> dict:
    """Returns a snapshot of current inventory health."""
    total_cars = db.query(func.count(Car.id)).scalar() or 0
    total_stock_units = db.query(func.sum(Car.stock_qty)).scalar() or 0
    out_of_stock_count = db.query(func.count(Car.id)).filter(Car.stock_qty == 0).scalar() or 0

    return {
        "total_car_listings": total_cars,
        "total_stock_units": int(total_stock_units),
        "out_of_stock_count": out_of_stock_count,
    }

