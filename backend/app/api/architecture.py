from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from app.models.base import get_db
from app.models import Module, Feature, FeatureModule, DataFlow, ResponsibilityField, ResponsibilityFieldFeature
from app.schemas import (
    ModuleCreate, ModuleUpdate, ModuleResponse, ModuleTreeResponse,
    FeatureCreate, FeatureUpdate, FeatureModulesUpdate, FeatureResponse, FeatureTreeResponse,
    DataFlowCreate, DataFlowResponse,
    ResponsibilityFieldCreate, ResponsibilityFieldUpdate, FieldFeaturesUpdate,
    ResponsibilityFieldResponse, ResponsibilityFieldDetailResponse,
    MermaidGraphResponse
)

router = APIRouter()


@router.post("/modules", response_model=ModuleResponse)
async def create_module(module: ModuleCreate, db: Session = Depends(get_db)):
    if module.parent_id:
        parent = db.query(Module).filter(Module.id == module.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="父模块不存在")
    
    db_module = Module(**module.dict())
    db.add(db_module)
    db.commit()
    db.refresh(db_module)
    return db_module


@router.get("/modules", response_model=List[ModuleResponse])
async def list_modules(db: Session = Depends(get_db)):
    return db.query(Module).all()


@router.get("/modules/tree", response_model=List[ModuleTreeResponse])
async def get_module_tree(db: Session = Depends(get_db)):
    root_modules = db.query(Module).filter(Module.parent_id == None).all()
    
    def build_tree(module):
        children = db.query(Module).filter(Module.parent_id == module.id).all()
        return ModuleTreeResponse(
            **{c.name: getattr(module, c.name) for c in module.__table__.columns},
            children=[build_tree(c) for c in children]
        )
    
    return [build_tree(m) for m in root_modules]


@router.put("/modules/{module_id}", response_model=ModuleResponse)
async def update_module(
    module_id: str,
    module: ModuleUpdate,
    db: Session = Depends(get_db)
):
    db_module = db.query(Module).filter(Module.id == module_id).first()
    if not db_module:
        raise HTTPException(status_code=404, detail="模块不存在")
    
    if module.parent_id:
        parent = db.query(Module).filter(Module.id == module.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="父模块不存在")
    
    update_data = module.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_module, key, value)
    
    db.commit()
    db.refresh(db_module)
    return db_module


@router.delete("/modules/{module_id}")
async def delete_module(module_id: str, db: Session = Depends(get_db)):
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="模块不存在")
    
    db.delete(module)
    db.commit()
    return {"message": "删除成功"}


@router.post("/features", response_model=FeatureResponse)
async def create_feature(feature: FeatureCreate, db: Session = Depends(get_db)):
    if feature.parent_id:
        parent = db.query(Feature).filter(Feature.id == feature.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="父功能不存在")
    
    db_feature = Feature(name=feature.name, parent_id=feature.parent_id)
    db.add(db_feature)
    db.commit()
    db.refresh(db_feature)
    
    for module_id in feature.dependent_module_ids:
        module = db.query(Module).filter(Module.id == module_id).first()
        if module:
            db_fm = FeatureModule(feature_id=db_feature.id, module_id=module_id)
            db.add(db_fm)
    
    db.commit()
    return db_feature


@router.get("/features", response_model=List[FeatureResponse])
async def list_features(db: Session = Depends(get_db)):
    return db.query(Feature).all()


@router.get("/features/tree", response_model=List[FeatureTreeResponse])
async def get_feature_tree(db: Session = Depends(get_db)):
    root_features = db.query(Feature).filter(Feature.parent_id == None).all()
    
    def build_tree(feature):
        children = db.query(Feature).filter(Feature.parent_id == feature.id).all()
        dependent_modules = [fm.module_id for fm in db.query(FeatureModule).filter(FeatureModule.feature_id == feature.id).all()]
        return FeatureTreeResponse(
            **{c.name: getattr(feature, c.name) for c in feature.__table__.columns},
            children=[build_tree(c) for c in children],
            dependent_modules=dependent_modules
        )
    
    return [build_tree(f) for f in root_features]


@router.put("/features/{feature_id}", response_model=FeatureResponse)
async def update_feature(
    feature_id: str,
    feature: FeatureUpdate,
    db: Session = Depends(get_db)
):
    db_feature = db.query(Feature).filter(Feature.id == feature_id).first()
    if not db_feature:
        raise HTTPException(status_code=404, detail="功能不存在")
    
    if feature.parent_id:
        parent = db.query(Feature).filter(Feature.id == feature.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="父功能不存在")
    
    update_data = feature.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_feature, key, value)
    
    db.commit()
    db.refresh(db_feature)
    return db_feature


@router.post("/features/{feature_id}/modules")
async def add_feature_modules(
    feature_id: str,
    modules: FeatureModulesUpdate,
    db: Session = Depends(get_db)
):
    feature = db.query(Feature).filter(Feature.id == feature_id).first()
    if not feature:
        raise HTTPException(status_code=404, detail="功能不存在")
    
    added_count = 0
    for module_id in modules.module_ids:
        module = db.query(Module).filter(Module.id == module_id).first()
        if module:
            existing = db.query(FeatureModule).filter(
                FeatureModule.feature_id == feature_id,
                FeatureModule.module_id == module_id
            ).first()
            
            if not existing:
                db_fm = FeatureModule(feature_id=feature_id, module_id=module_id)
                db.add(db_fm)
                added_count += 1
    
    db.commit()
    return {"message": f"已关联 {added_count} 个模块"}


@router.delete("/features/{feature_id}/modules/{module_id}")
async def remove_feature_module(
    feature_id: str,
    module_id: str,
    db: Session = Depends(get_db)
):
    fm = db.query(FeatureModule).filter(
        FeatureModule.feature_id == feature_id,
        FeatureModule.module_id == module_id
    ).first()
    
    if not fm:
        raise HTTPException(status_code=404, detail="关联不存在")
    
    db.delete(fm)
    db.commit()
    return {"message": "已取消关联"}


@router.delete("/features/{feature_id}")
async def delete_feature(feature_id: str, db: Session = Depends(get_db)):
    feature = db.query(Feature).filter(Feature.id == feature_id).first()
    if not feature:
        raise HTTPException(status_code=404, detail="功能不存在")
    
    db.delete(feature)
    db.commit()
    return {"message": "删除成功"}


@router.post("/data-flows", response_model=DataFlowResponse)
async def create_data_flow(data_flow: DataFlowCreate, db: Session = Depends(get_db)):
    feature = db.query(Feature).filter(Feature.id == data_flow.feature_id).first()
    if not feature:
        raise HTTPException(status_code=404, detail="功能不存在")
    
    from_module = db.query(Module).filter(Module.id == data_flow.from_module_id).first()
    to_module = db.query(Module).filter(Module.id == data_flow.to_module_id).first()
    
    if not from_module or not to_module:
        raise HTTPException(status_code=404, detail="模块不存在")
    
    db_df = DataFlow(**data_flow.dict())
    db.add(db_df)
    db.commit()
    db.refresh(db_df)
    return db_df


@router.post("/responsibility-fields", response_model=ResponsibilityFieldResponse)
async def create_responsibility_field(field: ResponsibilityFieldCreate, db: Session = Depends(get_db)):
    db_field = ResponsibilityField(
        name=field.name,
        group_id=field.group_id,
        owner_id=field.owner_id,
        backup_owner_id=field.backup_owner_id
    )
    db.add(db_field)
    db.commit()
    db.refresh(db_field)
    
    for feature_id in field.feature_ids:
        feature = db.query(Feature).filter(Feature.id == feature_id).first()
        if feature:
            db_rf = ResponsibilityFieldFeature(field_id=db_field.id, feature_id=feature_id)
            db.add(db_rf)
    
    db.commit()
    return db_field


@router.get("/responsibility-fields", response_model=List[ResponsibilityFieldResponse])
async def list_responsibility_fields(db: Session = Depends(get_db)):
    return db.query(ResponsibilityField).all()


@router.get("/responsibility-fields/{field_id}", response_model=ResponsibilityFieldDetailResponse)
async def get_responsibility_field(field_id: str, db: Session = Depends(get_db)):
    field = db.query(ResponsibilityField).filter(ResponsibilityField.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="责任田不存在")
    
    features = [f.feature_id for f in field.features]
    return ResponsibilityFieldDetailResponse(
        **{c.name: getattr(field, c.name) for c in field.__table__.columns},
        features=features
    )


@router.put("/responsibility-fields/{field_id}", response_model=ResponsibilityFieldResponse)
async def update_responsibility_field(
    field_id: str,
    field: ResponsibilityFieldUpdate,
    db: Session = Depends(get_db)
):
    db_field = db.query(ResponsibilityField).filter(ResponsibilityField.id == field_id).first()
    if not db_field:
        raise HTTPException(status_code=404, detail="责任田不存在")
    
    update_data = field.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_field, key, value)
    
    db.commit()
    db.refresh(db_field)
    return db_field


@router.post("/responsibility-fields/{field_id}/features")
async def add_field_features(
    field_id: str,
    features: FieldFeaturesUpdate,
    db: Session = Depends(get_db)
):
    field = db.query(ResponsibilityField).filter(ResponsibilityField.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="责任田不存在")
    
    added_count = 0
    for feature_id in features.feature_ids:
        feature = db.query(Feature).filter(Feature.id == feature_id).first()
        if feature:
            existing = db.query(ResponsibilityFieldFeature).filter(
                ResponsibilityFieldFeature.field_id == field_id,
                ResponsibilityFieldFeature.feature_id == feature_id
            ).first()
            
            if not existing:
                db_rf = ResponsibilityFieldFeature(field_id=field_id, feature_id=feature_id)
                db.add(db_rf)
                added_count += 1
    
    db.commit()
    return {"message": f"已关联 {added_count} 个功能"}


@router.delete("/responsibility-fields/{field_id}/features/{feature_id}")
async def remove_field_feature(
    field_id: str,
    feature_id: str,
    db: Session = Depends(get_db)
):
    rf = db.query(ResponsibilityFieldFeature).filter(
        ResponsibilityFieldFeature.field_id == field_id,
        ResponsibilityFieldFeature.feature_id == feature_id
    ).first()
    
    if not rf:
        raise HTTPException(status_code=404, detail="关联不存在")
    
    db.delete(rf)
    db.commit()
    return {"message": "已取消关联"}


@router.delete("/responsibility-fields/{field_id}")
async def delete_responsibility_field(field_id: str, db: Session = Depends(get_db)):
    field = db.query(ResponsibilityField).filter(ResponsibilityField.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="责任田不存在")
    
    db.delete(field)
    db.commit()
    return {"message": "删除成功"}


@router.get("/modules/mermaid", response_model=MermaidGraphResponse)
async def export_modules_mermaid(db: Session = Depends(get_db)):
    modules = db.query(Module).all()
    
    lines = ["graph TD"]
    for module in modules:
        if module.parent_id:
            parent = db.query(Module).filter(Module.id == module.parent_id).first()
            if parent:
                lines.append(f"    {parent.name}[{parent.name}] --> {module.name}[{module.name}]")
        else:
            lines.append(f"    {module.name}[{module.name}]")
    
    return MermaidGraphResponse(
        graph_type="module",
        mermaid_code="\n".join(lines)
    )


@router.get("/features/mermaid", response_model=MermaidGraphResponse)
async def export_features_mermaid(db: Session = Depends(get_db)):
    features = db.query(Feature).all()
    
    lines = ["graph TD"]
    for feature in features:
        if feature.parent_id:
            parent = db.query(Feature).filter(Feature.id == feature.parent_id).first()
            if parent:
                lines.append(f"    {parent.name}[{parent.name}] --> {feature.name}[{feature.name}]")
        else:
            lines.append(f"    {feature.name}[{feature.name}]")
    
    return MermaidGraphResponse(
        graph_type="feature",
        mermaid_code="\n".join(lines)
    )
