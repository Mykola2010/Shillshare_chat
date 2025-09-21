from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


sqlite_file_name = "database.db"
DATABASE_URL = "sqlite:///database.db"

connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

