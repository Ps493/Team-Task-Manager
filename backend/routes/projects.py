"""
routes/projects.py - Project management endpoints

GET    /api/projects              — List projects
POST   /api/projects              — Create project (admin)
GET    /api/projects/:id          — Project detail + members
PUT    /api/projects/:id          — Update project (admin)
DELETE /api/projects/:id          — Delete project (admin)
POST   /api/projects/:id/members  — Add member (admin)
DELETE /api/projects/:id/members/:uid — Remove member (admin)
GET    /api/projects/users        — List all users (admin, for member picker)
"""
from flask import Blueprint, request, jsonify
from middleware.auth import jwt_required_custom, admin_required, get_current_user
from models import db, Project, ProjectMember, User

projects_bp = Blueprint("projects", __name__, url_prefix="/api/projects")


@projects_bp.route("/users", methods=["GET"])
@admin_required
def list_users():
    """Return all users — used by admin to populate member picker."""
    users = User.query.order_by(User.name).all()
    return jsonify({"users": [u.to_dict() for u in users]}), 200


@projects_bp.route("", methods=["GET"])
@jwt_required_custom
def list_projects():
    user = get_current_user()
    if user.role == "admin":
        projects = Project.query.order_by(Project.created_at.desc()).all()
    else:
        memberships = ProjectMember.query.filter_by(user_id=user.id).all()
        project_ids = [m.project_id for m in memberships]
        projects = Project.query.filter(Project.id.in_(project_ids)).order_by(Project.created_at.desc()).all()

    return jsonify({"projects": [p.to_dict() for p in projects]}), 200


@projects_bp.route("", methods=["POST"])
@admin_required
def create_project():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get("name", "").strip()
    if not name or len(name) < 2:
        return jsonify({"error": "Project name must be at least 2 characters"}), 422

    user = get_current_user()
    project = Project(
        name=name,
        description=data.get("description", "").strip(),
        owner_id=user.id
    )
    db.session.add(project)
    db.session.flush()  # get project.id before commit

    # Auto-add owner as member
    member = ProjectMember(project_id=project.id, user_id=user.id)
    db.session.add(member)
    db.session.commit()

    return jsonify({"message": "Project created", "project": project.to_dict(include_members=True)}), 201


@projects_bp.route("/<int:project_id>", methods=["GET"])
@jwt_required_custom
def get_project(project_id):
    project = Project.query.get_or_404(project_id)
    user = get_current_user()

    if user.role != "admin":
        is_member = ProjectMember.query.filter_by(project_id=project_id, user_id=user.id).first()
        if not is_member:
            return jsonify({"error": "Access denied"}), 403

    return jsonify({"project": project.to_dict(include_members=True)}), 200


@projects_bp.route("/<int:project_id>", methods=["PUT"])
@admin_required
def update_project(project_id):
    project = Project.query.get_or_404(project_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if "name" in data and data["name"].strip():
        project.name = data["name"].strip()
    if "description" in data:
        project.description = data["description"].strip()

    db.session.commit()
    return jsonify({"message": "Project updated", "project": project.to_dict()}), 200


@projects_bp.route("/<int:project_id>", methods=["DELETE"])
@admin_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return jsonify({"message": "Project deleted"}), 200


@projects_bp.route("/<int:project_id>/members", methods=["POST"])
@admin_required
def add_member(project_id):
    project = Project.query.get_or_404(project_id)
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id is required"}), 422

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    existing = ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first()
    if existing:
        return jsonify({"error": "User is already a member"}), 409

    member = ProjectMember(project_id=project_id, user_id=user_id)
    db.session.add(member)
    db.session.commit()
    return jsonify({"message": "Member added", "project": project.to_dict(include_members=True)}), 201


@projects_bp.route("/<int:project_id>/members/<int:user_id>", methods=["DELETE"])
@admin_required
def remove_member(project_id, user_id):
    member = ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first()
    if not member:
        return jsonify({"error": "Member not found"}), 404

    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "Member removed"}), 200
