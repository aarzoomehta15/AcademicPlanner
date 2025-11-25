from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import Session
from db.session import Base

class TasksDB(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    date = Column(String)
    task_name = Column(String)
    subject = Column(String, nullable=True)
    duration = Column(Integer)
    priority = Column(String)
    status = Column(String, default="pending")

    def __init__(self, session: Session = None):
        self.session = session

    def add_task(self, user_id, date, name, subject, duration, priority):
        task = TasksDB(
            user_id=user_id,
            date=date,
            task_name=name,
            subject=subject,
            duration=duration,
            priority=priority,
            status="pending"
        )
        self.session.add(task)
        self.session.commit()

    def get_tasks_for_date(self, user_id, date):
        tasks = (
            self.session.query(TasksDB)
            .filter_by(user_id=user_id, date=date)
            .order_by(TasksDB.priority.desc())
            .all()
        )
        return [
            {
                "id": t.id,
                "task_name": t.task_name,
                "subject": t.subject,
                "duration": t.duration,
                "priority": t.priority,
                "status": t.status,
            }
            for t in tasks
        ]

    def update_status(self, task_id, new_status):
        task = self.session.query(TasksDB).filter_by(id=task_id).first()
        if task:
            task.status = new_status
            self.session.commit()

    def delete_task(self, task_id):
        task = self.session.query(TasksDB).filter_by(id=task_id).first()
        if task:
            self.session.delete(task)
            self.session.commit()
