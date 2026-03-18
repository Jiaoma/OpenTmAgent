from sqlalchemy import Column, String, ForeignKey, Date, Float, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base, generate_uuid, TimestampMixin
import enum


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskRelationType(str, enum.Enum):
    DEPENDS_ON = "depends_on"
    RELATED_TO = "related_to"


class Version(Base, TimestampMixin):
    __tablename__ = "versions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False, unique=True)
    project_manager = Column(String(100), nullable=True)
    software_manager = Column(String(100), nullable=True)
    test_manager = Column(String(100), nullable=True)
    
    iterations = relationship("Iteration", back_populates="version")
    
    def __repr__(self):
        return f"<Version {self.name}>"


class Iteration(Base, TimestampMixin):
    __tablename__ = "iterations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    version_id = Column(String(36), ForeignKey("versions.id"), nullable=False)
    name = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_man_month = Column(Float, default=0.0)
    
    version = relationship("Version", back_populates="iterations")
    tasks = relationship("Task", back_populates="iteration")
    
    def __repr__(self):
        return f"<Iteration {self.name}>"


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    iteration_id = Column(String(36), ForeignKey("iterations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    man_month = Column(Float, nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    actual_end_date = Column(Date, nullable=True)
    design_doc_url = Column(String(500), nullable=True)
    
    iteration = relationship("Iteration", back_populates="tasks")
    feature_owner = relationship("TaskPerson", foreign_keys="TaskPerson.task_id", 
                                  primaryjoin="and_(Task.id==TaskPerson.task_id, TaskPerson.role=='feature_owner')")
    dev_owners = relationship("TaskPerson", 
                               primaryjoin="and_(Task.id==TaskPerson.task_id, TaskPerson.role=='dev_owner')")
    testers = relationship("TaskTester", back_populates="task")
    dependencies = relationship("TaskRelation", 
                                foreign_keys="TaskRelation.task_id",
                                back_populates="task")
    related_tasks = relationship("TaskRelation",
                                  foreign_keys="TaskRelation.task_id",
                                  primaryjoin="and_(Task.id==TaskRelation.task_id, TaskRelation.relation_type=='related_to')")
    
    def __repr__(self):
        return f"<Task {self.name}>"


class TaskPerson(Base, TimestampMixin):
    __tablename__ = "task_persons"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False)
    person_id = Column(String(36), ForeignKey("persons.id"), nullable=True)
    person_name = Column(String(100), nullable=True)
    role = Column(String(50), nullable=False)
    
    task = relationship("Task")
    person = relationship("Person", back_populates="tasks")
    
    def __repr__(self):
        return f"<TaskPerson {self.task_id}:{self.role}>"


class TaskTester(Base, TimestampMixin):
    __tablename__ = "task_testers"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False)
    name = Column(String(100), nullable=False)
    
    task = relationship("Task", back_populates="testers")
    
    def __repr__(self):
        return f"<TaskTester {self.task_id}:{self.name}>"


class TaskRelation(Base, TimestampMixin):
    __tablename__ = "task_relations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False)
    related_task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False)
    relation_type = Column(Enum(TaskRelationType), nullable=False)
    
    task = relationship("Task", foreign_keys=[task_id], back_populates="dependencies")
    related_task = relationship("Task", foreign_keys=[related_task_id])
    
    def __repr__(self):
        return f"<TaskRelation {self.task_id}->{self.related_task_id}>"


class TaskCompletionRecord(Base, TimestampMixin):
    __tablename__ = "task_completion_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    person_id = Column(String(36), ForeignKey("persons.id"), nullable=False)
    version_id = Column(String(36), ForeignKey("versions.id"), nullable=False)
    iteration_id = Column(String(36), ForeignKey("iterations.id"), nullable=False)
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False)
    status = Column(String(50), nullable=False)
    completed_at = Column(Date, nullable=True)
    
    def __repr__(self):
        return f"<TaskCompletionRecord {self.task_id}:{self.status}>"
