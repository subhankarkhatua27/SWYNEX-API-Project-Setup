from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column

# from uuid import uuid4
class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    
    # id : Mapped[str]= mapped_column(primary_key=True, default=lambda: str(uuid4()))
    id : Mapped[int]= mapped_column(primary_key=True)
    name : Mapped[str] = mapped_column(nullable=False)
    email : Mapped[str] = mapped_column(nullable=False, unique=True)
    
    
    
