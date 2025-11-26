from sqlalchemy import Column, Integer, Float, String, Date, text
from sqlalchemy.orm import Session
from db.session import Base, get_session

# Old CGPA table (kept for compatibility)
class GoalsDB(Base):
    __tablename__ = "goals"
    user_id = Column(Integer, primary_key=True)
    target_cgpa = Column(Float, default=0.0)

# New Subject Target Table
class SubjectGoalDB(Base):
    __tablename__ = "subject_goals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    subject = Column(String, nullable=False)
    target_score = Column(Float, nullable=False)

class GoalsHelper:
    def __init__(self):
        session = get_session()
        try:
            Base.metadata.create_all(bind=session.get_bind())
        finally:
            session.close()

    def get_target_cgpa(self, user_id):
        # Deprecated but safe
        session = get_session()
        try:
            row = session.query(GoalsDB).filter_by(user_id=user_id).first()
            return row.target_cgpa if row else 0.0
        finally:
            session.close()

    def set_target_cgpa(self, user_id, value):
        session = get_session()
        try:
            row = session.query(GoalsDB).filter_by(user_id=user_id).first()
            if row:
                row.target_cgpa = value
            else:
                row = GoalsDB(user_id=user_id, target_cgpa=value)
                session.add(row)
            session.commit()
        except:
            session.rollback()
        finally:
            session.close()

    def set_subject_target(self, user_id, subject, target):
        session = get_session()
        try:
            row = session.query(SubjectGoalDB).filter_by(user_id=user_id, subject=subject).first()
            if row:
                row.target_score = target
            else:
                row = SubjectGoalDB(user_id=user_id, subject=subject, target_score=target)
                session.add(row)
            session.commit()
        except:
            session.rollback()
        finally:
            session.close()

    def get_subject_target(self, user_id, subject):
        session = get_session()
        try:
            row = session.query(SubjectGoalDB).filter_by(user_id=user_id, subject=subject).first()
            return row.target_score if row else None
        finally:
            session.close()

    def add_mst_score(self, user_id, subject, exam_name, score, max_score):
        session = get_session()
        try:
            session.execute(
                text("""
                INSERT INTO scores (user_id, subject, exam_name, score, max_score, date)
                VALUES (:uid, :sub, :exam, :score, :max, DATE('now'))
                """),
                {"uid": user_id, "sub": subject, "exam": exam_name, "score": score, "max": max_score}
            )
            session.commit()
        except:
            session.rollback()
        finally:
            session.close()

    def get_scores_for_user(self, user_id):
        session = get_session()
        try:
            rows = session.execute(text("""
                SELECT subject, exam_name, score, max_score
                FROM scores
                WHERE user_id = :uid
                ORDER BY date DESC
            """), {"uid": user_id}).fetchall()
            return [tuple(r) for r in rows]
        finally:
            session.close()

    def get_subject_totals(self, user_id):
        session = get_session()
        try:
            query = """
                SELECT subject, SUM(score) AS total_score, SUM(max_score) AS total_max
                FROM scores
                WHERE user_id = :uid
                GROUP BY subject
            """
            rows = session.execute(text(query), {"uid": user_id}).fetchall()
            result = {}
            for subj, total_score, total_max in rows:
                if total_max and total_score is not None:
                    pct = round((float(total_score) / float(total_max)) * 100, 2)
                else:
                    pct = 0
                result[subj] = pct
            return result
        finally:
            session.close()