# modules/todo_db.py

from sqlalchemy import Column, Integer, String, Float
from db.session import Base, get_session
from sqlalchemy.orm import Session
from db.session import get_session
from sqlalchemy import text


class ToDo(Base):
    __tablename__ = "todo"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    date = Column(String, nullable=False)          # "YYYY-MM-DD"
    task_name = Column(String, nullable=False)
    subject = Column(String, nullable=True)
    duration = Column(Float, nullable=True)        # hours (optional)
    priority = Column(String, nullable=True)       # "Low"/"Medium"/"High"
    status = Column(String, nullable=False, default="pending")


class ToDoDB:
    def __init__(self):
        self.session: Session = get_session() 
        # Nothing needed here, we open a session per call
        pass

    def add_task(
        self,
        user_id: int,
        date: str,
        task_name: str,
        subject: str | None = None,
        duration: float | None = None,
        priority: str | None = None,
        status: str = "pending",
    ):
        """
        Works with BOTH:
        - add_task(user_id, date, task_name)
        - add_task(user_id, date, task_name, subject, duration, priority)
        - add_task(user_id, date, task_name, subject, duration, priority, status)
        """
        db = get_session()
        try:
            todo = ToDo(
                user_id=user_id,
                date=date,
                task_name=task_name,
                subject=subject,
                duration=duration,
                priority=priority,
                status=status or "pending",
            )
            db.add(todo)
            db.commit()
            db.refresh(todo)
            return todo.id
        finally:
            db.close()

    def get_tasks_for_date(self, user_id: int, date: str):
        """
        Returns a list of dicts:
        [{"id": ..., "task_name": ..., "subject": ..., "duration": ..., "priority": ..., "status": ...}, ...]
        """
        db = get_session()
        try:
            rows = (
                db.query(ToDo)
                .filter(ToDo.user_id == user_id, ToDo.date == date)
                .order_by(ToDo.priority.desc().nullslast(), ToDo.id)
                .all()
            )
            result = []
            for r in rows:
                result.append(
                    {
                        "id": r.id,
                        "task_name": r.task_name,
                        "subject": r.subject,
                        "duration": r.duration,
                        "priority": r.priority,
                        "status": r.status,
                    }
                )
            return result
        finally:
            db.close()

    def update_status(self, task_id: int, status: str):
        db = get_session()
        try:
            row = db.query(ToDo).filter(ToDo.id == task_id).first()
            if not row:
                return False
            row.status = status
            db.commit()
            return True
        finally:
            db.close()

    def delete_task(self, task_id: int):
        db = get_session()
        try:
            row = db.query(ToDo).filter(ToDo.id == task_id).first()
            if not row:
                return False
            db.delete(row)
            db.commit()
            return True
        finally:
            db.close()

    def get_statistics(self, user_id):
        """
        Returns:
        {
            "DBMS": {"done": 3, "total": 5},
            "Math": {"done": 1, "total": 3},
            "DSA": {"done": 5, "total": 6}
        }
        """
        db = get_session()
        try:
            rows = (
                db.query(ToDo)
                .filter(ToDo.user_id == user_id)
                .all()
            )

            stats = {}
            for r in rows:
                subj = r.subject or "General"
                if subj not in stats:
                    stats[subj] = {"done": 0, "total": 0}
                stats[subj]["total"] += 1
                if r.status == "done":
                    stats[subj]["done"] += 1

            return stats
        finally:
            db.close()


    def get_completion_percent(self, user_id):
        """
        Converts stats into:
        { "DBMS": 60, "Math": 33, "General": 80 }
        """
        stats = self.get_statistics(user_id)
        result = {}
        for subj, entry in stats.items():
            done = entry["done"]
            total = entry["total"]
            result[subj] = int((done / total) * 100) if total else 0
        return result
