from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///academic.db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_session():
    return SessionLocal()

def init_db():
    # Import models
    from modules.users_db import User
    from modules.subjects_db import SubjectsDB
    from modules.attendance_db import AttendanceDB
    #from modules.timetable_db import TimetableDB
    from modules.goals_db import GoalsDB, SubjectGoalDB
    
    Base.metadata.create_all(bind=engine)