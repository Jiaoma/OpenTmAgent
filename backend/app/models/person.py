from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import Base, generate_uuid, TimestampMixin


class Person(Base, TimestampMixin):
    __tablename__ = "persons"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    employee_id = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    group_id = Column(String(36), ForeignKey("groups.id"), nullable=True)
    position = Column(String(100), nullable=True)
    
    group = relationship("Group", foreign_keys=[group_id], back_populates="members")
    ability_model = relationship("PersonAbilityModel", back_populates="person", uselist=False)
    tasks = relationship("TaskPerson", back_populates="person")
    responsibility_fields = relationship("ResponsibilityField", foreign_keys="ResponsibilityField.owner_id", back_populates="owner")
    
    def __repr__(self):
        return f"<Person {self.name} ({self.employee_id})>"
