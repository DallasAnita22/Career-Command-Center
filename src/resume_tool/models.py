from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String) 
    
    # Current Active Draft (What is currently on the screen)
    saved_name = Column(String, nullable=True)
    saved_email = Column(String, nullable=True)
    saved_phone = Column(String, nullable=True)
    saved_linkedin = Column(String, nullable=True)
    saved_summary = Column(Text, nullable=True)
    saved_experience = Column(Text, nullable=True)
    saved_skills = Column(Text, nullable=True)
    saved_references = Column(Text, nullable=True)
    saved_role = Column(String, default="General")
    
    # Relationships
    projects = relationship("PortfolioProject", back_populates="owner")
    resumes = relationship("SavedResume", back_populates="owner")

class PortfolioProject(Base):
    __tablename__ = "portfolio_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    title = Column(String, index=True)
    industry = Column(String)
    situation = Column(Text)
    task = Column(Text)
    action = Column(Text)
    result = Column(Text)
    evidence_url = Column(String, nullable=True)
    
    owner = relationship("User", back_populates="projects")

class SavedResume(Base):
    __tablename__ = "saved_resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    version_name = Column(String) # e.g. "Software V1"
    created_at = Column(String)
    
    # We store the full resume data as a JSON string for easy saving/loading
    data_dump = Column(Text) 
    
    owner = relationship("User", back_populates="resumes")