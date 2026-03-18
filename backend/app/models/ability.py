from sqlalchemy import Column, String, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.models.base import Base, generate_uuid, TimestampMixin


class AbilityDimension(Base, TimestampMixin):
    __tablename__ = "ability_dimensions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    level_1_desc = Column(String(255), nullable=True)
    level_2_desc = Column(String(255), nullable=True)
    level_3_desc = Column(String(255), nullable=True)
    level_4_desc = Column(String(255), nullable=True)
    level_5_desc = Column(String(255), nullable=True)
    
    person_abilities = relationship("PersonAbilityModel", back_populates="dimension")
    
    def __repr__(self):
        return f"<AbilityDimension {self.name}>"


class PersonAbilityModel(Base, TimestampMixin):
    __tablename__ = "person_ability_models"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    person_id = Column(String(36), ForeignKey("persons.id"), nullable=False)
    dimension_id = Column(String(36), ForeignKey("ability_dimensions.id"), nullable=False)
    score = Column(Integer, nullable=False)
    updated_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    person = relationship("Person", back_populates="ability_model")
    dimension = relationship("AbilityDimension", back_populates="person_abilities")
    
    def __repr__(self):
        return f"<PersonAbilityModel {self.person_id}:{self.dimension_id}={self.score}>"
