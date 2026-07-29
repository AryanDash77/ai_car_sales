import streamlit as st
from db.database import SessionLocal, init_db
from modules.user_module import register_user, authenticate_user
from modules.inventory_module import search_cars, add_car

init_db()  # ensures tables exist even on a teammate's fresh clone

st.set_page_config(page_title="AI Car Sales System", layout="wide")

if "user" not in st.session_state:
    st.session_state.user = None

db = SessionLocal()

st.sidebar.title("🚗 AI Car Sales")

if st.session_state.user:
    st.sidebar.write(f"Logged in as **{st.session_state.user.name}** ({st.session_state.user.role})")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()
    nav_options = ["Browse Cars"]
    if st.session_state.user.role == "admin":
        nav_options.append("Admin: Add Car")
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

            