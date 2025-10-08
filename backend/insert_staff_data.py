import requests
import json
import datetime

# --- CONFIGURATION ---
API_BASE_URL = 'http://127.0.0.1:5000/api'
HEADERS = {'Content-Type': 'application/json'}
DEFAULT_PASSWORD = "securepwd123"

# --- STAFF DATA FOR INSERTION ---
# These records will be created in your database.
STAFF_RECORDS = [
    {
        "firstName": "System",
        "lastName": "Admin",
        "email": "sysadmin@hotel.com",
        "phoneNumber": "1000000001",
        "username": "sysadmin",
        "password": DEFAULT_PASSWORD,
        "role": "Admin",
        "address": "99 HQ St",
        "dateOfHire": "2024-01-01",
        "salary": 95000.00
    },
    {
        "firstName": "Fiona",
        "lastName": "Reception",
        "email": "fiona@hotel.com",
        "phoneNumber": "1000000002",
        "username": "reception",
        "password": DEFAULT_PASSWORD,
        "role": "Receptionist",
        "address": "20 Front Desk Rd",
        "dateOfHire": "2024-03-15",
        "salary": 40000.00
    },
    {
        "firstName": "Robert",
        "lastName": "Manager",
        "email": "robert@hotel.com",
        "phoneNumber": "1000000003",
        "username": "manager",
        "password": DEFAULT_PASSWORD,
        "role": "Manager",
        "address": "50 Oversight Ave",
        "dateOfHire": "2023-08-20",
        "salary": 65000.00
    },
    {
        "firstName": "Holly",
        "lastName": "Housekeeper",
        "email": "holly@hotel.com",
        "phoneNumber": "1000000004",
        "username": "housekeeping",
        "password": DEFAULT_PASSWORD,
        "role": "Housekeeping",
        "address": "30 Clean Ln",
        "dateOfHire": "2024-05-10",
        "salary": 35000.00
    }
]


def insert_staff_records():
    """Sends POST requests to the API to insert defined staff records."""
    print(f"Attempting to insert {len(STAFF_RECORDS)} staff records...")

    for record in STAFF_RECORDS:
        try:
            response = requests.post(
                f"{API_BASE_URL}/staff", data=json.dumps(record), headers=HEADERS)
            data = response.json()

            if response.status_code == 201:
                print(
                    f"  SUCCESS: {record['role']} ({record['username']}) added with ID: {data.get('staffID')}")
            else:
                # Handle database errors (like Duplicate Entry)
                error_details = data.get('details', data.get('error'))
                print(f"  FAILED: {record['username']} -> {error_details}")

        except requests.exceptions.ConnectionError:
            print(
                "\n[CRITICAL ERROR] Could not connect to the Flask API. Please ensure app.py is running.")
            return


if __name__ == '__main__':
    insert_staff_records()
    print("\nStaff insertion script finished.")
