import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import date

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.models.base import Base, get_db
from app.models import User, Person, Group, AbilityDimension, Version, Iteration, Task
from app.api.auth import get_password_hash

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


class TestAuth:
    def test_visitor_login_new_user(self, db):
        response = client.post("/api/v1/auth/visitor-login", json={"employee_id": "TEST001"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["token"]["access_token"] is not None

    def test_visitor_login_existing_user(self, db):
        user = User(employee_id="TEST001", is_admin=False)
        db.add(user)
        db.commit()
        
        response = client.post("/api/v1/auth/visitor-login", json={"employee_id": "TEST001"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_admin_login_new_user(self, db):
        user = User(employee_id="ADMIN001", is_admin=True)
        db.add(user)
        db.commit()
        
        response = client.post("/api/v1/auth/admin-login", json={
            "employee_id": "ADMIN001",
            "password": "test123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_admin_login_wrong_password(self, db):
        user = User(employee_id="ADMIN001", is_admin=True, password_hash=get_password_hash("correct"))
        db.add(user)
        db.commit()
        
        response = client.post("/api/v1/auth/admin-login", json={
            "employee_id": "ADMIN001",
            "password": "wrong"
        })
        assert response.status_code == 401

    def test_admin_login_non_admin(self, db):
        user = User(employee_id="USER001", is_admin=False)
        db.add(user)
        db.commit()
        
        response = client.post("/api/v1/auth/admin-login", json={
            "employee_id": "USER001",
            "password": "testpass123"
        })
        assert response.status_code == 403


class TestPerson:
    def test_create_person(self, db):
        response = client.post("/api/v1/persons", json={
            "name": "张三",
            "employee_id": "EMP001",
            "email": "zhangsan@example.com",
            "position": "工程师"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "张三"
        assert data["employee_id"] == "EMP001"

    def test_create_person_duplicate_employee_id(self, db):
        person = Person(name="张三", employee_id="EMP001", email="zhangsan@example.com")
        db.add(person)
        db.commit()
        
        response = client.post("/api/v1/persons", json={
            "name": "李四",
            "employee_id": "EMP001",
            "email": "lisi@example.com"
        })
        assert response.status_code == 400

    def test_create_person_duplicate_email(self, db):
        person = Person(name="张三", employee_id="EMP001", email="zhangsan@example.com")
        db.add(person)
        db.commit()
        
        response = client.post("/api/v1/persons", json={
            "name": "李四",
            "employee_id": "EMP002",
            "email": "zhangsan@example.com"
        })
        assert response.status_code == 400

    def test_list_persons(self, db):
        person1 = Person(name="张三", employee_id="EMP001", email="zhangsan@example.com")
        person2 = Person(name="李四", employee_id="EMP002", email="lisi@example.com")
        db.add_all([person1, person2])
        db.commit()
        
        response = client.get("/api/v1/persons")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_person(self, db):
        person = Person(name="张三", employee_id="EMP001", email="zhangsan@example.com")
        db.add(person)
        db.commit()
        
        response = client.get(f"/api/v1/persons/{person.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "张三"

    def test_get_person_not_found(self, db):
        response = client.get("/api/v1/persons/nonexistent-id")
        assert response.status_code == 404

    def test_update_person(self, db):
        person = Person(name="张三", employee_id="EMP001", email="zhangsan@example.com")
        db.add(person)
        db.commit()
        
        response = client.put(f"/api/v1/persons/{person.id}", json={
            "name": "张三丰"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "张三丰"

    def test_delete_person(self, db):
        person = Person(name="张三", employee_id="EMP001", email="zhangsan@example.com")
        db.add(person)
        db.commit()
        
        response = client.delete(f"/api/v1/persons/{person.id}")
        assert response.status_code == 200
        
        response = client.get(f"/api/v1/persons/{person.id}")
        assert response.status_code == 404


class TestGroup:
    def test_create_group(self, db):
        response = client.post("/api/v1/groups", json={
            "name": "研发一组",
            "leader_id": None,
            "member_ids": [],
            "key_persons": []
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "研发一组"

    def test_create_group_duplicate_name(self, db):
        group = Group(name="研发一组")
        db.add(group)
        db.commit()
        
        response = client.post("/api/v1/groups", json={
            "name": "研发一组",
            "leader_id": None,
            "member_ids": [],
            "key_persons": []
        })
        assert response.status_code == 400

    def test_list_groups(self, db):
        group1 = Group(name="研发一组")
        group2 = Group(name="研发二组")
        db.add_all([group1, group2])
        db.commit()
        
        response = client.get("/api/v1/groups")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_group(self, db):
        group = Group(name="研发一组")
        db.add(group)
        db.commit()
        
        response = client.get(f"/api/v1/groups/{group.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "研发一组"


class TestAbilityDimension:
    def test_create_ability_dimension(self, db):
        response = client.post("/api/v1/ability-dimensions", json={
            "name": "技术能力",
            "description": "技术能力评估",
            "level_1_desc": "入门",
            "level_2_desc": "初级",
            "level_3_desc": "中级",
            "level_4_desc": "高级",
            "level_5_desc": "专家"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "技术能力"

    def test_create_ability_dimension_duplicate_name(self, db):
        dim = AbilityDimension(name="技术能力")
        db.add(dim)
        db.commit()
        
        response = client.post("/api/v1/ability-dimensions", json={
            "name": "技术能力"
        })
        assert response.status_code == 400

    def test_list_ability_dimensions(self, db):
        dim1 = AbilityDimension(name="技术能力")
        dim2 = AbilityDimension(name="沟通能力")
        db.add_all([dim1, dim2])
        db.commit()
        
        response = client.get("/api/v1/ability-dimensions")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


class TestVersion:
    def test_create_version(self, db):
        response = client.post("/api/v1/versions", json={
            "name": "V1.0",
            "project_manager": "张三",
            "software_manager": "李四",
            "test_manager": "王五"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "V1.0"

    def test_create_version_duplicate_name(self, db):
        version = Version(name="V1.0")
        db.add(version)
        db.commit()
        
        response = client.post("/api/v1/versions", json={
            "name": "V1.0"
        })
        assert response.status_code == 400

    def test_list_versions(self, db):
        version1 = Version(name="V1.0")
        version2 = Version(name="V2.0")
        db.add_all([version1, version2])
        db.commit()
        
        response = client.get("/api/v1/versions")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_delete_version(self, db):
        version = Version(name="V1.0")
        db.add(version)
        db.commit()
        
        response = client.delete(f"/api/v1/versions/{version.id}")
        assert response.status_code == 200


class TestIteration:
    def test_create_iteration(self, db):
        version = Version(name="V1.0")
        db.add(version)
        db.commit()
        
        response = client.post("/api/v1/iterations", json={
            "version_id": version.id,
            "name": "Sprint1",
            "start_date": "2026-01-01",
            "end_date": "2026-01-31"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Sprint1"

    def test_create_iteration_version_not_found(self, db):
        response = client.post("/api/v1/iterations", json={
            "version_id": "nonexistent",
            "name": "Sprint1",
            "start_date": "2026-01-01",
            "end_date": "2026-01-31"
        })
        assert response.status_code == 404

    def test_list_iterations(self, db):
        version = Version(name="V1.0")
        db.add(version)
        db.commit()
        
        iteration1 = Iteration(name="Sprint1", version_id=version.id, start_date=date(2026, 1, 1), end_date=date(2026, 1, 31))
        iteration2 = Iteration(name="Sprint2", version_id=version.id, start_date=date(2026, 2, 1), end_date=date(2026, 2, 28))
        db.add_all([iteration1, iteration2])
        db.commit()
        
        response = client.get("/api/v1/iterations")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


class TestTask:
    def test_create_task(self, db):
        version = Version(name="V1.0")
        db.add(version)
        db.commit()
        
        iteration = Iteration(name="Sprint1", version_id=version.id, start_date=date(2026, 1, 1), end_date=date(2026, 3, 31))
        db.add(iteration)
        db.commit()
        
        response = client.post("/api/v1/tasks", json={
            "iteration_id": iteration.id,
            "name": "开发登录功能",
            "start_date": "2026-01-01",
            "end_date": "2026-01-15",
            "man_month": 1.0,
            "dev_owners": [],
            "testers": [],
            "dependencies": []
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "开发登录功能"

    def test_create_task_invalid_dates(self, db):
        version = Version(name="V1.0")
        db.add(version)
        db.commit()
        
        iteration = Iteration(name="Sprint1", version_id=version.id, start_date=date(2026, 1, 1), end_date=date(2026, 1, 31))
        db.add(iteration)
        db.commit()
        
        response = client.post("/api/v1/tasks", json={
            "iteration_id": iteration.id,
            "name": "开发登录功能",
            "start_date": "2026-01-15",
            "end_date": "2026-01-01",
            "man_month": 1.0,
            "dev_owners": [],
            "testers": [],
            "dependencies": []
        })
        assert response.status_code == 400

    def test_create_task_exceeds_iteration_end_date(self, db):
        version = Version(name="V1.0")
        db.add(version)
        db.commit()
        
        iteration = Iteration(name="Sprint1", version_id=version.id, start_date=date(2026, 1, 1), end_date=date(2026, 1, 31))
        db.add(iteration)
        db.commit()
        
        response = client.post("/api/v1/tasks", json={
            "iteration_id": iteration.id,
            "name": "开发登录功能",
            "start_date": "2026-01-01",
            "end_date": "2026-02-15",
            "man_month": 1.0,
            "dev_owners": [],
            "testers": [],
            "dependencies": []
        })
        assert response.status_code == 400

    def test_list_tasks(self, db):
        version = Version(name="V1.0")
        db.add(version)
        db.commit()
        
        iteration = Iteration(name="Sprint1", version_id=version.id, start_date=date(2026, 1, 1), end_date=date(2026, 1, 31))
        db.add(iteration)
        db.commit()
        
        task1 = Task(name="任务1", iteration_id=iteration.id, start_date=date(2026, 1, 1), end_date=date(2026, 1, 15), man_month=1.0)
        task2 = Task(name="任务2", iteration_id=iteration.id, start_date=date(2026, 1, 16), end_date=date(2026, 1, 31), man_month=1.0)
        db.add_all([task1, task2])
        db.commit()
        
        response = client.get("/api/v1/tasks")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_update_task_status(self, db):
        version = Version(name="V1.0")
        db.add(version)
        db.commit()
        
        iteration = Iteration(name="Sprint1", version_id=version.id, start_date=date(2026, 1, 1), end_date=date(2026, 1, 31))
        db.add(iteration)
        db.commit()
        
        task = Task(name="任务1", iteration_id=iteration.id, start_date=date(2026, 1, 1), end_date=date(2026, 1, 15), man_month=1.0)
        db.add(task)
        db.commit()
        
        response = client.put(f"/api/v1/tasks/{task.id}", json={
            "status": "in_progress"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"

    def test_delete_task(self, db):
        version = Version(name="V1.0")
        db.add(version)
        db.commit()
        
        iteration = Iteration(name="Sprint1", version_id=version.id, start_date=date(2026, 1, 1), end_date=date(2026, 1, 31))
        db.add(iteration)
        db.commit()
        
        task = Task(name="任务1", iteration_id=iteration.id, start_date=date(2026, 1, 1), end_date=date(2026, 1, 15), man_month=1.0)
        db.add(task)
        db.commit()
        
        response = client.delete(f"/api/v1/tasks/{task.id}")
        assert response.status_code == 200


class TestModule:
    def test_create_module(self, db):
        response = client.post("/api/v1/modules", json={
            "name": "用户模块"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "用户模块"

    def test_create_module_with_parent(self, db):
        from app.models import Module
        
        parent = Module(name="用户模块")
        db.add(parent)
        db.commit()
        
        response = client.post("/api/v1/modules", json={
            "name": "登录子模块",
            "parent_id": parent.id
        })
        assert response.status_code == 200
        data = response.json()
        assert data["parent_id"] == parent.id

    def test_list_modules(self, db):
        from app.models import Module
        
        module1 = Module(name="用户模块")
        module2 = Module(name="订单模块")
        db.add_all([module1, module2])
        db.commit()
        
        response = client.get("/api/v1/modules")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_delete_module(self, db):
        from app.models import Module
        
        module = Module(name="用户模块")
        db.add(module)
        db.commit()
        
        response = client.delete(f"/api/v1/modules/{module.id}")
        assert response.status_code == 200


class TestFeature:
    def test_create_feature(self, db):
        response = client.post("/api/v1/features", json={
            "name": "用户登录",
            "dependent_module_ids": []
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "用户登录"

    def test_list_features(self, db):
        from app.models import Feature
        
        feature1 = Feature(name="用户登录")
        feature2 = Feature(name="用户注册")
        db.add_all([feature1, feature2])
        db.commit()
        
        response = client.get("/api/v1/features")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_delete_feature(self, db):
        from app.models import Feature
        
        feature = Feature(name="用户登录")
        db.add(feature)
        db.commit()
        
        response = client.delete(f"/api/v1/features/{feature.id}")
        assert response.status_code == 200


class TestResponsibilityField:
    def test_create_responsibility_field(self, db):
        response = client.post("/api/v1/responsibility-fields", json={
            "name": "用户系统",
            "feature_ids": []
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "用户系统"

    def test_list_responsibility_fields(self, db):
        from app.models import ResponsibilityField
        
        field1 = ResponsibilityField(name="用户系统")
        field2 = ResponsibilityField(name="订单系统")
        db.add_all([field1, field2])
        db.commit()
        
        response = client.get("/api/v1/responsibility-fields")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_delete_responsibility_field(self, db):
        from app.models import ResponsibilityField
        
        field = ResponsibilityField(name="用户系统")
        db.add(field)
        db.commit()
        
        response = client.delete(f"/api/v1/responsibility-fields/{field.id}")
        assert response.status_code == 200


class TestHealthCheck:
    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"

    def test_health(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
