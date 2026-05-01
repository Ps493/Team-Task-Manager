"""
routes/dashboard.py - Dashboard stats endpoint

GET /api/dashboard — Task stats + evaluation analytics
"""
from flask import jsonify
from sqlalchemy import func
from middleware.auth import jwt_required_custom, get_current_user
from models import db, Task, TaskEvaluation, Project, ProjectMember
from flask import Blueprint
from datetime import datetime, timezone

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api")


@dashboard_bp.route("/dashboard", methods=["GET"])
@jwt_required_custom
def dashboard():
    user = get_current_user()

    # Scope tasks to user's access
    if user.role == "admin":
        tasks_query = Task.query
        projects_query = Project.query
    else:
        memberships = ProjectMember.query.filter_by(user_id=user.id).all()
        project_ids = [m.project_id for m in memberships]
        tasks_query = Task.query.filter(Task.project_id.in_(project_ids))
        projects_query = Project.query.filter(Project.id.in_(project_ids))

    all_tasks = tasks_query.all()
    total_tasks = len(all_tasks)
    completed_tasks = sum(1 for t in all_tasks if t.status == "done")
    todo_tasks = sum(1 for t in all_tasks if t.status == "todo")
    in_progress_tasks = sum(1 for t in all_tasks if t.status == "in_progress")
    overdue_tasks = sum(1 for t in all_tasks if t.is_overdue)
    total_projects = projects_query.count()

    completion_rate = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0

    # Evaluation analytics
    eval_query = db.session.query(TaskEvaluation)
    if user.role != "admin":
        memberships = ProjectMember.query.filter_by(user_id=user.id).all()
        project_ids = [m.project_id for m in memberships]
        eval_task_ids = [t.id for t in tasks_query.all()]
        eval_query = eval_query.filter(TaskEvaluation.task_id.in_(eval_task_ids))

    evaluations = eval_query.all()
    total_evaluated = len(evaluations)

    avg_accuracy = round(sum(e.accuracy_score for e in evaluations) / total_evaluated, 2) if total_evaluated > 0 else None
    avg_completeness = round(sum(e.completeness_score for e in evaluations) / total_evaluated, 2) if total_evaluated > 0 else None
    avg_composite = round(sum(e.composite_score for e in evaluations) / total_evaluated, 2) if total_evaluated > 0 else None

    # Recent evaluations (last 5)
    recent_evals = eval_query.order_by(TaskEvaluation.evaluated_at.desc()).limit(5).all()

    return jsonify({
        "stats": {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "todo_tasks": todo_tasks,
            "in_progress_tasks": in_progress_tasks,
            "overdue_tasks": overdue_tasks,
            "total_projects": total_projects,
            "completion_rate": completion_rate
        },
        "evaluation": {
            "total_evaluated": total_evaluated,
            "avg_accuracy_score": avg_accuracy,
            "avg_completeness_score": avg_completeness,
            "avg_composite_score": avg_composite
        },
        "recent_evaluations": [e.to_dict() for e in recent_evals]
    }), 200
