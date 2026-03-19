from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class KeyPersonBase(BaseModel):
    type_id: str
    person_id: str


class KeyPersonCreate(KeyPersonBase):
    group_id: str


class KeyPersonResponse(KeyPersonBase):
    id: str
    group_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KeyPersonTypeBase(BaseModel):
    name: str
    description: Optional[str] = None


class KeyPersonTypeCreate(KeyPersonTypeBase):
    pass


class KeyPersonTypeResponse(KeyPersonTypeBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GroupBase(BaseModel):
    name: str
    leader_id: Optional[str] = None


class GroupCreate(GroupBase):
    member_ids: List[str] = []
    key_persons: List[KeyPersonBase] = []


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    leader_id: Optional[str] = None
    member_ids: Optional[List[str]] = None


class GroupMembersUpdate(BaseModel):
    person_ids: List[str]


class GroupResponse(GroupBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GroupDetailResponse(GroupResponse):
    members: List[str] = []
    key_persons: List[dict] = []
    responsibility_fields: List[str] = []


class GroupLoadResponse(BaseModel):
    group_id: str
    group_name: str
    total_load: float
    avg_load: float
    member_loads: List[dict]


class LoadCurvePoint(BaseModel):
    month: str
    load: float


class GroupLoadCurveResponse(BaseModel):
    group_id: str
    group_name: str
    curve: List[LoadCurvePoint]
