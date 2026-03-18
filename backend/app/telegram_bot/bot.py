import asyncio
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from app.config import settings
from app.models.base import SessionLocal
from app.models import User, Person, Group, Version, Iteration, Task
import logging

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self):
        self.application = None
        self.user_sessions = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "欢迎使用 OpenTmAgent Bot!\n\n"
            "可用命令:\n"
            "/login <工号> - 访客登录\n"
            "/admin_login <工号> <密码> - 管理员登录\n"
            "/help - 查看帮助\n"
            "/list_persons - 查看人员列表\n"
            "/list_groups - 查看小组列表\n"
            "/list_versions - 查看版本列表\n"
            "/list_tasks - 查看任务列表"
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "OpenTmAgent Bot 帮助\n\n"
            "团队管理:\n"
            "/list_persons - 查看人员列表\n"
            "/list_groups - 查看小组列表\n"
            "/group_load <组名> - 查看小组负载\n\n"
            "项目管理:\n"
            "/list_versions - 查看版本列表\n"
            "/list_iterations [版本名] - 查看迭代列表\n"
            "/list_tasks [迭代名] - 查看任务列表\n"
            "/task_graph - 查看任务关系图\n\n"
            "架构档案:\n"
            "/list_modules - 查看模块列表\n"
            "/list_features - 查看功能列表\n"
            "/list_fields - 查看责任田列表"
        )

    async def login(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("请提供工号: /login <工号>")
            return

        employee_id = context.args[0]
        user_id = update.effective_user.id

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.employee_id == employee_id).first()
            if not user:
                user = User(employee_id=employee_id, is_admin=False)
                db.add(user)
                db.commit()

            self.user_sessions[user_id] = {
                "employee_id": employee_id,
                "is_admin": user.is_admin
            }

            await update.message.reply_text(f"登录成功! 工号: {employee_id}")
        finally:
            db.close()

    async def admin_login(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if len(context.args) < 2:
            await update.message.reply_text("请提供工号和密码: /admin_login <工号> <密码>")
            return

        employee_id = context.args[0]
        password = context.args[1]
        user_id = update.effective_user.id

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.employee_id == employee_id).first()
            if not user or not user.is_admin:
                await update.message.reply_text("用户不存在或非管理员")
                return

            from app.api.auth import verify_password
            if not user.password_hash:
                from app.api.auth import get_password_hash
                if len(password) < settings.ADMIN_PASSWORD_MIN_LENGTH:
                    await update.message.reply_text(f"密码长度至少{settings.ADMIN_PASSWORD_MIN_LENGTH}位")
                    return
                user.password_hash = get_password_hash(password)
                db.commit()
            elif not verify_password(password, user.password_hash):
                await update.message.reply_text("密码错误")
                return

            self.user_sessions[user_id] = {
                "employee_id": employee_id,
                "is_admin": True
            }

            await update.message.reply_text(f"管理员登录成功! 工号: {employee_id}")
        finally:
            db.close()

    async def list_persons(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        db = SessionLocal()
        try:
            persons = db.query(Person).limit(20).all()
            if not persons:
                await update.message.reply_text("暂无人员数据")
                return

            message = "人员列表:\n\n"
            for p in persons:
                message += f"- {p.name} ({p.employee_id})\n"

            await update.message.reply_text(message)
        finally:
            db.close()

    async def list_groups(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        db = SessionLocal()
        try:
            groups = db.query(Group).all()
            if not groups:
                await update.message.reply_text("暂无小组数据")
                return

            message = "小组列表:\n\n"
            for g in groups:
                message += f"- {g.name}\n"

            await update.message.reply_text(message)
        finally:
            db.close()

    async def list_versions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        db = SessionLocal()
        try:
            versions = db.query(Version).all()
            if not versions:
                await update.message.reply_text("暂无版本数据")
                return

            message = "版本列表:\n\n"
            for v in versions:
                message += f"- {v.name}\n"

            await update.message.reply_text(message)
        finally:
            db.close()

    async def list_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        db = SessionLocal()
        try:
            query = db.query(Task)
            if context.args:
                iteration_name = context.args[0]
                iteration = db.query(Iteration).filter(Iteration.name == iteration_name).first()
                if iteration:
                    query = query.filter(Task.iteration_id == iteration.id)

            tasks = query.limit(20).all()
            if not tasks:
                await update.message.reply_text("暂无任务数据")
                return

            message = "任务列表:\n\n"
            for t in tasks:
                message += f"- {t.name} [{t.status}]\n"

            await update.message.reply_text(message)
        finally:
            db.close()

    def run(self):
        if not settings.TELEGRAM_BOT_TOKEN:
            logger.warning("Telegram Bot Token not configured")
            return

        self.application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("login", self.login))
        self.application.add_handler(CommandHandler("admin_login", self.admin_login))
        self.application.add_handler(CommandHandler("list_persons", self.list_persons))
        self.application.add_handler(CommandHandler("list_groups", self.list_groups))
        self.application.add_handler(CommandHandler("list_versions", self.list_versions))
        self.application.add_handler(CommandHandler("list_tasks", self.list_tasks))

        self.application.run_polling()


bot = TelegramBot()


def run_bot():
    bot.run()
