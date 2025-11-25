from sqlalchemy import Column, Integer, Float
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.session import Base, get_session
from sqlalchemy import text



class GoalsDB(Base):
    __tablename__ = "goals"
    user_id = Column(Integer, primary_key=True)
    target_cgpa = Column(Float, default=0.0)


class GoalsHelper:
    def __init__(self):
        self.session: Session = get_session()

    def get_target_cgpa(self, user_id):
        row = self.session.query(GoalsDB).filter_by(user_id=user_id).first()
        return row.target_cgpa if row else 0.0

    def set_target_cgpa(self, user_id, value):
        row = self.session.query(GoalsDB).filter_by(user_id=user_id).first()
        if row:
            row.target_cgpa = value
        else:
            row = GoalsDB(user_id=user_id, target_cgpa=value)
            self.session.add(row)
        self.session.commit()

    # For MST scores (for Scores page)
    def add_mst_score(self, user_id, subject, exam_name, score, max_score):
        self.session.execute(
            text("""
            INSERT INTO scores (user_id, subject, exam_name, score, max_score, date)
            VALUES (:uid, :sub, :exam, :score, :max, DATE('now'))
            """),
            {"uid": user_id, "sub": subject, "exam": exam_name, "score": score, "max": max_score}
        )
        self.session.commit()

    def get_scores_for_user(self, user_id):
        rows = self.session.execute(text("""
    SELECT subject, exam_name, score, max_score
    FROM scores
    WHERE user_id = :uid
    ORDER BY date DESC
"""), {"uid": user_id}).fetchall()

        return [tuple(r) for r in rows]
    def get_subject_totals(self, user_id):
   
      query = """
        SELECT subject, SUM(score) AS total_score, SUM(max_score) AS total_max
        FROM scores
        WHERE user_id = :uid
        GROUP BY subject
    """
      rows = self.session.execute(text(query), {"uid": user_id}).fetchall()

      result = {}
      for subj, total_score, total_max in rows:
        if total_max and total_score is not None:
            pct = round((float(total_score) / float(total_max)) * 100, 2)
        else:
            pct = 0
        result[subj] = pct

      return result



class GoalsScoreHelper:
    """Returns subject-wise average percentage for Dashboard."""
    def __init__(self):
        self.session: Session = get_session()

    def get_subject_averages(self, user_id):
        rows = self.session.execute(
            """
            SELECT subject, AVG(score * 1.0 / max_score)
            FROM scores
            WHERE user_id = :uid
            GROUP BY subject
            """, {"uid": user_id}
        ).fetchall()

        return {sub: float(avg) for sub, avg in rows}
    
