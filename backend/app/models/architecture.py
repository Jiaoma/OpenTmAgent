from sqlalchemy import Column, String, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from app.models.base import Base, generate_uuid, TimestampMixin


class Module(Base, TimestampMixin):
    __tablename__ = "modules"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    parent_id = Column(String(36), ForeignKey("modules.id"), nullable=True)
    
    parent = relationship("Module", remote_side=[id], backref="children")
    feature_dependencies = relationship("FeatureModule", back_populates="module")
    
    def __repr__(self):
        return f"<Module {self.name}>"


class Feature(Base, TimestampMixin):
    __tablename__ = "features"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    parent_id = Column(String(36), ForeignKey("features.id"), nullable=True)
    
    parent = relationship("Feature", remote_side=[id], backref="children")
    module_dependencies = relationship("FeatureModule", back_populates="feature")
    responsibility_fields = relationship("ResponsibilityFieldFeature", back_populates="feature")
    
    def __repr__(self):
        return f"<Feature {self.name}>"


class FeatureModule(Base, TimestampMixin):
    __tablename__ = "feature_modules"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    feature_id = Column(String(36), ForeignKey("features.id"), nullable=False)
    module_id = Column(String(36), ForeignKey("modules.id"), nullable=False)
    
    feature = relationship("Feature", back_populates="module_dependencies")
    module = relationship("Module", back_populates="feature_dependencies")
    
    def __repr__(self):
        return f"<FeatureModule {self.feature_id}->{self.module_id}>"


class DataFlow(Base, TimestampMixin):
    __tablename__ = "data_flows"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    feature_id = Column(String(36), ForeignKey("features.id"), nullable=False)
    from_module_id = Column(String(36), ForeignKey("modules.id"), nullable=False)
    to_module_id = Column(String(36), ForeignKey("modules.id"), nullable=False)
    order = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    
    feature = relationship("Feature")
    from_module = relationship("Module", foreign_keys=[from_module_id])
    to_module = relationship("Module", foreign_keys=[to_module_id])
    
    def __repr__(self):
        return f"<DataFlow {self.from_module_id}->{self.to_module_id}>"


class ResponsibilityField(Base, TimestampMixin):
    __tablename__ = "responsibility_fields"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    group_id = Column(String(36), ForeignKey("groups.id"), nullable=True)
    owner_id = Column(String(36), ForeignKey("persons.id"), nullable=True)
    backup_owner_id = Column(String(36), ForeignKey("persons.id"), nullable=True)
    
    group = relationship("Group", back_populates="responsibility_fields")
    owner = relationship("Person", foreign_keys=[owner_id], back_populates="responsibility_fields")
    backup_owner = relationship("Person", foreign_keys=[backup_owner_id])
    features = relationship("ResponsibilityFieldFeature", back_populates="responsibility_field")
    
    def __repr__(self):
        return f"<ResponsibilityField {self.name}>"


class ResponsibilityFieldFeature(Base, TimestampMixin):
    __tablename__ = "responsibility_field_features"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    field_id = Column(String(36), ForeignKey("responsibility_fields.id"), nullable=False)
    feature_id = Column(String(36), ForeignKey("features.id"), nullable=False)
    
    responsibility_field = relationship("ResponsibilityField", back_populates="features")
    feature = relationship("Feature", back_populates="responsibility_fields")
    
    def __repr__(self):
        return f"<ResponsibilityFieldFeature {self.field_id}->{self.feature_id}>"
