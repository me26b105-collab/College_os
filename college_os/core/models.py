from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Boolean, Integer, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .db import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Course(Base):
    __tablename__ = "courses"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)
    color = Column(String, default="#FFFFFF")
    credits = Column(Float, default=3.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    tasks = relationship("Task", back_populates="course")
    attendance_records = relationship("AttendanceRecord", back_populates="course", cascade="all, delete-orphan")
    exams = relationship("Exam", back_populates="course", cascade="all, delete-orphan")
    topics = relationship("SyllabusTopic", back_populates="course", cascade="all, delete-orphan")
    mock_tests = relationship("MockTest", back_populates="course", cascade="all, delete-orphan")
    study_sessions = relationship("StudySession", back_populates="course", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="course", cascade="all, delete-orphan")
    resources = relationship("Resource", back_populates="course", cascade="all, delete-orphan")
    grade_items = relationship("GradeItem", back_populates="course", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    is_completed = Column(Boolean, default=False)
    course_id = Column(String, ForeignKey("courses.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    course = relationship("Course", back_populates="tasks")

class Event(Base):
    __tablename__ = "events"
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    date = Column(String, nullable=False) 
    time = Column(String, nullable=True)
    event_type = Column(String, default="Meeting")

class TimetableSlot(Base):
    __tablename__ = "timetable_slots"
    id = Column(String, primary_key=True, default=generate_uuid)
    day_index = Column(Integer, nullable=False)
    time_index = Column(Integer, nullable=False)
    course_id = Column(String, ForeignKey("courses.id"), nullable=False)
    course = relationship("Course")

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    id = Column(String, primary_key=True, default=generate_uuid)
    course_id = Column(String, ForeignKey("courses.id"), nullable=False)
    date = Column(String, nullable=False)
    status = Column(String, nullable=False)
    course = relationship("Course", back_populates="attendance_records")

class Exam(Base):
    __tablename__ = "exams"
    id = Column(String, primary_key=True, default=generate_uuid)
    course_id = Column(String, ForeignKey("courses.id"), nullable=False)
    title = Column(String, nullable=False)
    date = Column(String, nullable=False)
    time = Column(String, nullable=True)
    location = Column(String, default="Main Hall")
    importance = Column(String, default="High")
    course = relationship("Course", back_populates="exams")

class SyllabusTopic(Base):
    __tablename__ = "syllabus_topics"
    id = Column(String, primary_key=True, default=generate_uuid)
    course_id = Column(String, ForeignKey("courses.id"), nullable=False)
    unit_name = Column(String, nullable=False)
    topic_name = Column(String, nullable=False)
    status = Column(String, default="Not Started")
    difficulty = Column(String, default="Medium")
    last_revised = Column(String, nullable=True)
    course = relationship("Course", back_populates="topics")

class MockTest(Base):
    __tablename__ = "mock_tests"
    id = Column(String, primary_key=True, default=generate_uuid)
    course_id = Column(String, ForeignKey("courses.id"), nullable=False)
    title = Column(String, nullable=False)
    date = Column(String, nullable=False)
    marks_obtained = Column(Float, nullable=False)
    max_marks = Column(Float, nullable=False)
    notes = Column(String, nullable=True)
    course = relationship("Course", back_populates="mock_tests")

class StudySession(Base):
    __tablename__ = "study_sessions"
    id = Column(String, primary_key=True, default=generate_uuid)
    course_id = Column(String, ForeignKey("courses.id"), nullable=False)
    date = Column(String, nullable=False)
    time_index = Column(Integer, nullable=False)
    topic_summary = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    status = Column(String, default="Scheduled")
    course = relationship("Course", back_populates="study_sessions")

class AppUsageRecord(Base):
    __tablename__ = "app_usage_records"
    id = Column(String, primary_key=True, default=generate_uuid)
    app_name = Column(String, nullable=False)
    category = Column(String, default="Other")
    duration_minutes = Column(Float, default=0.0)
    date = Column(String, nullable=False)

class Note(Base):
    __tablename__ = "notes"
    id = Column(String, primary_key=True, default=generate_uuid)
    course_id = Column(String, ForeignKey("courses.id"), nullable=True)
    title = Column(String, nullable=False)
    content = Column(Text, default="")
    tags = Column(String, default="")
    is_favorite = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    course = relationship("Course", back_populates="notes")

class Resource(Base):
    __tablename__ = "resources"
    id = Column(String, primary_key=True, default=generate_uuid)
    course_id = Column(String, ForeignKey("courses.id"), nullable=True)
    title = Column(String, nullable=False)
    resource_type = Column(String, default="PDF")
    file_path_or_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    course = relationship("Course", back_populates="resources")

class Project(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    category = Column(String, default="Personal")
    description = Column(String, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    tasks = relationship("ProjectTask", back_populates="project", cascade="all, delete-orphan")

class ProjectTask(Base):
    __tablename__ = "project_tasks"
    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    title = Column(String, nullable=False)
    status = Column(String, default="To Do")
    priority = Column(String, default="Medium")
    due_date = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    project = relationship("Project", back_populates="tasks")

class GradeItem(Base):
    __tablename__ = "grade_items"
    id = Column(String, primary_key=True, default=generate_uuid)
    course_id = Column(String, ForeignKey("courses.id"), nullable=False)
    title = Column(String, nullable=False)
    category = Column(String, default="Assignment") # Exam, Assignment, Quiz, Project, Lab
    weight_percent = Column(Float, default=10.0)
    score_achieved = Column(Float, default=0.0)
    max_score = Column(Float, default=100.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    course = relationship("Course", back_populates="grade_items")