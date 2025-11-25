from sqlalchemy import Column, Integer, String
from db.session import Base, get_session

class SubjectsDB(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    subject = Column(String, nullable=False)

    def __init__(self):
        Base.metadata.create_all(bind=get_session().get_bind())

    def add_subject(self, user_id, subject_name):
        session = get_session()
        subject_name = subject_name.strip()
        existing = session.query(SubjectsDB).filter_by(user_id=user_id, subject=subject_name).first()
        if not existing:
            row = SubjectsDB()
            row.user_id = user_id
            row.subject = subject_name
            session.add(row)
            session.commit()

    def get_subjects(self, user_id):
        session = get_session()
        rows = session.query(SubjectsDB).filter_by(user_id=user_id).all()
        return [r.subject for r in rows]
