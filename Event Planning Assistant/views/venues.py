import streamlit as st
from backend.database import get_connection
import datetime

def venues_page():
    st.title("🏢 Venue Browser & Booking")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, type, capacity, location, rating, booked_dates FROM venues")
    venues = cursor.fetchall()
    conn.close()

    if not venues:
        st.info("No venues available in the database yet. Please add some manually.")
        return

    # Venue filter
    venue_type = st.selectbox("Filter by Type", ["All", "Banquet Hall", "Open Ground", "Hotel", "Resort"])
    capacity_filter = st.number_input("Minimum Capacity", min_value=0, step=10)

    for v in venues:
        vid, name, vtype, capacity, location, rating, booked_dates = v

        if venue_type != "All" and vtype != venue_type:
            continue
        if capacity < capacity_filter:
            continue

        with st.expander(f"{name} ({vtype}) - {capacity} guests"):
            st.write(f"📍 Location: {location}")
            st.write(f"⭐ Rating: {rating}/5.0")
            st.write(f"📅 Already booked on: {booked_dates if booked_dates else 'None'}")

            date = st.date_input(f"Select booking date for {name}", datetime.date.today(), key=f"date_{vid}")
            
            if st.button(f"Book {name}", key=f"book_{vid}"):
                conn = get_connection()
                cursor = conn.cursor()
                # Check if already booked
                cursor.execute("SELECT booked_dates FROM venues WHERE id=?", (vid,))
                existing = cursor.fetchone()[0]
                if existing:
                    existing_dates = existing.split(",")
                else:
                    existing_dates = []

                if str(date) in existing_dates:
                    st.error("❌ This date is already booked for this venue.")
                else:
                    existing_dates.append(str(date))
                    cursor.execute("UPDATE venues SET booked_dates=? WHERE id=?", (",".join(existing_dates), vid))
                    conn.commit()
                    st.success(f"✅ Successfully booked {name} on {date}!")
                conn.close()

if __name__ == "__main__":
    venues_page()
