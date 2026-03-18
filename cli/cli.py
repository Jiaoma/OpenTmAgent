#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from app.models.base import SessionLocal
from app.models import User, Person, Group, Version, Iteration, Task
from app.api.auth import verify_password, get_password_hash
from app.config import settings
import requests


class OpenTmAgentCLI:
    def __init__(self):
        self.session = PromptSession(
            history=FileHistory('.cli_history'),
            auto_suggest=AutoSuggestFromHistory()
        )
        self.user = None
        self.is_admin = False
        self.db = SessionLocal()
        self.base_url = "http://localhost:8000/api/v1"

        self.commands = {
            "help": self.cmd_help,
            "exit": self.cmd_exit,
            "quit": self.cmd_exit,
            "login": self.cmd_login,
            "admin-login": self.cmd_admin_login,
            "logout": self.cmd_logout,
            "add": self.cmd_add,
            "list": self.cmd_list,
            "view": self.cmd_view,
            "update": self.cmd_update,
            "delete": self.cmd_delete,
            "export": self.cmd_export,
        }

        self.sub_commands = {
            "person": self.handle_person,
            "group": self.handle_group,
            "version": self.handle_version,
            "iteration": self.handle_iteration,
            "task": self.handle_task,
            "module": self.handle_module,
            "feature": self.handle_feature,
            "field": self.handle_field,
        }

    def cmd_help(self, args):
        print("""
OpenTmAgent CLI - 企业级项目管理和团队管理平台

基础命令:
  help              显示帮助信息
  login <工号>      访客登录
  admin-login <工号> <密码>  管理员登录
  logout            登出
  exit/quit         退出程序

数据操作:
  add <类型>        添加数据 (person/group/version/iteration/task/module/feature/field)
  list <类型>       列出数据
  view <类型> <id>  查看详情
  update <类型> <id> 更新数据
  delete <类型> <id> 删除数据
  export <类型>     导出数据

示例:
  add person
  list persons
  view person <工号>
  delete person <工号>
  export modules
        """)

    def cmd_exit(self, args):
        print("再见!")
        self.db.close()
        sys.exit(0)

    def cmd_login(self, args):
        if not args:
            employee_id = input("请输入工号: ")
        else:
            employee_id = args[0]

        user = self.db.query(User).filter(User.employee_id == employee_id).first()
        if not user:
            user = User(employee_id=employee_id, is_admin=False)
            self.db.add(user)
            self.db.commit()

        self.user = user
        self.is_admin = False
        print(f"登录成功! 工号: {employee_id}")

    def cmd_admin_login(self, args):
        if len(args) < 2:
            employee_id = input("请输入工号: ")
            password = input("请输入密码: ")
        else:
            employee_id, password = args[0], args[1]

        user = self.db.query(User).filter(User.employee_id == employee_id).first()
        if not user or not user.is_admin:
            print("用户不存在或非管理员")
            return

        if not user.password_hash:
            if len(password) < settings.ADMIN_PASSWORD_MIN_LENGTH:
                print(f"密码长度至少{settings.ADMIN_PASSWORD_MIN_LENGTH}位")
                return
            user.password_hash = get_password_hash(password)
            self.db.commit()
        elif not verify_password(password, user.password_hash):
            print("密码错误")
            return

        self.user = user
        self.is_admin = True
        print(f"管理员登录成功! 工号: {employee_id}")

    def cmd_logout(self, args):
        self.user = None
        self.is_admin = False
        print("已登出")

    def cmd_add(self, args):
        if not args:
            print("请指定类型: add <类型>")
            return

        obj_type = args[0]
        if obj_type in self.sub_commands:
            self.sub_commands[obj_type]("add", args[1:])
        else:
            print(f"未知类型: {obj_type}")

    def cmd_list(self, args):
        if not args:
            print("请指定类型: list <类型>")
            return

        obj_type = args[0].rstrip('s')
        if obj_type in self.sub_commands:
            self.sub_commands[obj_type]("list", args[1:])
        else:
            print(f"未知类型: {obj_type}")

    def cmd_view(self, args):
        if len(args) < 2:
            print("请指定类型和ID: view <类型> <id>")
            return

        obj_type = args[0]
        if obj_type in self.sub_commands:
            self.sub_commands[obj_type]("view", args[1:])
        else:
            print(f"未知类型: {obj_type}")

    def cmd_update(self, args):
        if len(args) < 2:
            print("请指定类型和ID: update <类型> <id>")
            return

        obj_type = args[0]
        if obj_type in self.sub_commands:
            self.sub_commands[obj_type]("update", args[1:])
        else:
            print(f"未知类型: {obj_type}")

    def cmd_delete(self, args):
        if len(args) < 2:
            print("请指定类型和ID: delete <类型> <id>")
            return

        obj_type = args[0]
        if obj_type in self.sub_commands:
            self.sub_commands[obj_type]("delete", args[1:])
        else:
            print(f"未知类型: {obj_type}")

    def cmd_export(self, args):
        if not args:
            print("请指定类型: export <类型>")
            return

        obj_type = args[0]
        if obj_type in self.sub_commands:
            self.sub_commands[obj_type]("export", args[1:])
        else:
            print(f"未知类型: {obj_type}")

    def handle_person(self, action, args):
        if action == "add":
            name = input("姓名: ")
            employee_id = input("工号: ")
            email = input("邮箱: ")
            position = input("职位 (可选): ") or None

            person = Person(name=name, employee_id=employee_id, email=email, position=position)
            self.db.add(person)
            self.db.commit()
            print(f"创建成功! ID: {person.id}")

        elif action == "list":
            persons = self.db.query(Person).limit(20).all()
            print("\n人员列表:")
            for p in persons:
                print(f"  {p.employee_id}: {p.name} ({p.email})")

        elif action == "view":
            if not args:
                print("请提供工号")
                return
            person = self.db.query(Person).filter(Person.employee_id == args[0]).first()
            if person:
                print(f"\n姓名: {person.name}")
                print(f"工号: {person.employee_id}")
                print(f"邮箱: {person.email}")
                print(f"职位: {person.position or '-'}")
            else:
                print("人员不存在")

        elif action == "delete":
            if not args:
                print("请提供工号")
                return
            person = self.db.query(Person).filter(Person.employee_id == args[0]).first()
            if person:
                self.db.delete(person)
                self.db.commit()
                print("删除成功")
            else:
                print("人员不存在")

    def handle_group(self, action, args):
        if action == "add":
            name = input("组名: ")
            group = Group(name=name)
            self.db.add(group)
            self.db.commit()
            print(f"创建成功! ID: {group.id}")

        elif action == "list":
            groups = self.db.query(Group).all()
            print("\n小组列表:")
            for g in groups:
                print(f"  {g.id}: {g.name}")

    def handle_version(self, action, args):
        if action == "add":
            name = input("版本名称: ")
            pm = input("项目经理 (可选): ") or None
            sm = input("软件经理 (可选): ") or None
            tm = input("测试经理 (可选): ") or None

            version = Version(name=name, project_manager=pm, software_manager=sm, test_manager=tm)
            self.db.add(version)
            self.db.commit()
            print(f"创建成功! ID: {version.id}")

        elif action == "list":
            versions = self.db.query(Version).all()
            print("\n版本列表:")
            for v in versions:
                print(f"  {v.id}: {v.name}")

    def handle_iteration(self, action, args):
        if action == "add":
            name = input("迭代名称: ")
            version_id = input("版本ID: ")
            start_date = input("起始时间 (YYYY-MM-DD): ")
            end_date = input("终止时间 (YYYY-MM-DD): ")

            iteration = Iteration(name=name, version_id=version_id, start_date=start_date, end_date=end_date)
            self.db.add(iteration)
            self.db.commit()
            print(f"创建成功! ID: {iteration.id}")

        elif action == "list":
            iterations = self.db.query(Iteration).all()
            print("\n迭代列表:")
            for i in iterations:
                print(f"  {i.id}: {i.name} ({i.start_date} ~ {i.end_date})")

    def handle_task(self, action, args):
        if action == "add":
            name = input("任务名称: ")
            iteration_id = input("迭代ID: ")
            start_date = input("起始时间 (YYYY-MM-DD): ")
            end_date = input("终止时间 (YYYY-MM-DD): ")
            man_month = float(input("人月: ") or "1.0")

            task = Task(name=name, iteration_id=iteration_id, start_date=start_date, end_date=end_date, man_month=man_month)
            self.db.add(task)
            self.db.commit()
            print(f"创建成功! ID: {task.id}")

        elif action == "list":
            tasks = self.db.query(Task).limit(20).all()
            print("\n任务列表:")
            for t in tasks:
                print(f"  {t.id}: {t.name} [{t.status}]")

    def handle_module(self, action, args):
        if action == "add":
            name = input("模块名称: ")
            parent_id = input("父模块ID (可选): ") or None

            from app.models import Module
            module = Module(name=name, parent_id=parent_id)
            self.db.add(module)
            self.db.commit()
            print(f"创建成功! ID: {module.id}")

        elif action == "list":
            from app.models import Module
            modules = self.db.query(Module).all()
            print("\n模块列表:")
            for m in modules:
                print(f"  {m.id}: {m.name}")

        elif action == "export":
            try:
                res = requests.get(f"{self.base_url}/modules/mermaid")
                if res.ok:
                    print("\nMermaid代码:")
                    print(res.json()["mermaid_code"])
            except Exception as e:
                print(f"导出失败: {e}")

    def handle_feature(self, action, args):
        if action == "add":
            name = input("功能名称: ")
            parent_id = input("父功能ID (可选): ") or None

            from app.models import Feature
            feature = Feature(name=name, parent_id=parent_id)
            self.db.add(feature)
            self.db.commit()
            print(f"创建成功! ID: {feature.id}")

        elif action == "list":
            from app.models import Feature
            features = self.db.query(Feature).all()
            print("\n功能列表:")
            for f in features:
                print(f"  {f.id}: {f.name}")

        elif action == "export":
            try:
                res = requests.get(f"{self.base_url}/features/mermaid")
                if res.ok:
                    print("\nMermaid代码:")
                    print(res.json()["mermaid_code"])
            except Exception as e:
                print(f"导出失败: {e}")

    def handle_field(self, action, args):
        if action == "add":
            name = input("责任田名称: ")
            from app.models import ResponsibilityField
            field = ResponsibilityField(name=name)
            self.db.add(field)
            self.db.commit()
            print(f"创建成功! ID: {field.id}")

        elif action == "list":
            from app.models import ResponsibilityField
            fields = self.db.query(ResponsibilityField).all()
            print("\n责任田列表:")
            for f in fields:
                print(f"  {f.id}: {f.name}")

    def run(self):
        print("OpenTmAgent CLI v1.0.0")
        print("输入 'help' 查看帮助, 'exit' 退出\n")

        completer = WordCompleter(list(self.commands.keys()))

        while True:
            try:
                prompt = f"OpenTmAgent{' (admin)' if self.is_admin else ''}> "
                text = self.session.prompt(prompt, completer=completer)

                if not text.strip():
                    continue

                parts = text.strip().split()
                cmd = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []

                if cmd in self.commands:
                    self.commands[cmd](args)
                else:
                    print(f"未知命令: {cmd}. 输入 'help' 查看帮助")

            except KeyboardInterrupt:
                print("\n使用 'exit' 退出")
            except EOFError:
                self.cmd_exit([])
            except Exception as e:
                print(f"错误: {e}")


def main():
    cli = OpenTmAgentCLI()
    cli.run()


if __name__ == "__main__":
    main()
