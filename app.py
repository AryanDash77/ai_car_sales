import streamlit as st
from datetime import datetime
from db.database import SessionLocal, init_db

# Make sure these import paths match your exact file names
from modules.user_module import register_user, authenticate_user
from modules.inventory_module import search_cars, add_car
from modules.order_module import (
    place_order, book_test_drive, list_orders_for_user, 
    list_test_drives_for_user, list_all_orders, update_order_status
)
from modules.admin_module import get_sales_summary, get_inventory_summary

init_db()  # ensures tables exist

st.set_page_config(page_title="AI Car Sales System", layout="wide")

# --- CUSTOM CSS FOR DARK THEME & GLASSMORPHISM ---
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stTextInput input, .stSelectbox select, .stNumberInput input, .stDateInput input, .stTimeInput input {
        background: rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        border-radius: 8px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #6e8efb, #a777e3);
        border: none;
        border-radius: 8px;
        color: white;
        transition: 0.3s;
    }
    .stButton>button:hover {
        box-shadow: 0 0 15px rgba(167, 119, 227, 0.5);
    }
</style>
""", unsafe_allow_html=True)

if "user" not in st.session_state:
    st.session_state.user = None

# Open DB connection for this run
db = SessionLocal()

try:
    st.sidebar.title(" AI Car Sales System")

    if st.session_state.user:
        st.sidebar.write(f"Logged in as **{st.session_state.user.name}** ({st.session_state.user.role})")
        if st.sidebar.button("Logout"):
            st.session_state.user = None
            st.rerun()
        
        # Base options for everyone
        nav_options = ["Browse Cars", "My Profile & Orders"]
        
        # Extra options for admins
        if st.session_state.user.role == "admin":
            nav_options.extend(["Admin: Dashboard", "Admin: Manage Orders", "Admin: Add Car"])
            
        page = st.sidebar.radio("Navigate", nav_options)
    else:
        page = st.sidebar.radio("Navigate", ["Login", "Sign Up"])

    # ---------------- LOGIN ----------------
    if page == "Login":
        st.title("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = authenticate_user(db, email, password)
            if user:
                st.session_state.user = user
                st.success(f"Welcome back, {user.name}!")
                st.rerun()
            else:
                st.error("Invalid email or password.")

    # ---------------- SIGN UP ----------------
    elif page == "Sign Up":
        st.title("Create an Account")
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Sign Up"):
            try:
                register_user(db, name, email, password)
                st.success("Account created! Please log in.")
            except ValueError as e:
                st.error(str(e))

    # ---------------- BROWSE CARS ----------------
    elif page == "Browse Cars":
        st.title("Browse Cars")
        col1, col2, col3 = st.columns(3)
        brand = col1.text_input("Brand")
        body_type = col2.selectbox("Body Type", ["", "SUV", "Sedan", "Hatchback"])
        max_price = col3.number_input("Max Price (₹)", min_value=0, value=0)

        results = search_cars(
            db,
            brand=brand or None,
            body_type=body_type or None,
            max_price=max_price or None,
        )

        if not results:
            st.info("No cars found.")
            
        for car in results:
            st.subheader(f"{car.brand} {car.model} ({car.year})")
            st.write(f"Price: ₹{car.price:,.0f} | Fuel: {car.fuel_type} | Stock: {car.stock_qty}")
            
            # Action Buttons for Logged-In Users
            if st.session_state.user:
                action_col1, action_col2 = st.columns(2)
                
                with action_col1:
                    if st.button("Buy Now", key=f"buy_{car.id}"):
                        try:
                            place_order(db, st.session_state.user.id, car.id)
                            st.success("Order placed successfully! Check 'My Profile' for status.")
                        except ValueError as e:
                            st.error(str(e))
                            
                with action_col2:
                    with st.expander("Book Test Drive"):
                        d = st.date_input("Date", key=f"date_{car.id}")
                        t = st.time_input("Time", key=f"time_{car.id}")
                        if st.button("Confirm Booking", key=f"book_{car.id}"):
                            try:
                                slot = datetime.combine(d, t)
                                book_test_drive(db, st.session_state.user.id, car.id, slot)
                                st.success("Test drive booked!")
                            except ValueError as e:
                                st.error(str(e))
            st.divider()

    # ---------------- CUSTOMER: MY PROFILE & ORDERS ----------------
    elif page == "My Profile & Orders":
        st.title("My Profile")
        
        st.subheader("My Vehicle Orders")
        orders = list_orders_for_user(db, st.session_state.user.id)
        if not orders:
            st.info("You haven't placed any orders yet.")
        else:
            for o in orders:
                st.write(f"**Order #{o.id}** | Car ID: {o.car_id} | Status: `{o.status}` | Date: {o.created_at.strftime('%Y-%m-%d')}")
                
        st.divider()
        
        st.subheader("My Test Drives")
        test_drives = list_test_drives_for_user(db, st.session_state.user.id)
        if not test_drives:
            st.info("No test drives booked.")
        else:
            for td in test_drives:
                st.write(f"**Booking #{td.id}** | Car ID: {td.car_id} | Slot: {td.slot_datetime.strftime('%Y-%m-%d %H:%M')} | Status: `{td.status}`")

    # ---------------- ADMIN: DASHBOARD ----------------
    elif page == "Admin: Dashboard":
        st.title("Admin Dashboard")
        
        sales_data = get_sales_summary(db)
        inv_data = get_inventory_summary(db)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Revenue", f"₹{sales_data['total_revenue']:,.0f}")
        col2.metric("Total Orders", sales_data['total_orders'])
        col3.metric("Stock Units", inv_data['total_stock_units'])
        
        st.divider()
        st.subheader("Order Breakdown")
        st.write(sales_data['orders_by_status'])

    # ---------------- ADMIN: MANAGE ORDERS ----------------
    elif page == "Admin: Manage Orders":
        st.title("Manage Orders")
        all_orders = list_all_orders(db)
        
        if not all_orders:
            st.info("No orders in the system.")
        else:
            for o in all_orders:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Order #{o.id}** | User ID: {o.user_id} | Car ID: {o.car_id} | Current Status: `{o.status}`")
                with col2:
                    new_status = st.selectbox("Update Status", ["pending", "confirmed", "cancelled"], key=f"status_{o.id}", index=["pending", "confirmed", "cancelled"].index(o.status))
                    if st.button("Update", key=f"update_{o.id}"):
                        update_order_status(db, o.id, new_status)
                        st.success("Updated!")
                        st.rerun()
                st.divider()

    # ---------------- ADMIN: ADD CAR ----------------
    elif page == "Admin: Add Car":
        st.title("Add New Car")
        brand = st.text_input("Brand")
        model = st.text_input("Model")
        year = st.number_input("Year", min_value=2000, max_value=2027, value=2024)
        price = st.number_input("Price (₹)", min_value=0.0)
        fuel_type = st.selectbox("Fuel Type", ["Petrol", "Diesel", "Electric", "Hybrid"])
        body_type = st.selectbox("Body Type", ["Sedan", "SUV", "Hatchback"])
        stock_qty = st.number_input("Stock Quantity", min_value=0, value=1)
        
        if st.button("Add Car"):
            try:
                add_car(db, brand, model, int(year), price, fuel_type, body_type, stock_qty=int(stock_qty))
                st.success(f"{brand} {model} added to inventory!")
            except ValueError as e:
                st.error(str(e))

finally:
    # Ensure the DB session is ALWAYS closed
    db.close()


