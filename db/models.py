from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="customer")  # "customer" or "admin"
    created_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="user")
    test_drives = relationship("TestDrive", back_populates="user")


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    fuel_type = Column(String(20))       # Petrol / Diesel / Electric / Hybrid
    body_type = Column(String(20))       # Sedan / SUV / Hatchback
    mileage = Column(Float)              # km/l or km range for EVs
    image_url = Column(String(255))
    stock_qty = Column(Integer, default=0)

    @property
    def in_stock(self) -> bool:
        return self.stock_qty > 0


class TestDrive(Base):
    __tablename__ = "test_drives"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    slot_datetime = Column(DateTime, nullable=False)
    status = Column(String(20), default="booked")  # booked / cancelled / completed

    user = relationship("User", back_populates="test_drives")
    car = relationship("Car")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    status = Column(String(20), default="pending")  # pending / confirmed / cancelled
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="orders")
    car = relationship("Car")

    