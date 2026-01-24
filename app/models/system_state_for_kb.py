from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from app.core.database import Base

class SystemState(Base):
    __tablename__ = "system_state"

    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[str] = mapped_column(String)
