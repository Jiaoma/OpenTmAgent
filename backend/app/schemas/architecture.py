from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ModuleBase(BaseModel):
    name: str
    parent_id: Optional[str] = None


class ModuleCreate(ModuleBase):
    pass


class ModuleResponse(ModuleBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ModuleTreeResponse(ModuleResponse):
    children: List["ModuleTreeResponse"] = []


class FeatureBase(BaseModel):
    name: str
    parent_id: Optional[str] = None


class FeatureCreate(FeatureBase):
    dependent_module_ids: List[str] = []


class FeatureResponse(FeatureBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FeatureTreeResponse(FeatureResponse):
    children: List["FeatureTreeResponse"] = []
    dependent_modules: List[str] = []


class DataFlowBase(BaseModel):
    from_module_id: str
    to_module_id: str
    order: int
    description: Optional[str] = None


class DataFlowCreate(DataFlowBase):
    feature_id: str


class DataFlowResponse(DataFlowBase):
    id: str
    feature_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResponsibilityFieldBase(BaseModel):
    name: str
    group_id: Optional[str] = None
    owner_id: Optional[str] = None
    backup_owner_id: Optional[str] = None


class ResponsibilityFieldCreate(ResponsibilityFieldBase):
    feature_ids: List[str] = []


class ResponsibilityFieldResponse(ResponsibilityFieldBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResponsibilityFieldDetailResponse(ResponsibilityFieldResponse):
    features: List[str] = []


class MermaidGraphResponse(BaseModel):
    graph_type: str
    mermaid_code: str
