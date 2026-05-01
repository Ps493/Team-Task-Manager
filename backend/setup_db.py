"""
setup_db.py - Complete database setup + seed script
Run from your backend folder: python setup_db.py
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from app import create_app
from models import db, User, Project, ProjectMember, Task, TaskEvaluation
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone, timedelta


def reset_db(app):
    with app.app_context():
        print("⏳ Dropping all tables...")
        db.drop_all()
        print("⏳ Creating all tables...")
        db.create_all()
        print("✅ Tables created!\n")


def seed_db(app):
    with app.app_context():
        print("🌱 Seeding database...\n")

        # ── Users ──────────────────────────────────────────────
        admin = User(
            name="Admin User",
            email="admin@taskflow.com",
            password_hash=generate_password_hash("admin123"),
            role="admin"
        )
        member1 = User(
            name="Alice Johnson",
            email="alice@taskflow.com",
            password_hash=generate_password_hash("alice123"),
            role="member"
        )
        member2 = User(
            name="Bob Smith",
            email="bob@taskflow.com",
            password_hash=generate_password_hash("bob123"),
            role="member"
        )

        db.session.add_all([admin, member1, member2])
        db.session.flush()
        print(f"✅ Users created:")
        print(f"   Admin  → admin@taskflow.com  / admin123")
        print(f"   Member → alice@taskflow.com  / alice123")
        print(f"   Member → bob@taskflow.com    / bob123\n")

        # ── Projects ───────────────────────────────────────────
        project1 = Project(
            name="Website Redesign",
            description="Complete overhaul of the company website with modern UI/UX.",
            owner_id=admin.id
        )
        project2 = Project(
            name="Mobile App",
            description="Cross-platform mobile application for iOS and Android.",
            owner_id=admin.id
        )

        db.session.add_all([project1, project2])
        db.session.flush()
        print(f"✅ Projects created: '{project1.name}', '{project2.name}'\n")

        # ── Project Members ────────────────────────────────────
        members = [
            ProjectMember(project_id=project1.id, user_id=admin.id),
            ProjectMember(project_id=project1.id, user_id=member1.id),
            ProjectMember(project_id=project1.id, user_id=member2.id),
            ProjectMember(project_id=project2.id, user_id=admin.id),
            ProjectMember(project_id=project2.id, user_id=member1.id),
        ]
        db.session.add_all(members)
        db.session.flush()
        print(f"✅ Project members assigned\n")

        # ── Tasks ──────────────────────────────────────────────
        now = datetime.now(timezone.utc)

        task1 = Task(
            title="Design new homepage mockups",
            description="Create Figma mockups for the new homepage layout.",
            status="done",
            due_date=now - timedelta(days=5),
            project_id=project1.id,
            assigned_to=member1.id,
            created_by=admin.id
        )
        task2 = Task(
            title="Implement responsive navbar",
            description="Build a fully responsive navigation bar using Tailwind CSS.",
            status="in_progress",
            due_date=now + timedelta(days=3),
            project_id=project1.id,
            assigned_to=member2.id,
            created_by=admin.id
        )
        task3 = Task(
            title="SEO audit and fixes",
            description="Run a full SEO audit and fix all critical issues.",
            status="todo",
            due_date=now + timedelta(days=10),
            project_id=project1.id,
            assigned_to=member1.id,
            created_by=admin.id
        )
        task4 = Task(
            title="Set up React Native project",
            description="Initialize the React Native project with navigation and state management.",
            status="done",
            due_date=now - timedelta(days=2),
            project_id=project2.id,
            assigned_to=member1.id,
            created_by=admin.id
        )
        task5 = Task(
            title="Build login and auth screens",
            description="Implement login, register, and forgot password screens.",
            status="in_progress",
            due_date=now + timedelta(days=7),
            project_id=project2.id,
            assigned_to=member1.id,
            created_by=admin.id
        )

        db.session.add_all([task1, task2, task3, task4, task5])
        db.session.flush()
        print(f"✅ Tasks created: {5} tasks across 2 projects\n")

        # ── Task Evaluations (for done tasks) ──────────────────
        eval1 = TaskEvaluation(
            task_id=task1.id,
            evaluator_id=admin.id,
            accuracy_score=9.0,
            completeness_score=8.5,
            comments="Great mockups, very clean and modern. Minor spacing issues on mobile."
        )
        eval2 = TaskEvaluation(
            task_id=task4.id,
            evaluator_id=admin.id,
            accuracy_score=8.0,
            completeness_score=9.0,
            comments="Solid setup, good folder structure and dependencies chosen."
        )

        db.session.add_all([eval1, eval2])
        db.session.commit()
        print(f"✅ Evaluations created for completed tasks\n")

        print("=" * 45)
        print("🎉 Database setup complete!")
        print("=" * 45)
        print("\n📋 Summary:")
        print(f"   Users:       {User.query.count()}")
        print(f"   Projects:    {Project.query.count()}")
        print(f"   Members:     {ProjectMember.query.count()}")
        print(f"   Tasks:       {Task.query.count()}")
        print(f"   Evaluations: {TaskEvaluation.query.count()}")
        print("\n🔑 Login credentials:")
        print("   Admin  → admin@taskflow.com  / admin123")
        print("   Member → alice@taskflow.com  / alice123")
        print("   Member → bob@taskflow.com    / bob123")


if __name__ == "__main__":
    app = create_app()

    if "--reset" in sys.argv:
        confirm = input("⚠️  This will DELETE all data. Type 'yes' to confirm: ")
        if confirm.strip().lower() != "yes":
            print("Aborted.")
            sys.exit(0)
        reset_db(app)

    seed_db(app)