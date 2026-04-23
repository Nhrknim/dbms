# Hotel Management System

A DBMS project for hotel operations built with a Flask + MySQL backend and static frontend dashboards for login, administration, and reception workflows.

## Overview

This project covers the core day-to-day operations of a hotel management system:

- staff authentication
- guest registration
- reservations and check-in
- room inventory and room status tracking
- billing and payment handling
- service catalog management

## Project Structure

```text
proj2/
├── backend/
│   ├── app.py
│   ├── insert_staff_data.py
│   └── test_api_script.py
└── frontend/
    ├── index.html
    ├── admin.html
    └── receptionist.html
```

## Features

- Staff login with role-based redirection
- Guest CRUD operations
- Staff CRUD operations
- Reservation creation, update, checkout status handling
- Room type configuration and room inventory management
- Live room status view for reception
- Billing and payment record management
- Service catalog and bill-service support

## Tech Stack

- Backend: Python, Flask, PyMySQL, Flask-CORS
- Database: MySQL
- Frontend: HTML, Tailwind CSS, vanilla JavaScript

## Dashboards

- `frontend/index.html`: staff login page
- `frontend/admin.html`: admin/manager dashboard
- `frontend/receptionist.html`: receptionist dashboard

## Backend API Modules

The backend in `backend/app.py` exposes REST endpoints for:

- `/api/login`
- `/api/guests`
- `/api/staff`
- `/api/reservations`
- `/api/room-types`
- `/api/rooms`
- `/api/rooms-details`
- `/api/rooms/available`
- `/api/billing`
- `/api/payments`
- `/api/services`
- `/api/bill-services`

## Prerequisites

- Python 3.x
- MySQL Server
- A MySQL database named `hotel_db`

Install dependencies:

```bash
pip install -r requirements.txt
```

## Database Configuration

Database connection settings are currently defined directly in `backend/app.py`:

```python
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'hotel_manage',
    'password': 'dbms123',
    'database': 'hotel_db',
}
```

Update these values if your local MySQL setup is different.

## How To Run

1. Create the `hotel_db` database and required tables in MySQL.
2. Start the Flask backend:

```bash
cd backend
python app.py
```

3. Open `frontend/index.html` in a browser.
4. Log in and use the relevant dashboard based on role.

## Seed / Test Scripts

- `backend/insert_staff_data.py`: inserts sample staff accounts through the API
- `backend/test_api_script.py`: runs end-to-end API tests for major modules

Run them after the backend server is already running:

```bash
cd backend
python insert_staff_data.py
python test_api_script.py
```

## Sample Staff Accounts

The seed script creates accounts like:

- `sysadmin` / `securepwd123`
- `reception` / `securepwd123`
- `manager` / `securepwd123`
- `housekeeping` / `securepwd123`

## Notes

- The frontend is static and expects the backend at `http://127.0.0.1:5000`.
- The repository currently includes admin and receptionist dashboards.
- MySQL schema SQL is not included in this repository, so the tables must be created separately before running the app.
- Login redirects non-admin and non-receptionist roles to `general.html`, but that file is not currently present in this repository.

## Future Improvements

- Move DB credentials to environment variables
- Add a `requirements.txt`
- Add database schema and sample SQL
- Serve the frontend through Flask or a dedicated frontend setup
- Add screenshots and deployment instructions
