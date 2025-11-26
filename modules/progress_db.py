from sqlalchemy import Column, Integer, String, Date, Float
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
        pass

    def add_entry(self, user_id, subject, date, score):
        session = get_session()
        try:
            entry = ProgressDB(user_id=user_id, subject=subject, date=date, score=score)
            session.add(entry)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def get_performance_since(self, user_id, since_date):
        session = get_session()
        try:
            return (
                session.query(ProgressDB.subject, ProgressDB.score)
                .filter(ProgressDB.user_id == user_id, ProgressDB.date >= since_date)
                .all()
            )
        finally:
            session.close()

    def log_feedback(self, user_id, date, subject, hours, score):
        # Log feedback as a score entry (100 = completed, 50 = half, 0 = not done)
        numeric_score = score * 100
        self.add_entry(user_id, subject, date, numeric_score)