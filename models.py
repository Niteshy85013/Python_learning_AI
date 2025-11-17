from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from config import Config

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    submissions = relationship('Submission', back_populates='user')

class Exercise(Base):
    __tablename__ = 'exercises'
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    starter_code = Column(Text, default='')
    expected_output = Column(Text, default='')  # used for simple output comparison
    difficulty = Column(String(30), default='Beginner')
    created_at = Column(DateTime, default=datetime.utcnow)

    submissions = relationship('Submission', back_populates='exercise')

class Submission(Base):
    __tablename__ = 'submissions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    exercise_id = Column(Integer, ForeignKey('exercises.id'))
    code = Column(Text, nullable=False)
    result = Column(Text, nullable=True)
    passed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='submissions')
    exercise = relationship('Exercise', back_populates='submissions')

# Database session helpers
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, future=True)
Session = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))

def init_db():
    Base.metadata.create_all(engine)
