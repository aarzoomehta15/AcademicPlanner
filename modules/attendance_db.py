from sqlalchemy import Column, Integer, String, Float
from db.session import Base, get_session

# New Table for simple Percentage Storage
class ManualAttendance(Base):
    __tablename__ = "manual_attendance"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    subject = Column(String, nullable=False)
    percentage = Column(Float, nullable=False, default=0.0)

class AttendanceDB:
    def set_attendance_percentage(self, user_id, subject, percent):
        session = get_session()
        try:
            # Check if entry exists
            row = session.query(ManualAttendance).filter_by(user_id=user_id, subject=subject).first()
            if row:
                row.percentage = percent
            else:
                new_entry = ManualAttendance(user_id=user_id, subject=subject, percentage=percent)
                session.add(new_entry)
            session.commit()
        finally:
            session.close()

    def get_attendance_percent(self, user_id):
        """
        Returns dictionary: {'Math': 85.0, 'Science': 90.0}
        """
        session = get_session()
        try:
            rows = session.query(ManualAttendance).filter_by(user_id=user_id).all()
            return {r.subject: r.percentage for r in rows}
        finally:
            session.close()