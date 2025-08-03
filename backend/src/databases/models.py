from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

engine = create_engine('sqlite:///database.db', echo=True)
Base = declarative_base()

class Challenge(Base):
    __tablename__ = "challenges"
    
    id = Column(Integer, primary_key=True)
    difficulty = Column(String, nullable=False)
    date_created = Column(DateTime, default=datetime.now)
    created_by = Column(String, nullable=False)
    title = Column(String, nullable=False)
    options = Column(String, nullable=False)
    correct_answer_id = Column(Integer, nullable=False)
    explanation = Column(Integer, nullable=False)
    
class ChallengeQuota(Base):
    __tablename__ = "challenge_quotas"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False, unique=True)
    remaining_quota = Column(Integer, nullable=False, default=50)
    last_reset_date = Column(DateTime, nullable=False, default=datetime.now)
    
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

     
    