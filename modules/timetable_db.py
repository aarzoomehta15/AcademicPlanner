from sqlalchemy import Column, Integer, String
from db.session import Base, get_session


class TimetableDB(Base):
    __tablename__ = "timetable"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    weekday = Column(Integer, nullable=False)  # 0-6
    slot = Column(Integer, nullable=False)     # 0-10
    subject = Column(String, nullable=True)
    class_type = Column(String, nullable=True)

    def __init__(self):
        Base.metadata.create_all(bind=get_session().get_bind())

    def set_slot(self, user_id, weekday, slot, subject, class_type):
        session = get_session()
        try:
            row = session.query(TimetableDB).filter_by(
                user_id=user_id, weekday=weekday, slot=slot
            ).first()

            if row:
                row.subject = subject
                row.class_type = class_type
            else:
                row = TimetableDB()
                row.user_id = user_id
                row.weekday = weekday
                row.slot = slot
                row.subject = subject
                row.class_type = class_type
                session.add(row)

            session.commit()
        finally:
            session.close()

    def get_slots_for_weekday(self, user_id, weekday):
        session = get_session()
        try:
            rows = session.query(TimetableDB).filter_by(
                user_id=user_id, weekday=weekday
            ).all()

            result = {}
            for r in rows:
                result[r.slot] = (r.subject, r.class_type)
            return result
        finally:
            session.close()

    def count_filled_slots_for_date(self, user_id, weekday):
        session = get_session()
        try:
            rows = session.query(TimetableDB).filter_by(
                user_id=user_id, weekday=weekday
            ).all()
            return sum(1 for r in rows if r.subject)
        finally:
            session.close()
