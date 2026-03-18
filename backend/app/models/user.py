from sqlalchemy import Column, String, Boolean, DateTime
from app.models.base import Base, generate_uuid, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    employee_id = Column(String(50), unique=True, nullable=False, index=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    password_hash = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<User {self.employee_id}>"
