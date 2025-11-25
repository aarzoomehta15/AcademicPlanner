from sqlalchemy import Column, Integer, String, Float, Date
from db.session import Base

class ScoresDB(Base):
    __tablename__ = "scores"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    subject = Column(String, nullable=False)
    exam_name = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
