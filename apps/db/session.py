from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "postgresql+psycopg://user:password@localhost:5432/mydb"

engine = create_engine(
   DATABASE_URL,
   pool_pre_ping=True,
   pool_size=5,
   max_overflow=10, 
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass