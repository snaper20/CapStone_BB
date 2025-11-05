"""
Database models and connection setup for Blood Management System
"""
from sqlalchemy import create_engine, Column, String, Integer, Date, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum

Base = declarative_base()


class GenderEnum(enum.Enum):
    M = "M"
    F = "F"
    O = "O"


class RoleEnum(enum.Enum):
    DONOR = "donor"
    REQUESTER = "requester"
    STAFF = "staff"
    ADMIN = "admin"


class BloodGroup(Base):
    __tablename__ = "blood_groups"
    
    blood_id = Column(String(10), primary_key=True)
    blood_type = Column(String(5), nullable=False, unique=True)  # A+, A-, B+, B-, AB+, AB-, O+, O-
    description = Column(String(200))


class User(Base):
    __tablename__ = "users"
    
    user_id = Column(String(10), primary_key=True)
    blood_id = Column(String(10), ForeignKey("blood_groups.blood_id"), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)
    email = Column(String(255), nullable=False, unique=True)
    mobile_no = Column(String(10), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(Enum(GenderEnum), nullable=True)
    pincode = Column(String(6), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_donation_date = Column(Date, nullable=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.DONOR)
    
    # Relationships
    blood_group = relationship("BloodGroup", backref="users")
    
    # Note: SQLite has limited CHECK constraint support
    # Validation is handled in auth.py instead


class BloodRequest(Base):
    __tablename__ = "blood_requests"
    
    request_id = Column(String(10), primary_key=True)
    requester_id = Column(String(10), ForeignKey("users.user_id"), nullable=False)
    blood_id = Column(String(10), ForeignKey("blood_groups.blood_id"), nullable=False)
    units_required = Column(Integer, nullable=False)
    urgency = Column(String(20), default="normal")  # normal, urgent, critical
    status = Column(String(20), default="pending")  # pending, fulfilled, cancelled
    hospital_name = Column(String(200), nullable=True)
    request_date = Column(DateTime, default=datetime.utcnow)
    fulfilled_date = Column(DateTime, nullable=True)
    notes = Column(String(500), nullable=True)
    
    requester = relationship("User", foreign_keys=[requester_id])
    blood_group = relationship("BloodGroup")


class BloodDonation(Base):
    __tablename__ = "blood_donations"
    
    donation_id = Column(String(10), primary_key=True)
    donor_id = Column(String(10), ForeignKey("users.user_id"), nullable=False)
    blood_id = Column(String(10), ForeignKey("blood_groups.blood_id"), nullable=False)
    donation_date = Column(DateTime, default=datetime.utcnow)
    units_donated = Column(Integer, default=1)
    status = Column(String(20), default="completed")  # completed, pending, rejected
    health_check_passed = Column(String(10), default="yes")  # yes, no
    notes = Column(String(500), nullable=True)
    
    donor = relationship("User", foreign_keys=[donor_id])
    blood_group = relationship("BloodGroup")


class BloodInventory(Base):
    __tablename__ = "blood_inventory"
    
    inventory_id = Column(String(10), primary_key=True)
    blood_id = Column(String(10), ForeignKey("blood_groups.blood_id"), nullable=False)
    units_available = Column(Integer, default=0)
    units_reserved = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    blood_group = relationship("BloodGroup")


# Database setup
def init_db(db_path="blood_management.db"):
    """Initialize database and create tables"""
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    return engine


def get_session(engine):
    """Get database session"""
    Session = sessionmaker(bind=engine)
    return Session()


def get_or_create_engine(db_path="blood_management.db"):
    """Get or create database engine"""
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    return engine

