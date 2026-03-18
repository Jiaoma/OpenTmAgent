from sqlalchemy import Column, String, ForeignKey, Text, Enum, Float
from app.models.base import Base, generate_uuid, TimestampMixin
import enum


class UserType(str, enum.Enum):
    ADMIN = "admin"
    VISITOR = "visitor"


class OperationLog(Base, TimestampMixin):
    __tablename__ = "operation_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    user_type = Column(Enum(UserType), nullable=False)
    operation = Column(String(100), nullable=False)
    target_type = Column(String(100), nullable=False)
    target_id = Column(String(36), nullable=True)
    result = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<OperationLog {self.operation}:{self.target_type}>"


class TeamLoadRecord(Base, TimestampMixin):
    __tablename__ = "team_load_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    month = Column(String(7), nullable=False)
    total_load = Column(Float, nullable=False)
    avg_load = Column(Float, nullable=False)
    max_load_person_id = Column(String(36), ForeignKey("persons.id"), nullable=True)
    max_load_value = Column(Float, nullable=True)
    
    def __repr__(self):
        return f"<TeamLoadRecord {self.month}>"
