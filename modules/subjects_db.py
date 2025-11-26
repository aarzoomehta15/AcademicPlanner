from sqlalchemy import Column, Integer, String
from db.session import Base, get_session

# 1. The SQLAlchemy Model
class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    subject = Column(String, nullable=False)

# 2. The Helper Class
class SubjectsDB:
    def __init__(self):
        session = get_session()
        try:
            Base.metadata.create_all(bind=session.get_bind())
        finally:
            session.close()

    def add_subject(self, user_id, subject_name):
        session = get_session()
        try:
            subject_name = subject_name.strip()
            # Check if subject already exists for this user
            existing = session.query(Subject).filter_by(user_id=user_id, subject=subject_name).first()
            if not existing:
                # Correctly instantiate the Subject model
                row = Subject(user_id=user_id, subject=subject_name)
                session.add(row)
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error adding subject: {e}")
            raise
        finally:
            session.close()

    def get_subjects(self, user_id):
        session = get_session()
        try:
            rows = session.query(Subject).filter_by(user_id=user_id).all()
            return [r.subject for r in rows]
        finally:
            session.close()