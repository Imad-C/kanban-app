from configparser import ConfigParser
from typing_extensions import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import sessionmaker


config = ConfigParser()
config.read("config.ini")
active_board = config["BOARDS"]["active"]
sql_url = config["PATHS"]["sql"]


class Base(DeclarativeBase):
    """declarative base class"""
    pass

class Task(Base):
    """defining table parameters from class using sqlalchemy ORM"""
    __tablename__ = "task"

    name: Mapped[str] = mapped_column(primary_key=True)
    board: Mapped[str] = mapped_column(primary_key=True)
    number: Mapped[int] 
    description: Mapped[Optional[str]]
    date: Mapped[str] 
    status: Mapped[str] 

    def __repr__(self):
        return f"Task: [{self.number}] {self.name} from Board: {self.board}"
    

def database_init():
    """creating table"""

    engine = create_engine(sql_url, echo=False)
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    pass
