import secrets
from functools import wraps

from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from .models import Project, Task, db

bp = Blueprint("main", __name__)


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        required = current_app.config.get("APP_PASSWORD")
        if required and not session.get("authed"):
            return redirect(url_for("main.login", next=request.path))
        return fn(*args, **kwargs)

    return wrapper


@bp.route("/login", methods=["GET", "POST"])
def login():
    required = current_app.config.get("APP_PASSWORD")
    if not required:
        return redirect(url_for("main.index"))

    error = None
    if request.method == "POST":
        given = request.form.get("password", "")
        if secrets.compare_digest(given, required):
            session["authed"] = True
            return redirect(request.args.get("next") or url_for("main.index"))
        error = "Wrong password."
    return render_template("login.html", error=error)


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("main.login"))


@bp.route("/")
@login_required
def index():
    projects = Project.query.order_by(Project.created_at.asc()).all()
    total = sum(p.progress["total"] for p in projects)
    done = sum(p.progress["done"] for p in projects)
    overall_pct = round(done / total * 100) if total else 0
    return render_template(
        "index.html",
        projects=projects,
        total=total,
        done=done,
        overall_pct=overall_pct,
    )


@bp.route("/projects", methods=["POST"])
@login_required
def create_project():
    name = request.form.get("name", "").strip()
    if name:
        db.session.add(Project(name=name[:120]))
        db.session.commit()
    return redirect(url_for("main.index"))


@bp.route("/projects/<int:project_id>/delete", methods=["POST"])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for("main.index"))


@bp.route("/projects/<int:project_id>/tasks", methods=["POST"])
@login_required
def add_task(project_id):
    project = Project.query.get_or_404(project_id)
    text = request.form.get("text", "").strip()
    if text:
        db.session.add(Task(project_id=project.id, text=text[:300]))
        db.session.commit()
    return redirect(url_for("main.index"))


@bp.route("/tasks/<int:task_id>/toggle", methods=["POST"])
@login_required
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.done = not task.done
    db.session.commit()
    return redirect(url_for("main.index"))


@bp.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("main.index"))
