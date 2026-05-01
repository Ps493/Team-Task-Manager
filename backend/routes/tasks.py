"""
routes/tasks.py - Task management + Evaluation endpoints

Task CRUD:
  GET    /api/tasks                  — list tasks (filtered by project, status, assignee)
  POST   /api/tasks                  — create task (admin only)
  GET    /api/tasks/:id              — task detail
  PUT    /api/tasks/:id              — update task fields (admin)
  PATCH  /api/tasks/:id/status       — update status (member/admin)
  DELETE /api/tasks/:id              — delete task (admin)

Evaluation (RLHF-inspired scoring):
  POST   /api/tasks/:id/evaluate     — create/update evaluation (admin only)
  GET    /api/tasks/:id/evaluate     — get evaluation for task
"""
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from middleware.auth import jwt_required_custom, admin_required, get_current_user
from models import db, Task, TaskEvaluation, Project, ProjectMember, User

tasks_bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")

VALID_STATUSES = ("todo", "in_progress", "done")


def validate_score(value, field_name):
    """Validate that a score is a float between 0 and 5"""
    try:
        v = float(value)
        if not (0 <= v <= 5):
            return f"{field_name} must be between 0 and 5"
    except (TypeError, ValueError):
        return f"{field_name} must be a number"
    return None


@tasks_bp.route("", methods=["GET"])
@jwt_required_custom
def list_tasks():
    user = get_current_user()
    query = Task.query

    # Filter params
    project_id = request.args.get("project_id", type=int)
    status = request.args.get("status")
    assigned_to = request.args.get("assigned_to", type=int)

    if project_id:
        # Access check for members
        if user.role != "admin":
            is_member = ProjectMember.query.filter_by(project_id=project_id, user_id=user.id).first()
            if not is_member:
                return jsonify({"error": "Access denied"}), 403
        query = query.filter_by(project_id=project_id)
    elif user.role != "admin":
        # Members only see tasks in their projects
        memberships = ProjectMember.query.filter_by(user_id=user.id).all()
        project_ids = [m.project_id for m in memberships]
        query = query.filter(Task.project_id.in_(project_ids))

    if status and status in VALID_STATUSES:
        query = query.filter_by(status=status)
    if assigned_to:
        query = query.filter_by(assigned_to=assigned_to)

    tasks = query.order_by(Task.created_at.desc()).all()
    return jsonify({"tasks": [t.to_dict() for t in tasks]}), 200


@tasks_bp.route("", methods=["POST"])
@admin_required
def create_task():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    errors = []
    if not data.get("title") or len(data["title"].strip()) < 3:
        errors.append("Title must be at least 3 characters")
    if not data.get("project_id"):
        errors.append("project_id is required")
    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 422

    # Verify project exists
    project = Project.query.get(data["project_id"])
    if not project:
        return jsonify({"error": "Project not found"}), 404

    # Parse due_date
    due_date = None
    if data.get("due_date"):
        try:
            due_date = datetime.fromisoformat(data["due_date"].replace("Z", "+00:00"))
        except ValueError:
            return jsonify({"error": "Invalid due_date format. Use ISO 8601"}), 422

    user = get_current_user()
    task = Task(
        title=data["title"].strip(),
        description=data.get("description", "").strip(),
        status=data.get("status", "todo"),
        due_date=due_date,
        project_id=data["project_id"],
        assigned_to=data.get("assigned_to"),
        created_by=user.id
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({"message": "Task created", "task": task.to_dict()}), 201


@tasks_bp.route("/<int:task_id>", methods=["GET"])
@jwt_required_custom
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    user = get_current_user()

    if user.role != "admin":
        is_member = ProjectMember.query.filter_by(project_id=task.project_id, user_id=user.id).first()
        if not is_member:
            return jsonify({"error": "Access denied"}), 403

    return jsonify({"task": task.to_dict()}), 200


@tasks_bp.route("/<int:task_id>", methods=["PUT"])
@admin_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if "title" in data and data["title"].strip():
        task.title = data["title"].strip()
    if "description" in data:
        task.description = data["description"].strip()
    if "status" in data:
        if data["status"] not in VALID_STATUSES:
            return jsonify({"error": f"Status must be one of: {VALID_STATUSES}"}), 422
        task.status = data["status"]
    if "assigned_to" in data:
        task.assigned_to = data["assigned_to"]
    if "due_date" in data:
        try:
            task.due_date = datetime.fromisoformat(data["due_date"].replace("Z", "+00:00")) if data["due_date"] else None
        except ValueError:
            return jsonify({"error": "Invalid due_date format"}), 422

    task.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({"message": "Task updated", "task": task.to_dict()}), 200


@tasks_bp.route("/<int:task_id>/status", methods=["PATCH"])
@jwt_required_custom
def update_status(task_id):
    """Members can update their own assigned task status; admins can update any"""
    task = Task.query.get_or_404(task_id)
    user = get_current_user()
    data = request.get_json()

    if not data or "status" not in data:
        return jsonify({"error": "status is required"}), 422
    if data["status"] not in VALID_STATUSES:
        return jsonify({"error": f"Status must be one of: {list(VALID_STATUSES)}"}), 422

    # Members can only update tasks assigned to them
    if user.role != "admin" and task.assigned_to != user.id:
        return jsonify({"error": "You can only update tasks assigned to you"}), 403

    task.status = data["status"]
    task.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({"message": "Status updated", "task": task.to_dict()}), 200


@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
@admin_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"}), 200


# ─── EVALUATION ENDPOINTS ────────────────────────────────────────────────────

@tasks_bp.route("/<int:task_id>/evaluate", methods=["POST"])
@admin_required
def evaluate_task(task_id):
    """
    Create or update an evaluation for a completed task.
    Inspired by LLM RLHF workflows: each 'response' (task output) is scored
    on accuracy and completeness, with qualitative comments — mirroring
    how human raters evaluate model outputs during post-training.
    """
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Task must be completed to be evaluated
    if task.status != "done":
        return jsonify({"error": "Only completed tasks can be evaluated"}), 400

    # Validate scores
    errors = []
    for field in ("accuracy_score", "completeness_score"):
        if field not in data:
            errors.append(f"{field} is required")
        else:
            err = validate_score(data[field], field)
            if err:
                errors.append(err)
    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 422

    user = get_current_user()
    evaluation = task.evaluation

    if evaluation:
        # Update existing evaluation (re-evaluation allowed)
        evaluation.accuracy_score = float(data["accuracy_score"])
        evaluation.completeness_score = float(data["completeness_score"])
        evaluation.comments = data.get("comments", "")
        evaluation.evaluator_id = user.id
        evaluation.updated_at = datetime.now(timezone.utc)
        message = "Evaluation updated"
    else:
        evaluation = TaskEvaluation(
            task_id=task_id,
            evaluator_id=user.id,
            accuracy_score=float(data["accuracy_score"]),
            completeness_score=float(data["completeness_score"]),
            comments=data.get("comments", "")
        )
        db.session.add(evaluation)
        message = "Evaluation submitted"

    db.session.commit()
    return jsonify({"message": message, "evaluation": evaluation.to_dict()}), 200


@tasks_bp.route("/<int:task_id>/evaluate", methods=["GET"])
@jwt_required_custom
def get_evaluation(task_id):
    task = Task.query.get_or_404(task_id)
    if not task.evaluation:
        return jsonify({"evaluation": None}), 200
    return jsonify({"evaluation": task.evaluation.to_dict()}), 200
