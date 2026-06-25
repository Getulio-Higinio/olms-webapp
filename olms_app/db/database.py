from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from olms_app.config import DB_PATH

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def get_session():
    return SessionLocal()
