from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime


class PersonBase(BaseModel):
    name: str
    employee_id: str
    email: EmailStr
    position: Optional[str] = None
    group_id: Optional[str] = None


class PersonCreate(PersonBase):
    pass


class PersonUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    position: Optional[str] = None
    group_id: Optional[str] = None


class PersonResponse(PersonBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PersonDetailResponse(PersonResponse):
    ability_model: Optional[Dict[str, int]] = None
    current_tasks: List[str] = []
    responsibility_fields: List[str] = []


class AbilityDimensionBase(BaseModel):
    name: str
    description: Optional[str] = None
    level_1_desc: Optional[str] = None
    level_2_desc: Optional[str] = None
    level_3_desc: Optional[str] = None
    level_4_desc: Optional[str] = None
    level_5_desc: Optional[str] = None


class AbilityDimensionCreate(AbilityDimensionBase):
    pass


class AbilityDimensionResponse(AbilityDimensionBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PersonAbilityUpdate(BaseModel):
    dimension_id: str
    score: int


class PersonAbilityModelCreate(BaseModel):
    person_id: str
    abilities: List[PersonAbilityUpdate]


class AbilityRadarData(BaseModel):
    dimensions: List[str]
    scores: List[int]
    person_name: str
