from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite for dev; swap to MySQL later just by changing this URL
# e.g. "mysql+pymysql://user:password@localhost/car_sales_db"
DATABASE_URL = "sqlite:///car_sales.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # needed only for SQLite + Streamlit
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def get_db():
    """Yields a DB session, auto-closes when done. Use with a context manager."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Creates all tables. Call once at app startup."""
    import db.models  # noqa: ensures models are registered on Base before create_all
    Base.metadata.create_all(bind=engine)

    