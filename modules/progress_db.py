from sqlalchemy import Column, Integer, String, Date, Float, func
from sqlalchemy.orm import Session
from db.session import Base, get_session


class ProgressDB(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    subject = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    score = Column(Float, nullable=False)


class ProgressHelper:
    def __init__(self):
        self.session: Session = get_session()

    def add_entry(self, user_id, subject, date, score):
        entry = ProgressDB(user_id=user_id, subject=subject, date=date, score=score)
        self.session.add(entry)
        self.session.commit()

    def get_performance_since(self, user_id, since_date):
        return (
            self.session.query(ProgressDB.subject, ProgressDB.score)
            .filter(ProgressDB.user_id == user_id, ProgressDB.date >= since_date)
            .all()
        )

    # ✔️ Added missing function with correct table reference
    def get_overall_performance(self, user_id):
        sess = get_session()
        rows = (
            sess.query(ProgressDB.subject, func.avg(ProgressDB.score))
            .filter(ProgressDB.user_id == user_id)
            .group_by(ProgressDB.subject)
            .all()
        )
        return [(subject, float(avg)) for subject, avg in rows]
