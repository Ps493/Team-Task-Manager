"""
models/__init__.py - SQLAlchemy models
User, Project, ProjectMember, Task, TaskEvaluation
"""
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="member")  # 'admin' | 'member'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    owned_projects = db.relationship("Project", backref="owner", lazy=True)
    tasks_assigned = db.relationship("Task", backref="assignee", lazy=True, foreign_keys="Task.assigned_to")
    evaluations_given = db.relationship("TaskEvaluation", backref="evaluator", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat()
        }


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    members = db.relationship("ProjectMember", backref="project", lazy=True, cascade="all, delete-orphan")
    tasks = db.relationship("Task", backref="project", lazy=True, cascade="all, delete-orphan")

    def to_dict(self, include_members=False):
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "owner_name": self.owner.name if self.owner else None,
            "task_count": len(self.tasks),
            "member_count": len(self.members),
            "created_at": self.created_at.isoformat()
        }
        if include_members:
            data["members"] = [m.to_dict() for m in self.members]
        return data


class ProjectMember(db.Model):
    __tablename__ = "project_members"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    joined_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user.name if self.user else None,
            "user_email": self.user.email if self.user else None,
            "joined_at": self.joined_at.isoformat()
        }


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="todo")  # todo | in_progress | done
    due_date = db.Column(db.DateTime, nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    creator = db.relationship("User", foreign_keys=[created_by], lazy=True)
    evaluation = db.relationship("TaskEvaluation", backref="task", lazy=True, uselist=False, cascade="all, delete-orphan")

    @property
    def is_overdue(self):
        if self.due_date and self.status != "done":
            return datetime.now(timezone.utc) > self.due_date.replace(tzinfo=timezone.utc)
        return False

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "project_id": self.project_id,
            "project_name": self.project.name if self.project else None,
            "assigned_to": self.assigned_to,
            "assignee_name": self.assignee.name if self.assignee else None,
            "created_by": self.created_by,
            "creator_name": self.creator.name if self.creator else None,
            "is_overdue": self.is_overdue,
            "evaluation": self.evaluation.to_dict() if self.evaluation else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class TaskEvaluation(db.Model):
    __tablename__ = "task_evaluations"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False, unique=True)
    evaluator_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    accuracy_score = db.Column(db.Float, nullable=False)
    completeness_score = db.Column(db.Float, nullable=False)
    comments = db.Column(db.Text, nullable=True)
    evaluated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    @property
    def composite_score(self):
        return round((self.accuracy_score * 0.6 + self.completeness_score * 0.4), 2)

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "evaluator_id": self.evaluator_id,
            "evaluator_name": self.evaluator.name if self.evaluator else None,
            "accuracy_score": self.accuracy_score,
            "completeness_score": self.completeness_score,
            "composite_score": self.composite_score,
            "comments": self.comments,
            "evaluated_at": self.evaluated_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
