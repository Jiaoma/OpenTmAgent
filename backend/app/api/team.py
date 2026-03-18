from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from app.models.base import get_db
from app.models import Person, AbilityDimension, PersonAbilityModel, Group, KeyPerson, KeyPersonType, TaskPerson
from app.schemas import (
    PersonCreate, PersonUpdate, PersonResponse, PersonDetailResponse,
    AbilityDimensionCreate, AbilityDimensionResponse,
    PersonAbilityModelCreate, AbilityRadarData,
    GroupCreate, GroupUpdate, GroupResponse, GroupDetailResponse,
    GroupLoadResponse, GroupLoadCurveResponse, LoadCurvePoint,
    KeyPersonTypeCreate, KeyPersonTypeResponse
)

router = APIRouter()


@router.post("/persons", response_model=PersonResponse)
async def create_person(person: PersonCreate, db: Session = Depends(get_db)):
    existing = db.query(Person).filter(Person.employee_id == person.employee_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="工号已存在")
    
    existing_email = db.query(Person).filter(Person.email == person.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="邮箱已存在")
    
    db_person = Person(**person.dict())
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person


@router.get("/persons", response_model=List[PersonResponse])
async def list_persons(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    persons = db.query(Person).offset(skip).limit(limit).all()
    return persons


@router.get("/persons/{person_id}", response_model=PersonDetailResponse)
async def get_person(person_id: str, db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="人员不存在")
    
    ability_model = {}
    for ab in db.query(PersonAbilityModel).filter(PersonAbilityModel.person_id == person_id).all():
        dim = db.query(AbilityDimension).filter(AbilityDimension.id == ab.dimension_id).first()
        if dim:
            ability_model[dim.name] = ab.score
    
    current_tasks = [tp.task_id for tp in db.query(TaskPerson).filter(TaskPerson.person_id == person_id).all()]
    responsibility_fields = [rf.id for rf in person.responsibility_fields]
    
    return PersonDetailResponse(
        **{c.name: getattr(person, c.name) for c in person.__table__.columns},
        ability_model=ability_model,
        current_tasks=current_tasks,
        responsibility_fields=responsibility_fields
    )


@router.put("/persons/{person_id}", response_model=PersonResponse)
async def update_person(person_id: str, person: PersonUpdate, db: Session = Depends(get_db)):
    db_person = db.query(Person).filter(Person.id == person_id).first()
    if not db_person:
        raise HTTPException(status_code=404, detail="人员不存在")
    
    update_data = person.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_person, key, value)
    
    db.commit()
    db.refresh(db_person)
    return db_person


@router.delete("/persons/{person_id}")
async def delete_person(person_id: str, db: Session = Depends(get_db)):
    db_person = db.query(Person).filter(Person.id == person_id).first()
    if not db_person:
        raise HTTPException(status_code=404, detail="人员不存在")
    
    db.delete(db_person)
    db.commit()
    return {"message": "删除成功"}


@router.post("/ability-dimensions", response_model=AbilityDimensionResponse)
async def create_ability_dimension(dimension: AbilityDimensionCreate, db: Session = Depends(get_db)):
    existing = db.query(AbilityDimension).filter(AbilityDimension.name == dimension.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="能力维度已存在")
    
    db_dimension = AbilityDimension(**dimension.dict())
    db.add(db_dimension)
    db.commit()
    db.refresh(db_dimension)
    return db_dimension


@router.get("/ability-dimensions", response_model=List[AbilityDimensionResponse])
async def list_ability_dimensions(db: Session = Depends(get_db)):
    return db.query(AbilityDimension).all()


@router.put("/persons/{person_id}/ability-model")
async def update_person_ability_model(
    person_id: str,
    model: PersonAbilityModelCreate,
    is_admin: bool = False,
    db: Session = Depends(get_db)
):
    if not is_admin:
        raise HTTPException(status_code=403, detail="仅管理员可修改能力模型")
    
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="人员不存在")
    
    for ability in model.abilities:
        existing = db.query(PersonAbilityModel).filter(
            PersonAbilityModel.person_id == person_id,
            PersonAbilityModel.dimension_id == ability.dimension_id
        ).first()
        
        if existing:
            existing.score = ability.score
        else:
            db_model = PersonAbilityModel(
                person_id=person_id,
                dimension_id=ability.dimension_id,
                score=ability.score
            )
            db.add(db_model)
    
    db.commit()
    return {"message": "能力模型更新成功"}


@router.get("/persons/{person_id}/ability-radar", response_model=AbilityRadarData)
async def get_person_ability_radar(person_id: str, db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="人员不存在")
    
    dimensions = db.query(AbilityDimension).all()
    abilities = db.query(PersonAbilityModel).filter(PersonAbilityModel.person_id == person_id).all()
    
    dim_names = [d.name for d in dimensions]
    scores = []
    for dim in dimensions:
        ab = next((a for a in abilities if a.dimension_id == dim.id), None)
        scores.append(ab.score if ab else 0)
    
    return AbilityRadarData(
        dimensions=dim_names,
        scores=scores,
        person_name=person.name
    )


@router.post("/groups", response_model=GroupResponse)
async def create_group(group: GroupCreate, db: Session = Depends(get_db)):
    existing = db.query(Group).filter(Group.name == group.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="小组名称已存在")
    
    db_group = Group(name=group.name, leader_id=group.leader_id)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    
    for member_id in group.member_ids:
        person = db.query(Person).filter(Person.id == member_id).first()
        if person:
            person.group_id = db_group.id
    
    for kp in group.key_persons:
        db_kp = KeyPerson(group_id=db_group.id, type_id=kp.type_id, person_id=kp.person_id)
        db.add(db_kp)
    
    db.commit()
    return db_group


@router.get("/groups", response_model=List[GroupResponse])
async def list_groups(db: Session = Depends(get_db)):
    return db.query(Group).all()


@router.get("/groups/{group_id}", response_model=GroupDetailResponse)
async def get_group(group_id: str, db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="小组不存在")
    
    members = [m.id for m in group.members]
    key_persons = [{"id": kp.id, "type_id": kp.type_id, "person_id": kp.person_id} for kp in group.key_persons]
    responsibility_fields = [rf.id for rf in group.responsibility_fields]
    
    return GroupDetailResponse(
        **{c.name: getattr(group, c.name) for c in group.__table__.columns},
        members=members,
        key_persons=key_persons,
        responsibility_fields=responsibility_fields
    )


@router.get("/groups/{group_id}/load", response_model=GroupLoadResponse)
async def get_group_load(group_id: str, db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="小组不存在")
    
    member_loads = []
    total_load = 0.0
    
    for member in group.members:
        load = 0.0
        member_loads.append({
            "person_id": member.id,
            "person_name": member.name,
            "load": load
        })
        total_load += load
    
    avg_load = total_load / len(group.members) if group.members else 0.0
    
    return GroupLoadResponse(
        group_id=group_id,
        group_name=group.name,
        total_load=total_load,
        avg_load=avg_load,
        member_loads=member_loads
    )


@router.get("/groups/{group_id}/load-curve", response_model=GroupLoadCurveResponse)
async def get_group_load_curve(group_id: str, db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="小组不存在")
    
    curve = [
        LoadCurvePoint(month="2026-04", load=10.5),
        LoadCurvePoint(month="2026-05", load=12.3),
        LoadCurvePoint(month="2026-06", load=8.7),
    ]
    
    return GroupLoadCurveResponse(
        group_id=group_id,
        group_name=group.name,
        curve=curve
    )


@router.post("/key-person-types", response_model=KeyPersonTypeResponse)
async def create_key_person_type(kpt: KeyPersonTypeCreate, db: Session = Depends(get_db)):
    existing = db.query(KeyPersonType).filter(KeyPersonType.name == kpt.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="关键人物类型已存在")
    
    db_kpt = KeyPersonType(**kpt.dict())
    db.add(db_kpt)
    db.commit()
    db.refresh(db_kpt)
    return db_kpt


@router.get("/key-person-types", response_model=List[KeyPersonTypeResponse])
async def list_key_person_types(db: Session = Depends(get_db)):
    return db.query(KeyPersonType).all()
