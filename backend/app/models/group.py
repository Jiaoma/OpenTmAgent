from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base, generate_uuid, TimestampMixin


class KeyPersonType(Base, TimestampMixin):
    __tablename__ = "key_person_types"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    
    key_persons = relationship("KeyPerson", back_populates="key_person_type")
    
    def __repr__(self):
        return f"<KeyPersonType {self.name}>"


class KeyPerson(Base, TimestampMixin):
    __tablename__ = "key_persons"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    group_id = Column(String(36), ForeignKey("groups.id"), nullable=False)
    type_id = Column(String(36), ForeignKey("key_person_types.id"), nullable=False)
    person_id = Column(String(36), ForeignKey("persons.id"), nullable=False)
    
    group = relationship("Group", back_populates="key_persons")
    key_person_type = relationship("KeyPersonType", back_populates="key_persons")
    person = relationship("Person")
    
    def __repr__(self):
        return f"<KeyPerson {self.group_id}:{self.type_id}>"


class Group(Base, TimestampMixin):
    __tablename__ = "groups"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False, unique=True)
    leader_id = Column(String(36), ForeignKey("persons.id"), nullable=True)
    
    leader = relationship("Person", foreign_keys=[leader_id])
    members = relationship("Person", foreign_keys="Person.group_id", back_populates="group")
    key_persons = relationship("KeyPerson", back_populates="group")
    responsibility_fields = relationship("ResponsibilityField", back_populates="group")
    
    def __repr__(self):
        return f"<Group {self.name}>"
