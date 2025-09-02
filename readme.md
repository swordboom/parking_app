# Parking Vehicle App

## Project Overview
The **Parking Vehicle App** is a multi-user web application built using Flask that manages parking lots, parking spots, and parked vehicles (for 4-wheelers). It allows users to book, release, and view parking history while providing an admin interface to manage parking lots, users, and overall occupancy.

---

## Project Structure
```
parking_app/
│
├── controllers/             # Flask Blueprints for routes
│   ├── auth_controller.py   # Handles signup, login, logout
│   ├── user_controller.py   # User dashboard, booking, release
│   ├── admin_controller.py  # Admin features and summary
│
├── models/
│   └── parking_model.py     # Database operations and queries
│
├── templates/               # HTML files (Jinja2 templates)
│   ├── index.html
│   ├── signup.html
│   ├── login.html
│   ├── user_dashboard.html
│   ├── book_parking.html
│   ├── release_parking.html
│   ├── user_summary.html
│   ├── admin_dashboard.html
│   ├── view_parking_spots.html
│   └── admin_summary.html
│
├── static/
│   └── css/
│       └── style.css        # CSS file for styling
│
├── database/
│   └── parking.db           # SQLite database
│
├── app.py                   # Main Flask entry point
├── requirements.txt         # Python dependencies
├── README.txt               # Documentation (this file)
```
---

## How to Run Locally

### 1. Clone the repository
```
git clone https://github.com/your-username/parking-app.git
cd parking-app
```

### 2. Create a virtual environment
```
python -m venv venv
```

### 3. Activate the virtual environment
```
- On Windows:
venv\Scripts\activate
- On Mac/Linux:
source venv/bin/activate
```

### 4. Install dependencies
```
pip install -r requirements.txt
```

### 5. Initialize database
```
Make sure `parking.db` exists in the `database/` folder.  
If not, create it using the schema in `parking_model.py`.
```

### 6. Run the Flask server
```
python app.py
```

### 7. Open in browser
```
http://127.0.0.1:localhost
```

---

## Features
- **User Features**:
  - Signup/Login
  - Search parking lots
  - Book a parking spot
  - Release booked spots
  - View booking history
  - Change password and profile details
  - Usage summary via charts

- **Admin Features**:
  - Manage parking lots and spots
  - View registered users
  - View occupancy summary (Chart.js visualization)

---

## Technologies Used
- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, Jinja2, Chart.js
- **Database**: SQLite
- **Libraries**: bcrypt (for password hashing), flask-session

---

## Deployed Website
```
- https://parking-app-qyns.onrender.com
```
