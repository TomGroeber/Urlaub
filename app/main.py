import streamlit as st
from database import init_db, session, User, Vacation
from user_auth import register_user, login_user
import os
from datetime import date, timedelta
import calendar

# Initialize the database if not already initialized
if not os.path.exists("vacation_manager.db"):
    st.write("Initializing database...")
    init_db()
    register_user("user1", "user1@example.com", "user1pass", 14, "Dreher")
    register_user("user2", "user2@example.com", "user2pass", 14, "Fräser")
    register_user("user3", "user3@example.com", "user3pass", 14, "Dreher")
    register_user("admin", "admin@example.com", "adminpass", 0, "Admin")
    st.experimental_rerun()

# Funktion zum Zurücksetzen der Urlaubsdaten
def reset_vacations():
    session.query(Vacation).delete()
    session.commit()

# Funktion zum Löschen eines bestimmten Urlaubs
def delete_vacation(vacation_id):
    session.query(Vacation).filter(Vacation.id == vacation_id).delete()
    session.commit()

# Funktion zum Berechnen der verwendeten Urlaubstage
def calculate_used_vacation_days(user_id):
    approved_vacations = session.query(Vacation).filter_by(user_id=user_id, status='approved').all()
    used_days = sum((vacation.end_date - vacation.start_date).days + 1 for vacation in approved_vacations)
    return used_days

# Funktion zum Formatieren des Datums
def format_date(d):
    return d.strftime('%d-%m-%Y')

# Streamlit-Layout
st.title("Vacation Manager")

# Registrierung und Login
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    # Registrierung und Login
    choice = st.sidebar.selectbox("Choose Action", ["Login", "Register"])
    
    if choice == "Register":
        st.subheader("Create New Account")
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        vacation_days = st.number_input("Vacation Days", min_value=0)
        role = st.selectbox("Role", ["Dreher", "Fräser", "Alles"])
        if st.button("Register"):
            try:
                register_user(username, email, password, vacation_days, role)
                st.success("Account created successfully!")
            except Exception as e:
                st.error(f"Error: {e}")
    
    if choice == "Login":
        st.subheader("Login to Your Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            try:
                user = login_user(username, password)
                if user:
                    st.session_state.user = user
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials")
            except Exception as e:
                st.error(f"Error: {e}")

else:
    user = st.session_state.user
    try:
        used_days = calculate_used_vacation_days(user.id)
        remaining_days = user.vacation_days - used_days
    except Exception as e:
        st.error(f"Error calculating vacation days: {e}")
        remaining_days = user.vacation_days

    st.write(f"Welcome, {user.username}!")
    st.write(f"Role: {user.role}")
    st.write(f"You have {remaining_days} vacation days remaining.")

    # Admin-Ansicht
    if user.username == 'admin':
        st.subheader("Admin View: Vacation Requests")

        # Überschrift für jede Spalte
        col1, col2, col3, col4, col5 = st.columns([3, 2, 1.5, 2.5, 1.5])
        with col1:
            st.markdown("**Request Details**")
        with col2:
            st.markdown("**Actions**")
        with col3:
            st.markdown("**Delete**")
        with col4:
            st.markdown("**Update Dates**")
        with col5:
            st.markdown("**Days Left**")

        for vacation in session.query(Vacation).all():
            requester = session.query(User).filter_by(id=vacation.user_id).first()
            col1, col2, col3, col4, col5 = st.columns([3, 2, 1.5, 2.5, 1.5])
            with col1:
                st.write(f"**{requester.username} ({requester.role}):** {format_date(vacation.start_date)} to {format_date(vacation.end_date)} ({vacation.status})")
                st.write(f"**Note:** {vacation.note}")
            with col2:
                if vacation.status == 'pending':
                    if st.button(f"Approve {vacation.id}", key=f"approve_{vacation.id}"):
                        days_requested = (vacation.end_date - vacation.start_date).days + 1
                        if requester.vacation_days >= days_requested:
                            vacation.status = 'approved'
                            session.commit()
                            st.experimental_rerun()
                        else:
                            st.warning(f"Not enough vacation days for {requester.username}")
                    if st.button(f"Deny {vacation.id}", key=f"deny_{vacation.id}"):
                        vacation.status = 'denied'
                        session.commit()
                        st.experimental_rerun()
            with col3:
                if st.button(f"Delete {vacation.id}", key=f"delete_{vacation.id}"):
                    delete_vacation(vacation.id)
                    session.commit()
                    st.experimental_rerun()
            with col4:
                new_start_date = st.date_input("Start Date", vacation.start_date, key=f"start_{vacation.id}")
                new_end_date = st.date_input("End Date", vacation.end_date, key=f"end_{vacation.id}")
                if st.button(f"Update {vacation.id}", key=f"update_{vacation.id}"):
                    vacation.start_date = new_start_date
                    vacation.end_date = new_end_date
                    session.commit()
                    st.experimental_rerun()
            with col5:
                requester_used_days = calculate_used_vacation_days(requester.id)
                requester_remaining_days = requester.vacation_days - requester_used_days
                st.write(f"{requester_remaining_days} days left")

        # Knopf zum Zurücksetzen der Urlaubsdaten
        st.markdown("---")
        if st.button("Reset All Vacations"):
            reset_vacations()
            st.experimental_rerun()
            st.success("All vacation entries have been reset.")

    # Benutzeransicht
    else:
        st.subheader("Your Vacation Calendar")
        
        # Legende
        st.markdown("""
        <div style='display: flex; justify-content: space-around;'>
            <div style='background-color: green; padding: 5px; color: white;'>Approved</div>
            <div style='background-color: orange; padding: 5px; color: white;'>Pending</div>
            <div style='background-color: red; padding: 5px; color: white;'>Denied</div>
            <div style='background-color: darkblue; padding: 5px; color: white;'>Selected</div>
        </div>
        """, unsafe_allow_html=True)

        today = date.today()

        # Monat und Jahr Auswahl (nur August bis Dezember 2024)
        months = ["August", "September", "October", "November", "December"]
        month_numbers = {month: index + 8 for index, month in enumerate(months)}
        selected_month = st.selectbox("Select Month", months)
        selected_year = 2024

        # Umwandlung des ausgewählten Monats in eine Zahl
        month_index = month_numbers[selected_month]
        
        days_in_month = calendar.monthrange(selected_year, month_index)[1]

        # Kalender für den ausgewählten Monat anzeigen
        cal = calendar.monthcalendar(selected_year, month_index)
        st.write(f"{selected_month} {selected_year}")

        # Kalender-Interaktion
        if 'vacation_start' not in st.session_state:
            st.session_state.vacation_start = None
        if 'vacation_end' not in st.session_state:
            st.session_state.vacation_end = None

        # Angefragte Urlaubszeiten aus der Datenbank abrufen
        requested_vacations = session.query(Vacation).filter_by(user_id=user.id, status='pending').all()
        requested_dates = []
        for vacation in requested_vacations:
            requested_dates.extend([vacation.start_date + timedelta(days=i) for i in range((vacation.end_date - vacation.start_date).days + 1)])

        # Genehmigte Urlaubszeiten aus der Datenbank abrufen
        approved_vacations = session.query(Vacation).filter_by(user_id=user.id, status='approved').all()
        approved_dates = []
        for vacation in approved_vacations:
            approved_dates.extend([vacation.start_date + timedelta(days=i) for i in range((vacation.end_date - vacation.start_date).days + 1)])

        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day == 0:
                    cols[i].markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
                else:
                    day_date = date(selected_year, month_index, day)
                    vacations = session.query(Vacation).filter_by(user_id=user.id, start_date=day_date).all()
                    if vacations:
                        status = vacations[0].status
                        color = "green" if status == 'approved' else "orange" if status == 'pending' else "red"
                    else:
                        color = "white"  # Standardfarbe setzen
                        if st.session_state.vacation_start and st.session_state.vacation_end:
                            if st.session_state.vacation_start <= day_date <= st.session_state.vacation_end:
                                color = "darkblue"
                        elif st.session_state.vacation_start and not st.session_state.vacation_end:
                            if day_date == st.session_state.vacation_start:
                                color = "darkblue"
                        elif day_date in requested_dates:
                            color = "orange"
                        elif day_date in approved_dates:
                            color = "green"

                    if cols[i].button(f"{day}", key=str(day_date), help=f"Select {day_date}", use_container_width=True):
                        if st.session_state.vacation_start is None:
                            st.session_state.vacation_start = day_date
                        elif st.session_state.vacation_end is None:
                            if day_date >= st.session_state.vacation_start:
                                st.session_state.vacation_end = day_date
                            else:
                                st.session_state.vacation_start = day_date
                        else:
                            st.session_state.vacation_start = day_date
                            st.session_state.vacation_end = None
                        st.experimental_rerun()
                    
                    cols[i].markdown(f"<div style='background-color:{color}; padding:5px; font-size:small; text-align:center; border-radius: 5px; height: 40px; line-height: 40px;'>{day}</div>", unsafe_allow_html=True)

        if st.session_state.vacation_start and st.session_state.vacation_end:
            st.write(f"Selected vacation from {format_date(st.session_state.vacation_start)} to {format_date(st.session_state.vacation_end)}")
            if st.session_state.vacation_start > st.session_state.vacation_end:
                st.error("End date must be after start date")
            else:
                days_requested = (st.session_state.vacation_end - st.session_state.vacation_start).days + 1
                note = st.text_area("Enter a note for your vacation (optional)")
                if days_requested > remaining_days:
                    st.error(f"You only have {remaining_days} vacation days remaining.")
                else:
                    if st.button("Request Vacation"):
                        new_vacation = Vacation(user_id=user.id, start_date=st.session_state.vacation_start, end_date=st.session_state.vacation_end, status='pending', note=note)
                        session.add(new_vacation)
                        session.commit()
                        st.success("Vacation request submitted!")
                        st.session_state.vacation_start = None
                        st.session_state.vacation_end = None
                        st.experimental_rerun()

        # Knopf zum Zurücksetzen der Auswahl
        if st.button("Clear Selection"):
            st.session_state.vacation_start = None
            st.session_state.vacation_end = None
            st.experimental_rerun()

        # Übersicht über alle Urlaubsanfragen des Mitarbeiters
        st.subheader("Your Vacation Requests Overview")
        vacations = session.query(Vacation).filter_by(user_id=user.id).all()
        if vacations:
            for vacation in vacations:
                st.write(f"{format_date(vacation.start_date)} to {format_date(vacation.end_date)} - {vacation.status} - Note: {vacation.note}")
        else:
            st.write("No vacation requests found.")
