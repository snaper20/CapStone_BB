"""
Role-based pages for different user types
"""
import streamlit as st
from database import (
    get_session, User, BloodGroup, BloodRequest, BloodDonation, 
    BloodInventory, RoleEnum, GenderEnum
)
from datetime import datetime, date
from auth import generate_id


def donor_page(engine, user):
    """Donor page functionality"""
    st.header("👤 Donor Dashboard")
    
    tab1, tab2, tab3 = st.tabs(["My Profile", "Donate Blood", "My Donations"])
    
    with tab1:
        session = get_session(engine)
        db_user = session.query(User).filter(User.user_id == user["user_id"]).first()
        
        if db_user:
            st.subheader("Profile Information")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Name:** {db_user.first_name} {db_user.last_name or ''}")
                st.write(f"**Email:** {db_user.email}")
                st.write(f"**Mobile:** {db_user.mobile_no}")
                st.write(f"**Pincode:** {db_user.pincode}")
            
            with col2:
                st.write(f"**Blood Group:** {db_user.blood_group.blood_type if db_user.blood_group else 'Not set'}")
                st.write(f"**Gender:** {db_user.gender.value if db_user.gender else 'Not set'}")
                st.write(f"**Date of Birth:** {db_user.date_of_birth or 'Not set'}")
                st.write(f"**Last Donation:** {db_user.last_donation_date or 'Never'}")
        
        session.close()
    
    with tab2:
        st.subheader("Register Blood Donation")
        
        session = get_session(engine)
        db_user = session.query(User).filter(User.user_id == user["user_id"]).first()
        
        if not db_user.blood_group:
            st.warning("Please update your blood group in profile first.")
        else:
            with st.form("donation_form"):
                donation_date = st.date_input("Donation Date", value=date.today())
                units = st.number_input("Units Donated", min_value=1, max_value=2, value=1)
                health_check = st.selectbox("Health Check Passed", ["yes", "no"])
                notes = st.text_area("Notes (optional)")
                
                submit = st.form_submit_button("Submit Donation")
                
                if submit:
                    donation_id = generate_id(session, BloodDonation, "donation_id", "DN")
                    donation = BloodDonation(
                        donation_id=donation_id,
                        donor_id=db_user.user_id,
                        blood_id=db_user.blood_id,
                        donation_date=datetime.combine(donation_date, datetime.min.time()),
                        units_donated=units,
                        health_check_passed=health_check,
                        notes=notes,
                        status="completed"
                    )
                    session.add(donation)
                    
                    # Update user's last donation date
                    db_user.last_donation_date = donation_date
                    
                    # Update inventory
                    inventory = session.query(BloodInventory).filter(
                        BloodInventory.blood_id == db_user.blood_id
                    ).first()
                    
                    if not inventory:
                        inv_id = generate_id(session, BloodInventory, "inventory_id", "IN")
                        inventory = BloodInventory(
                            inventory_id=inv_id,
                            blood_id=db_user.blood_id,
                            units_available=units
                        )
                        session.add(inventory)
                    else:
                        inventory.units_available += units
                    
                    session.commit()
                    st.success("Donation recorded successfully!")
                    session.close()
                    st.rerun()
        
        session.close()
    
    with tab3:
        st.subheader("My Donation History")
        session = get_session(engine)
        donations = session.query(BloodDonation).filter(
            BloodDonation.donor_id == user["user_id"]
        ).order_by(BloodDonation.donation_date.desc()).all()
        
        if donations:
            for donation in donations:
                with st.container():
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Date:** {donation.donation_date.date()}")
                    with col2:
                        st.write(f"**Units:** {donation.units_donated}")
                    with col3:
                        st.write(f"**Status:** {donation.status}")
                    st.write(f"**Blood Group:** {donation.blood_group.blood_type}")
                    if donation.notes:
                        st.write(f"*Notes: {donation.notes}*")
                    st.markdown("---")
        else:
            st.info("No donations recorded yet.")
        
        session.close()


def requester_page(engine, user):
    """Requester page functionality"""
    st.header("🩺 Blood Request Dashboard")
    
    tab1, tab2 = st.tabs(["Request Blood", "My Requests"])
    
    with tab1:
        st.subheader("Create Blood Request")
        session = get_session(engine)
        
        blood_groups = session.query(BloodGroup).all()
        blood_options = {bg.blood_type: bg.blood_id for bg in blood_groups}
        
        with st.form("request_form"):
            blood_type = st.selectbox("Blood Group Required *", [""] + list(blood_options.keys()))
            units_required = st.number_input("Units Required *", min_value=1, max_value=10, value=1)
            urgency = st.selectbox("Urgency Level", ["normal", "urgent", "critical"])
            hospital_name = st.text_input("Hospital/Clinic Name")
            notes = st.text_area("Additional Notes")
            
            submit = st.form_submit_button("Submit Request")
            
            if submit:
                if not blood_type:
                    st.error("Please select a blood group")
                else:
                    request_id = generate_id(session, BloodRequest, "request_id", "RQ")
                    request = BloodRequest(
                        request_id=request_id,
                        requester_id=user["user_id"],
                        blood_id=blood_options[blood_type],
                        units_required=units_required,
                        urgency=urgency,
                        hospital_name=hospital_name,
                        notes=notes,
                        status="pending"
                    )
                    session.add(request)
                    session.commit()
                    st.success("Blood request submitted successfully!")
                    session.close()
                    st.rerun()
        
        session.close()
    
    with tab2:
        st.subheader("My Blood Requests")
        session = get_session(engine)
        requests = session.query(BloodRequest).filter(
            BloodRequest.requester_id == user["user_id"]
        ).order_by(BloodRequest.request_date.desc()).all()
        
        if requests:
            for req in requests:
                with st.container():
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Date:** {req.request_date.date()}")
                    with col2:
                        st.write(f"**Blood Group:** {req.blood_group.blood_type}")
                    with col3:
                        status_color = {"pending": "🟡", "fulfilled": "🟢", "cancelled": "🔴"}
                        st.write(f"**Status:** {status_color.get(req.status, '⚪')} {req.status.upper()}")
                    
                    st.write(f"**Units Required:** {req.units_required}")
                    st.write(f"**Urgency:** {req.urgency.upper()}")
                    if req.hospital_name:
                        st.write(f"**Hospital:** {req.hospital_name}")
                    if req.notes:
                        st.write(f"*Notes: {req.notes}*")
                    st.markdown("---")
        else:
            st.info("No blood requests yet.")
        
        session.close()


def staff_page(engine, user):
    """Staff page functionality"""
    st.header("🏥 Staff Dashboard")
    
    tab1, tab2, tab3 = st.tabs(["Blood Inventory", "Pending Requests", "Donations"])
    
    with tab1:
        st.subheader("Blood Inventory Management")
        session = get_session(engine)
        
        inventory = session.query(BloodInventory).all()
        
        if inventory:
            st.dataframe(
                [
                    {
                        "Blood Type": inv.blood_group.blood_type,
                        "Available": inv.units_available,
                        "Reserved": inv.units_reserved,
                        "Total": inv.units_available + inv.units_reserved
                    }
                    for inv in inventory
                ],
                use_container_width=True
            )
        else:
            st.info("No inventory records yet.")
        
        session.close()
    
    with tab2:
        st.subheader("Pending Blood Requests")
        session = get_session(engine)
        
        requests = session.query(BloodRequest).filter(
            BloodRequest.status == "pending"
        ).order_by(
            BloodRequest.urgency.desc(),
            BloodRequest.request_date
        ).all()
        
        if requests:
            for req in requests:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Request ID:** {req.request_id}")
                        st.write(f"**Blood Group:** {req.blood_group.blood_type} | **Units:** {req.units_required}")
                        st.write(f"**Requester:** {req.requester.first_name} {req.requester.last_name or ''}")
                        st.write(f"**Urgency:** {req.urgency.upper()}")
                        if req.hospital_name:
                            st.write(f"**Hospital:** {req.hospital_name}")
                        st.write(f"**Date:** {req.request_date.date()}")
                    
                    with col2:
                        # Check if we have enough inventory
                        inventory = session.query(BloodInventory).filter(
                            BloodInventory.blood_id == req.blood_id
                        ).first()
                        
                        available = inventory.units_available if inventory else 0
                        
                        if available >= req.units_required:
                            if st.button("Fulfill", key=f"fulfill_{req.request_id}"):
                                req.status = "fulfilled"
                                req.fulfilled_date = datetime.utcnow()
                                if inventory:
                                    inventory.units_available -= req.units_required
                                session.commit()
                                st.success("Request fulfilled!")
                                st.rerun()
                        else:
                            st.warning(f"Only {available} units available")
                    
                    st.markdown("---")
        else:
            st.info("No pending requests.")
        
        session.close()
    
    with tab3:
        st.subheader("Recent Donations")
        session = get_session(engine)
        
        donations = session.query(BloodDonation).order_by(
            BloodDonation.donation_date.desc()
        ).limit(20).all()
        
        if donations:
            st.dataframe(
                [
                    {
                        "Date": don.donation_date.date(),
                        "Donor": f"{don.donor.first_name} {don.donor.last_name or ''}",
                        "Blood Type": don.blood_group.blood_type,
                        "Units": don.units_donated,
                        "Status": don.status
                    }
                    for don in donations
                ],
                use_container_width=True
            )
        else:
            st.info("No donations recorded yet.")
        
        session.close()


def admin_page(engine, user):
    """Admin page functionality"""
    st.header("⚙️ Admin Dashboard")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Users", "Inventory", "All Requests", "Statistics"])
    
    with tab1:
        st.subheader("User Management")
        session = get_session(engine)
        
        users = session.query(User).all()
        
        if users:
            user_data = []
            for u in users:
                user_data.append({
                    "User ID": u.user_id,
                    "Name": f"{u.first_name} {u.last_name or ''}",
                    "Email": u.email,
                    "Role": u.role.value if u.role else "donor",
                    "Blood Type": u.blood_group.blood_type if u.blood_group else "N/A",
                    "Mobile": u.mobile_no
                })
            
            st.dataframe(user_data, use_container_width=True)
            
            # Role management
            st.subheader("Change User Role")
            with st.form("change_role"):
                user_id = st.selectbox("Select User", [u.user_id for u in users])
                new_role = st.selectbox("New Role", ["donor", "requester", "staff", "admin"])
                submit = st.form_submit_button("Update Role")
                
                if submit:
                    target_user = session.query(User).filter(User.user_id == user_id).first()
                    if target_user:
                        target_user.role = RoleEnum[new_role.upper()]
                        session.commit()
                        st.success(f"Role updated to {new_role}")
                        st.rerun()
        else:
            st.info("No users found.")
        
        session.close()
    
    with tab2:
        st.subheader("Inventory Management")
        session = get_session(engine)
        
        # Show current inventory
        inventory = session.query(BloodInventory).all()
        if inventory:
            st.dataframe(
                [
                    {
                        "Blood Type": inv.blood_group.blood_type,
                        "Available": inv.units_available,
                        "Reserved": inv.units_reserved
                    }
                    for inv in inventory
                ],
                use_container_width=True
            )
        else:
            st.info("No inventory records.")
        
        session.close()
    
    with tab3:
        st.subheader("All Blood Requests")
        session = get_session(engine)
        
        requests = session.query(BloodRequest).order_by(
            BloodRequest.request_date.desc()
        ).all()
        
        if requests:
            st.dataframe(
                [
                    {
                        "Request ID": req.request_id,
                        "Requester": f"{req.requester.first_name} {req.requester.last_name or ''}",
                        "Blood Type": req.blood_group.blood_type,
                        "Units": req.units_required,
                        "Urgency": req.urgency,
                        "Status": req.status,
                        "Date": req.request_date.date()
                    }
                    for req in requests
                ],
                use_container_width=True
            )
        else:
            st.info("No requests found.")
        
        session.close()
    
    with tab4:
        st.subheader("System Statistics")
        session = get_session(engine)
        
        total_users = session.query(User).count()
        total_donors = session.query(User).filter(User.role == RoleEnum.DONOR).count()
        total_requests = session.query(BloodRequest).count()
        total_donations = session.query(BloodDonation).count()
        pending_requests = session.query(BloodRequest).filter(BloodRequest.status == "pending").count()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Users", total_users)
        with col2:
            st.metric("Donors", total_donors)
        with col3:
            st.metric("Total Requests", total_requests)
        with col4:
            st.metric("Total Donations", total_donations)
        with col5:
            st.metric("Pending Requests", pending_requests)
        
        session.close()

