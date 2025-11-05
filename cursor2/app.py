"""
Main Streamlit application for Blood Management System
"""
import streamlit as st
from database import get_or_create_engine, User, RoleEnum
from auth import authenticate_user, register_user, initialize_blood_groups, get_session
from pages import donor_page, requester_page, staff_page, admin_page
from sqlalchemy.orm import Session


def init_session_state():
    """Initialize session state variables"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "db_engine" not in st.session_state:
        st.session_state.db_engine = get_or_create_engine()
        # Initialize blood groups
        session = get_session(st.session_state.db_engine)
        initialize_blood_groups(session)
        session.close()


def login_page():
    """Display login page"""
    st.title("🩸 Blood Management System")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if email and password:
                    session = get_session(st.session_state.db_engine)
                    user, error = authenticate_user(session, email, password)
                    session.close()
                    
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user = {
                            "user_id": user.user_id,
                            "email": user.email,
                            "first_name": user.first_name,
                            "last_name": user.last_name,
                            "role": user.role.value if user.role else "donor"
                        }
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error(error or "Invalid credentials")
                else:
                    st.error("Please fill in all fields")
    
    with tab2:
        st.subheader("Register")
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name *")
                email = st.text_input("Email *")
                mobile_no = st.text_input("Mobile Number (10 digits) *")
                password = st.text_input("Password *", type="password")
            
            with col2:
                last_name = st.text_input("Last Name")
                pincode = st.text_input("Pincode (6 digits) *")
                date_of_birth = st.date_input("Date of Birth", value=None)
                gender = st.selectbox("Gender", ["", "M", "F", "O"])
            
            blood_type = st.selectbox(
                "Blood Group",
                ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
            )
            
            role = st.selectbox(
                "Role",
                ["donor", "requester"],
                help="Staff and Admin roles require manual assignment"
            )
            
            submit = st.form_submit_button("Register")
            
            if submit:
                if not all([first_name, email, mobile_no, password, pincode]):
                    st.error("Please fill in all required fields (*)")
                else:
                    session = get_session(st.session_state.db_engine)
                    user, error = register_user(
                        session=session,
                        first_name=first_name,
                        last_name=last_name if last_name else None,
                        email=email,
                        mobile_no=mobile_no,
                        password=password,
                        pincode=pincode,
                        date_of_birth=date_of_birth,
                        gender=gender if gender else None,
                        blood_type=blood_type if blood_type else None,
                        role=role
                    )
                    session.close()
                    
                    if user:
                        st.success("Registration successful! Please login.")
                    else:
                        st.error(error or "Registration failed")


def main():
    """Main application"""
    init_session_state()
    
    if not st.session_state.authenticated:
        login_page()
    else:
        # Display user info and logout
        user = st.session_state.user
        col1, col2 = st.columns([3, 1])
        with col1:
            st.title(f"Welcome, {user['first_name']}!")
        with col2:
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.rerun()
        
        st.markdown("---")
        
        # Route to appropriate page based on role
        role = user["role"]
        
        if role == "donor":
            donor_page(st.session_state.db_engine, user)
        elif role == "requester":
            requester_page(st.session_state.db_engine, user)
        elif role == "staff":
            staff_page(st.session_state.db_engine, user)
        elif role == "admin":
            admin_page(st.session_state.db_engine, user)
        else:
            st.error("Unknown role. Please contact administrator.")


if __name__ == "__main__":
    main()

