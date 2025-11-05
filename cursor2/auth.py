"""
Authentication and authorization utilities
"""
import bcrypt
from sqlalchemy.orm import Session
from database import User, RoleEnum, GenderEnum, BloodGroup, init_db, get_session, get_or_create_engine
from datetime import datetime, date
import re


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_mobile(mobile: str) -> bool:
    """Validate mobile number (10 digits)"""
    return mobile.isdigit() and len(mobile) == 10


def validate_pincode(pincode: str) -> bool:
    """Validate pincode (6 digits, 100000-999999)"""
    if not pincode.isdigit():
        return False
    return 100000 <= int(pincode) <= 999999


def generate_user_id(session: Session, prefix: str = "U") -> str:
    """Generate unique user ID"""
    last_user = session.query(User).order_by(User.user_id.desc()).first()
    if last_user:
        last_num = int(last_user.user_id[1:])
        new_num = last_num + 1
    else:
        new_num = 1
    return f"{prefix}{new_num:04d}"


def generate_id(session: Session, model_class, id_field, prefix: str) -> str:
    """Generate unique ID for any model"""
    last_record = session.query(model_class).order_by(getattr(model_class, id_field).desc()).first()
    if last_record:
        last_id = getattr(last_record, id_field)
        last_num = int(last_id.replace(prefix, ""))  # remove the prefix string completely

        new_num = last_num + 1
    else:
        new_num = 1
    return f"{prefix}{new_num:04d}"


def register_user(
    session: Session,
    first_name: str,
    email: str,
    mobile_no: str,
    password: str,
    pincode: str,
    last_name: str = None,
    date_of_birth: date = None,
    gender: str = None,
    blood_type: str = None,
    role: str = "donor"
) -> tuple[User, str]:
    """
    Register a new user
    Returns (user, error_message)
    """
    # Validation
    if not validate_email(email):
        return None, "Invalid email format"
    
    if not validate_mobile(mobile_no):
        return None, "Mobile number must be 10 digits"
    
    if not validate_pincode(pincode):
        return None, "Pincode must be 6 digits (100000-999999)"
    
    if len(password) < 6:
        return None, "Password must be at least 6 characters"
    
    # Check if email exists
    if session.query(User).filter(User.email == email).first():
        return None, "Email already registered"
    
    # Check if mobile exists
    if session.query(User).filter(User.mobile_no == mobile_no).first():
        return None, "Mobile number already registered"
    
    # Get blood group
    blood_id = None
    if blood_type:
        blood_group = session.query(BloodGroup).filter(BloodGroup.blood_type == blood_type).first()
        if blood_group:
            blood_id = blood_group.blood_id
        else:
            # Create blood group if it doesn't exist
            blood_id = generate_id(session, BloodGroup, "blood_id", "BG")
            blood_group = BloodGroup(blood_id=blood_id, blood_type=blood_type)
            session.add(blood_group)
    
    # Convert gender string to enum
    gender_enum = None
    if gender:
        gender_enum = GenderEnum[gender.upper()] if gender.upper() in ["M", "F", "O"] else None
    
    # Convert role string to enum
    role_enum = RoleEnum[role.upper()] if role.upper() in ["DONOR", "REQUESTER", "STAFF", "ADMIN"] else RoleEnum.DONOR
    
    # Create user
    user_id = generate_user_id(session)
    user = User(
        user_id=user_id,
        blood_id=blood_id,
        first_name=first_name,
        last_name=last_name,
        email=email,
        mobile_no=mobile_no,
        password_hash=hash_password(password),
        date_of_birth=date_of_birth,
        gender=gender_enum,
        pincode=pincode,
        role=role_enum
    )
    
    session.add(user)
    session.commit()
    return user, None


def authenticate_user(session: Session, email: str, password: str) -> tuple[User, str]:
    """
    Authenticate a user
    Returns (user, error_message)
    """
    user = session.query(User).filter(User.email == email).first()
    if not user:
        return None, "Invalid email or password"
    
    if not verify_password(password, user.password_hash):
        return None, "Invalid email or password"
    
    return user, None


def initialize_blood_groups(session: Session):
    """Initialize blood groups if they don't exist"""
    blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    
    for blood_type in blood_types:
        existing = session.query(BloodGroup).filter(BloodGroup.blood_type == blood_type).first()
        if not existing:
            blood_id = generate_id(session, BloodGroup, "blood_id", "BG")
            blood_group = BloodGroup(blood_id=blood_id, blood_type=blood_type)
            session.add(blood_group)
    
    session.commit()

