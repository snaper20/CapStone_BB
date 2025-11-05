# Blood Management System

A comprehensive blood management system built with Streamlit, featuring user authentication and role-based access control.

## Features

- **User Authentication**: Secure login and registration with password hashing
- **Role-Based Access Control**: Four user roles with different permissions:
  - **Donor**: Can view profile, record blood donations, view donation history
  - **Requester**: Can create blood requests and view request status
  - **Staff**: Can manage inventory, fulfill requests, view donations
  - **Admin**: Full system access including user management and statistics

## Database Schema

### Users Table
- `user_id`: Unique identifier (U0001, U0002, etc.)
- `blood_id`: Foreign key to blood_groups table
- `first_name`: User's first name (required)
- `last_name`: User's last name (optional)
- `email`: Unique email address (required, validated)
- `mobile_no`: 10-digit mobile number (required, unique, validated)
- `password_hash`: Bcrypt hashed password
- `date_of_birth`: Date of birth
- `gender`: M (Male), F (Female), or O (Other)
- `pincode`: 6-digit postal code (100000-999999, required)
- `created_at`: Account creation timestamp
- `last_donation_date`: Date of last blood donation
- `role`: User role (donor, requester, staff, admin)

### Additional Tables
- `blood_groups`: Blood type information (A+, A-, B+, B-, AB+, AB-, O+, O-)
- `blood_requests`: Blood request records
- `blood_donations`: Blood donation records
- `blood_inventory`: Current blood inventory levels

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
streamlit run app.py
```

3. Access the application in your browser (typically at `http://localhost:8501`)

## Usage

### First Time Setup

1. Register a new account (default role is "donor")
2. Login with your credentials
3. For admin/staff access, you'll need to manually update the role in the database or use the admin panel if you have admin access

### Creating Admin User

To create an admin user, you can either:
1. Register normally and then manually update the role in the database
2. Use an existing admin account to change roles via the Admin Dashboard

### User Roles

- **Donor**: View profile, record donations, view donation history
- **Requester**: Create blood requests, view request status
- **Staff**: View inventory, fulfill requests, manage donations
- **Admin**: Full access including user management, statistics, and system configuration

## Project Structure

```
.
├── app.py              # Main Streamlit application
├── pages.py            # Role-based page implementations
├── database.py         # Database models and setup
├── auth.py             # Authentication and authorization
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Security Features

- Password hashing using bcrypt
- Email and mobile number validation
- Pincode validation (6 digits, 100000-999999)
- Session-based authentication
- Role-based access control

## Database

The system uses SQLite by default (`blood_management.db`). The database is automatically created on first run with all necessary tables and initial blood group data.

## Notes

- Staff and Admin roles require manual assignment (cannot be selected during registration)
- Blood inventory is automatically updated when donations are recorded
- Requests can be fulfilled by staff members when sufficient inventory is available

