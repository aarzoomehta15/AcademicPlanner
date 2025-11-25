from sqlalchemy import Column, Integer, String
from db.session import Base, get_session

class AttendanceDB(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    date = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    status = Column(String, nullable=False)  # "P" / "A"

    def __init__(self):
        # ensure table exists
        Base.metadata.create_all(bind=get_session().get_bind())

    def set_attendance(self, user_id, date, subject, status):
        """
        status: "P" for present, "A" for absent
        """
        session = get_session()
        row = session.query(AttendanceDB).filter_by(
            user_id=user_id, date=date, subject=subject
        ).first()

        if row:
            row.status = status
        else:
            row = AttendanceDB()
            row.user_id = user_id
            row.date = date
            row.subject = subject
            row.status = status
            session.add(row)

        session.commit()

    def get_subject_attendance(self, user_id):
        """
        Returns: list of (subject, present, total_classes)
        """
        session = get_session()
        rows = session.query(AttendanceDB).filter_by(user_id=user_id).all()

        stats = {}
        for r in rows:
            if r.subject not in stats:
                stats[r.subject] = [0, 0]  # [present, total]
            stats[r.subject][1] += 1
            if r.status == "P":
                stats[r.subject][0] += 1

        # convert to list of tuples
        return [(subj, p, t) for subj, (p, t) in stats.items()]

    def get_attendance(self, user_id):
        """
        Wrapper for compatibility with app.py.
        Same output as get_subject_attendance:
        [(subject, present, total_classes), ...]
        """
        return self.get_subject_attendance(user_id)
    
    def get_attendance_percent(self, user_id):
     """
    Returns {subject: percentage}
    Example → {"DBMS": 82, "Math": 71, "DSA": 93}
      """
     rows = self.get_subject_attendance(user_id)  # [(subj, present, total)]
     result = {}
     for subj, present, total in rows:
        pct = int((present / total) * 100) if total else 0
        result[subj] = pct
     return result
