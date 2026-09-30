from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    tasks = db.relationship(
        "Task",
        backref="project",
        cascade="all, delete-orphan",
        order_by="Task.created_at",
    )

    @property
    def progress(self):
        total = len(self.tasks)
        done = sum(1 for t in self.tasks if t.done)
        pct = round(done / total * 100) if total else 0
        return {"total": total, "done": done, "pct": pct}


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(
        db.Integer, db.ForeignKey("project.id"), nullable=False
    )
    text = db.Column(db.String(300), nullable=False)
    done = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
