from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.models.base import get_db
from app.models import (
    Version, Iteration, Task, TaskPerson, TaskTester, TaskRelation,
    TaskStatus, TaskRelationType, Person
)
from app.schemas import (
    VersionCreate, VersionResponse, VersionDetailResponse,
    IterationCreate, IterationResponse, IterationDetailResponse,
    TaskCreate, TaskUpdate, TaskResponse, TaskDetailResponse,
    TaskGraphResponse, TaskGraphNode, TaskGraphEdge,
    CriticalPathResponse, MaxLoadPersonResponse,
    GanttResponse, GanttTask,
    CompletionStatsResponse, PersonCompletionStats
)

router = APIRouter()


@router.post("/versions", response_model=VersionResponse)
async def create_version(version: VersionCreate, db: Session = Depends(get_db)):
    existing = db.query(Version).filter(Version.name == version.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="版本名称已存在")
    
    db_version = Version(**version.dict())
    db.add(db_version)
    db.commit()
    db.refresh(db_version)
    return db_version


@router.get("/versions", response_model=List[VersionResponse])
async def list_versions(db: Session = Depends(get_db)):
    return db.query(Version).all()


@router.get("/versions/{version_id}", response_model=VersionDetailResponse)
async def get_version(version_id: str, db: Session = Depends(get_db)):
    version = db.query(Version).filter(Version.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="版本不存在")
    
    iterations = [i.id for i in version.iterations]
    return VersionDetailResponse(
        **{c.name: getattr(version, c.name) for c in version.__table__.columns},
        iterations=iterations
    )


@router.delete("/versions/{version_id}")
async def delete_version(version_id: str, db: Session = Depends(get_db)):
    version = db.query(Version).filter(Version.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="版本不存在")
    
    db.delete(version)
    db.commit()
    return {"message": "删除成功"}


@router.post("/iterations", response_model=IterationResponse)
async def create_iteration(iteration: IterationCreate, db: Session = Depends(get_db)):
    version = db.query(Version).filter(Version.id == iteration.version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="版本不存在")
    
    db_iteration = Iteration(**iteration.dict())
    db.add(db_iteration)
    db.commit()
    db.refresh(db_iteration)
    return db_iteration


@router.get("/iterations", response_model=List[IterationResponse])
async def list_iterations(version_id: str = None, db: Session = Depends(get_db)):
    query = db.query(Iteration)
    if version_id:
        query = query.filter(Iteration.version_id == version_id)
    return query.all()


@router.get("/iterations/{iteration_id}", response_model=IterationDetailResponse)
async def get_iteration(iteration_id: str, db: Session = Depends(get_db)):
    iteration = db.query(Iteration).filter(Iteration.id == iteration_id).first()
    if not iteration:
        raise HTTPException(status_code=404, detail="迭代不存在")
    
    tasks = [t.id for t in iteration.tasks]
    return IterationDetailResponse(
        **{c.name: getattr(iteration, c.name) for c in iteration.__table__.columns},
        tasks=tasks
    )


@router.post("/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    iteration = db.query(Iteration).filter(Iteration.id == task.iteration_id).first()
    if not iteration:
        raise HTTPException(status_code=404, detail="迭代不存在")
    
    if task.start_date > task.end_date:
        raise HTTPException(status_code=400, detail="起始时间不能晚于终止时间")
    
    if task.end_date > iteration.end_date:
        raise HTTPException(status_code=400, detail="任务终止时间晚于迭代终止时间")
    
    for dep in task.dependencies:
        dep_task = db.query(Task).filter(Task.id == dep.related_task_id).first()
        if not dep_task:
            raise HTTPException(status_code=400, detail=f"依赖任务 {dep.related_task_id} 不存在")
        if dep.relation_type == TaskRelationType.DEPENDS_ON and dep_task.end_date > task.end_date:
            raise HTTPException(status_code=400, detail=f"依赖任务 {dep.related_task_id} 终止时间晚于当前任务")
    
    db_task = Task(
        iteration_id=task.iteration_id,
        name=task.name,
        start_date=task.start_date,
        end_date=task.end_date,
        man_month=task.man_month,
        design_doc_url=task.design_doc_url
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    if task.feature_owner:
        db_fo = TaskPerson(
            task_id=db_task.id,
            person_id=task.feature_owner.person_id,
            person_name=task.feature_owner.person_name,
            role="feature_owner"
        )
        db.add(db_fo)
    
    for dev in task.dev_owners:
        db_dev = TaskPerson(
            task_id=db_task.id,
            person_id=dev.person_id,
            person_name=dev.person_name,
            role="dev_owner"
        )
        db.add(db_dev)
    
    for tester_name in task.testers:
        db_tester = TaskTester(task_id=db_task.id, name=tester_name)
        db.add(db_tester)
    
    for dep in task.dependencies:
        db_dep = TaskRelation(
            task_id=db_task.id,
            related_task_id=dep.related_task_id,
            relation_type=dep.relation_type
        )
        db.add(db_dep)
    
    db.commit()
    return db_task


@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(iteration_id: str = None, db: Session = Depends(get_db)):
    query = db.query(Task)
    if iteration_id:
        query = query.filter(Task.iteration_id == iteration_id)
    return query.all()


@router.get("/tasks/{task_id}", response_model=TaskDetailResponse)
async def get_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    feature_owner = None
    dev_owners = []
    for tp in db.query(TaskPerson).filter(TaskPerson.task_id == task_id).all():
        if tp.role == "feature_owner":
            feature_owner = {"person_id": tp.person_id, "person_name": tp.person_name}
        elif tp.role == "dev_owner":
            dev_owners.append({"person_id": tp.person_id, "person_name": tp.person_name})
    
    testers = [t.name for t in task.testers]
    dependencies = [{"related_task_id": d.related_task_id, "relation_type": d.relation_type} for d in task.dependencies]
    
    return TaskDetailResponse(
        **{c.name: getattr(task, c.name) for c in task.__table__.columns},
        feature_owner=feature_owner,
        dev_owners=dev_owners,
        testers=testers,
        dependencies=dependencies
    )


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task: TaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    update_data = task.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    db.delete(task)
    db.commit()
    return {"message": "删除成功"}


@router.get("/tasks/graph", response_model=TaskGraphResponse)
async def get_task_graph(
    version_ids: str = None,
    iteration_ids: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Task)
    
    if iteration_ids:
        ids = iteration_ids.split(",")
        query = query.filter(Task.iteration_id.in_(ids))
    elif version_ids:
        v_ids = version_ids.split(",")
        iteration_list = db.query(Iteration.id).filter(Iteration.version_id.in_(v_ids)).all()
        i_ids = [i[0] for i in iteration_list]
        query = query.filter(Task.iteration_id.in_(i_ids))
    
    tasks = query.all()
    
    nodes = []
    edges = []
    
    for task in tasks:
        nodes.append(TaskGraphNode(
            id=task.id,
            name=task.name,
            start_date=task.start_date,
            end_date=task.end_date,
            status=task.status
        ))
        
        for dep in task.dependencies:
            edges.append(TaskGraphEdge(
                source=dep.related_task_id,
                target=task.id,
                relation_type=dep.relation_type
            ))
    
    return TaskGraphResponse(nodes=nodes, edges=edges)


@router.get("/tasks/critical-path", response_model=CriticalPathResponse)
async def get_critical_path(iteration_ids: str, db: Session = Depends(get_db)):
    ids = iteration_ids.split(",")
    tasks = db.query(Task).filter(Task.iteration_id.in_(ids)).all()
    
    if not tasks:
        return CriticalPathResponse(path=[], total_duration=0)
    
    path = [t.id for t in sorted(tasks, key=lambda x: x.end_date, reverse=True)[:3]]
    total_duration = max((t.end_date - t.start_date).days for t in tasks) if tasks else 0
    
    return CriticalPathResponse(path=path, total_duration=total_duration)


@router.get("/tasks/max-load-person", response_model=MaxLoadPersonResponse)
async def get_max_load_person(iteration_ids: str, db: Session = Depends(get_db)):
    ids = iteration_ids.split(",")
    tasks = db.query(Task).filter(Task.iteration_id.in_(ids)).all()
    
    person_loads = {}
    for task in tasks:
        task_persons = db.query(TaskPerson).filter(TaskPerson.task_id == task.id).all()
        for tp in task_persons:
            if tp.person_id:
                if tp.person_id not in person_loads:
                    person = db.query(Person).filter(Person.id == tp.person_id).first()
                    person_loads[tp.person_id] = {"name": person.name if person else "Unknown", "load": 0}
                person_loads[tp.person_id]["load"] += task.man_month
    
    if not person_loads:
        return MaxLoadPersonResponse(person_id="", person_name="", load=0)
    
    max_person = max(person_loads.items(), key=lambda x: x[1]["load"])
    return MaxLoadPersonResponse(
        person_id=max_person[0],
        person_name=max_person[1]["name"],
        load=max_person[1]["load"]
    )


@router.get("/tasks/gantt", response_model=GanttResponse)
async def get_gantt_chart(iteration_id: str, db: Session = Depends(get_db)):
    iteration = db.query(Iteration).filter(Iteration.id == iteration_id).first()
    if not iteration:
        raise HTTPException(status_code=404, detail="迭代不存在")
    
    tasks = db.query(Task).filter(Task.iteration_id == iteration_id).all()
    
    gantt_tasks = []
    for task in tasks:
        dependencies = [d.related_task_id for d in task.dependencies if d.relation_type == TaskRelationType.DEPENDS_ON]
        gantt_tasks.append(GanttTask(
            id=task.id,
            name=task.name,
            start_date=task.start_date,
            end_date=task.end_date,
            status=task.status,
            dependencies=dependencies
        ))
    
    return GanttResponse(
        iteration_id=iteration_id,
        iteration_name=iteration.name,
        tasks=gantt_tasks
    )


@router.get("/completion-stats", response_model=CompletionStatsResponse)
async def get_completion_stats(
    version_id: str,
    iteration_id: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Task).join(Iteration).filter(Iteration.version_id == version_id)
    if iteration_id:
        query = query.filter(Task.iteration_id == iteration_id)
    
    tasks = query.all()
    
    person_stats = {}
    for task in tasks:
        task_persons = db.query(TaskPerson).filter(TaskPerson.task_id == task.id).all()
        for tp in task_persons:
            if tp.person_id and tp.person_id not in person_stats:
                person = db.query(Person).filter(Person.id == tp.person_id).first()
                person_stats[tp.person_id] = {
                    "person_name": person.name if person else "Unknown",
                    "total_tasks": 0,
                    "completed_tasks": 0,
                    "uncompleted_tasks": 0,
                    "early_count": 0,
                    "on_time_count": 0,
                    "slight_delay_count": 0,
                    "severe_delay_count": 0
                }
            
            if tp.person_id:
                person_stats[tp.person_id]["total_tasks"] += 1
                if task.status == TaskStatus.COMPLETED:
                    person_stats[tp.person_id]["completed_tasks"] += 1
                    if task.actual_end_date:
                        if task.actual_end_date < task.end_date:
                            person_stats[tp.person_id]["early_count"] += 1
                        elif task.actual_end_date == task.end_date:
                            person_stats[tp.person_id]["on_time_count"] += 1
                        elif (task.actual_end_date - task.end_date).days <= 1:
                            person_stats[tp.person_id]["slight_delay_count"] += 1
                        else:
                            person_stats[tp.person_id]["severe_delay_count"] += 1
                else:
                    person_stats[tp.person_id]["uncompleted_tasks"] += 1
    
    stats = [
        PersonCompletionStats(person_id=pid, **pdata)
        for pid, pdata in person_stats.items()
    ]
    
    return CompletionStatsResponse(
        version_id=version_id,
        iteration_id=iteration_id,
        stats=stats
    )
