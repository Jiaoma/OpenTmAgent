from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskRelationType(str, Enum):
    DEPENDS_ON = "depends_on"
    RELATED_TO = "related_to"


class VersionBase(BaseModel):
    name: str
    project_manager: Optional[str] = None
    software_manager: Optional[str] = None
    test_manager: Optional[str] = None


class VersionCreate(VersionBase):
    pass


class VersionResponse(VersionBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VersionDetailResponse(VersionResponse):
    iterations: List[str] = []


class IterationBase(BaseModel):
    name: str
    start_date: date
    end_date: date


class IterationCreate(IterationBase):
    version_id: str


class IterationResponse(IterationBase):
    id: str
    version_id: str
    total_man_month: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IterationDetailResponse(IterationResponse):
    tasks: List[str] = []


class TaskPersonBase(BaseModel):
    person_id: Optional[str] = None
    person_name: Optional[str] = None
    role: str


class TaskPersonCreate(TaskPersonBase):
    pass


class TaskTesterBase(BaseModel):
    name: str


class TaskTesterCreate(TaskTesterBase):
    pass


class TaskRelationBase(BaseModel):
    related_task_id: str
    relation_type: TaskRelationType


class TaskRelationCreate(TaskRelationBase):
    pass


class TaskBase(BaseModel):
    name: str
    start_date: date
    end_date: date
    man_month: float
    design_doc_url: Optional[str] = None


class TaskCreate(TaskBase):
    iteration_id: str
    feature_owner: Optional[TaskPersonBase] = None
    dev_owners: List[TaskPersonBase] = []
    testers: List[str] = []
    dependencies: List[TaskRelationBase] = []


class TaskUpdate(BaseModel):
    name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    man_month: Optional[float] = None
    status: Optional[TaskStatus] = None
    actual_end_date: Optional[date] = None
    design_doc_url: Optional[str] = None


class TaskResponse(TaskBase):
    id: str
    iteration_id: str
    status: TaskStatus
    actual_end_date: Optional[date]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskDetailResponse(TaskResponse):
    feature_owner: Optional[dict] = None
    dev_owners: List[dict] = []
    testers: List[str] = []
    dependencies: List[dict] = []


class TaskGraphNode(BaseModel):
    id: str
    name: str
    start_date: date
    end_date: date
    status: TaskStatus


class TaskGraphEdge(BaseModel):
    source: str
    target: str
    relation_type: TaskRelationType


class TaskGraphResponse(BaseModel):
    nodes: List[TaskGraphNode]
    edges: List[TaskGraphEdge]


class CriticalPathResponse(BaseModel):
    path: List[str]
    total_duration: int


class MaxLoadPersonResponse(BaseModel):
    person_id: str
    person_name: str
    load: float


class GanttTask(BaseModel):
    id: str
    name: str
    start_date: date
    end_date: date
    status: TaskStatus
    dependencies: List[str]


class GanttResponse(BaseModel):
    iteration_id: str
    iteration_name: str
    tasks: List[GanttTask]


class CompletionStatus(str, Enum):
    EARLY = "early"
    ON_TIME = "on_time"
    SLIGHT_DELAY = "slight_delay"
    SEVERE_DELAY = "severe_delay"


class PersonCompletionStats(BaseModel):
    person_id: str
    person_name: str
    total_tasks: int
    completed_tasks: int
    uncompleted_tasks: int
    early_count: int
    on_time_count: int
    slight_delay_count: int
    severe_delay_count: int


class CompletionStatsResponse(BaseModel):
    version_id: str
    iteration_id: Optional[str] = None
    stats: List[PersonCompletionStats]
