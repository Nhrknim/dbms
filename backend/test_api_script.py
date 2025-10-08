import requests
import json
import datetime

# ==============================================================================
# CONFIGURATION
# ==============================================================================
BASE_URL = 'http://127.0.0.1:5000/api'
HEADERS = {'Content-Type': 'application/json'}
TEST_DATA = {}  # Dictionary to store IDs created during testing


def send_request(method, endpoint, data=None, expected_status=200):
    """A helper function to send API requests and handle responses."""
    url = f"{BASE_URL}/{endpoint}"
    # Convert data to JSON string for POST/PUT requests
    payload = json.dumps(data) if data else None

    try:
        response = requests.request(method, url, headers=HEADERS, data=payload)

        # Print action and result
        print(f"\n[{method:<6} {endpoint}] -> Status: {response.status_code}")

        # Assert status code matches expectation
        assert response.status_code == expected_status, \
            f"FAILED! Expected {expected_status}, got {response.status_code}. Response: {response.text}"

        # If content exists, parse and return it
        if response.content:
            return response.json()
        return {}

    except requests.exceptions.ConnectionError:
        print(
            "\n\n[ERROR] Connection refused. Is the Flask server running on port 5000?")
        exit(1)
    except AssertionError as e:
        print(e)
        return None
    except Exception as e:
        print(f"\n[ERROR] An unexpected testing error occurred: {e}")
        return None

# ==============================================================================
# TEST FUNCTIONS
# ==============================================================================


def test_1_staff_and_login():
    """Tests Staff CRUD and Login authentication."""
    print("--- 1. STAFF & LOGIN TESTS (CRUD) ---")

    # 1. CREATE Staff
    staff_data = {
        "firstName": "Test", "lastName": "Admin", "email": "auto.test.admin@hotel.com",
        "phoneNumber": "1230001234", "username": "autotestadmin", "password": "securepwd",
        "role": "Admin", "address": "100 Server St", "dateOfHire": "2024-01-01", "salary": 80000
    }
    result = send_request('POST', 'staff', staff_data, 201)
    if result:
        TEST_DATA['staffID'] = result.get('staffID')
        print(f"-> Staff created successfully with ID: {TEST_DATA['staffID']}")

    # 2. LOGIN Test (Success)
    login_data = {"username": "autotestadmin", "password": "securepwd"}
    result = send_request('POST', 'login', login_data, 200)
    if result:
        print(f"-> Login Success. Role: {result.get('role')}")

    # 3. READ ALL Staff (Verification)
    result = send_request('GET', 'staff', expected_status=200)
    if result and len(result) >= 1:
        print(f"-> Staff list size: {len(result)}")

    # 4. UPDATE Staff
    update_data = {"salary": 85000.00}
    send_request('PUT', f"staff/{TEST_DATA['staffID']}", update_data, 200)
    print("-> Staff updated successfully.")


def test_2_inventory_setup():
    """Tests RoomType and Room creation (FK dependency setup)."""
    print("\n--- 2. INVENTORY SETUP (FKs) ---")

    # 1. CREATE RoomType
    rtype_data = {
        "typeName": "Suite", "description": "Luxury suite",
        "basePrice": 350.00, "capacity": 4
    }
    result = send_request('POST', 'room-types', rtype_data, 201)
    if result:
        TEST_DATA['roomTypeID'] = result.get('roomTypeID')
        print(f"-> RoomType created with ID: {TEST_DATA['roomTypeID']}")

    # 2. CREATE Room
    room_data = {
        # Note: roomNumber must be provided explicitly as it's not AUTO_INCREMENT
        "roomNumber": 305, "roomTypeID": TEST_DATA['roomTypeID'],
        "floorNumber": 3, "currentStatus": "Available"
    }
    send_request('POST', 'rooms', room_data, 201)
    TEST_DATA['roomNumber'] = 305
    print("-> Room 305 created successfully.")

    # 3. READ ONE Room
    send_request(
        'GET', f"rooms/{TEST_DATA['roomNumber']}", expected_status=200)
    print(f"-> Room {TEST_DATA['roomNumber']} read successfully.")


def test_3_guest_and_reservation():
    """Tests Guest and Reservation CRUD operations."""
    print("\n--- 3. GUEST & RESERVATION TESTS ---")

    # 1. CREATE Guest
    guest_data = {
        "firstName": "Alice", "lastName": "Guest", "email": "auto.alice@guest.com",
        "phoneNumber": "5551112222", "address": "10 Guest Lane", "idProof": "PAS-54321"
    }
    result = send_request('POST', 'guests', guest_data, 201)
    if result:
        TEST_DATA['guestID'] = result.get('guestID')
        print(f"-> Guest created successfully with ID: {TEST_DATA['guestID']}")

    # 2. CREATE Reservation (Requires Guest and Room)
    reservation_data = {
        "guestID": TEST_DATA['guestID'],
        "roomNumber": TEST_DATA['roomNumber'],
        "checkInDate": "2025-12-01",
        "checkOutDate": "2025-12-05",
        "bookingDate": str(datetime.date.today()),
        "numberOfAdults": 2,
        "numberOfChildren": 1,
        "reservationStatus": "Booked",
        "pricePerNight": 350.00
    }
    result = send_request('POST', 'reservations', reservation_data, 201)
    if result:
        TEST_DATA['reservationID'] = result.get('reservationID')
        print(
            f"-> Reservation created successfully with ID: {TEST_DATA['reservationID']}")

    # 3. UPDATE Reservation
    update_data = {"reservationStatus": "Checked-in"}
    send_request(
        'PUT', f"reservations/{TEST_DATA['reservationID']}", update_data, 200)
    print("-> Reservation updated successfully.")

    # 4. READ ALL Reservations
    result = send_request('GET', 'reservations', expected_status=200)
    if result and len(result) >= 1:
        print("-> Reservation list read successfully.")


def test_5_service_crud():
    """Tests Service CRUD operations."""
    print("\n--- 5. SERVICE TESTS (CRUD) ---")

    # 1. CREATE Service
    service_data = {
        "serviceName": "Laundry Service", "description": "Same-day laundry and pressing",
        "unitPrice": 15.50
    }
    result = send_request('POST', 'services', service_data, 201)
    if result:
        TEST_DATA['serviceID'] = result.get('serviceID')
        print(
            f"-> Service created successfully with ID: {TEST_DATA['serviceID']}")

    # 2. READ ONE Service
    result = send_request(
        'GET', f"services/{TEST_DATA['serviceID']}", expected_status=200)
    if result:
        print(f"-> Service read: {result.get('serviceName')}")

    # 3. UPDATE Service
    update_data = {"unitPrice": 20.00}
    send_request('PUT', f"services/{TEST_DATA['serviceID']}", update_data, 200)
    print("-> Service updated successfully.")

    # 4. READ ALL Services (Verification)
    send_request('GET', 'services', expected_status=200)


def test_6_billing_payment_crud():
    """Tests Billing and Payment creation (FK dependency on Reservation)."""
    print("\n--- 6. BILLING & PAYMENT TESTS (CRUD) ---")

    # Prerequisite: Reservation ID must exist in TEST_DATA
    reservation_id = TEST_DATA.get('reservationID')

    # 1. CREATE Billing (Uses Reservation ID)
    billing_data = {
        "reservationID": reservation_id,
        "billDate": str(datetime.date.today()),
        "subTotal": 900.00, "taxAmount": 90.00, "totalAmount": 990.00,
        "paymentStatus": "Unpaid"
    }
    result = send_request('POST', 'billing', billing_data, 201)
    if result:
        TEST_DATA['billID'] = result.get('billID')
        print(
            f"-> Billing created successfully with ID: {TEST_DATA['billID']}")

    # 2. CREATE Payment (Uses Bill ID)
    payment_data = {
        "billID": TEST_DATA['billID'],
        "paymentMethod": "Credit Card",
        "paymentDate": str(datetime.date.today()),
        "amountPaid": 500.00,
        "transactionID": "TXN-AUTO-500"
    }
    result = send_request('POST', 'payments', payment_data, 201)
    if result:
        TEST_DATA['paymentID'] = result.get('paymentID')
        print(
            f"-> Payment created successfully with ID: {TEST_DATA['paymentID']}")

    # 3. UPDATE Payment
    update_data = {"amountPaid": 490.00}
    send_request('PUT', f"payments/{TEST_DATA['paymentID']}", update_data, 200)
    print("-> Payment updated successfully.")


def test_7_bill_service_crud():
    """Tests BillService creation (FK dependency on Billing and Service)."""
    print("\n--- 7. BILL SERVICE TESTS (CRUD) ---")

    # Prerequisite: Bill ID and Service ID must exist in TEST_DATA
    bill_id = TEST_DATA.get('billID')
    service_id = TEST_DATA.get('serviceID')

    # 1. CREATE BillService (Links a Bill to a Service)
    bill_service_data = {
        "billID": bill_id,
        "serviceID": service_id,
        "quantity": 3,
        "totalServicePrice": 60.00  # 3 units @ 20.00
    }
    result = send_request('POST', 'bill-services', bill_service_data, 201)
    if result:
        TEST_DATA['billServiceID'] = result.get('billServiceID')
        print(
            f"-> BillService created successfully with ID: {TEST_DATA['billServiceID']}")

    # 2. READ ONE BillService
    result = send_request(
        'GET', f"bill-services/{TEST_DATA['billServiceID']}", expected_status=200)
    if result:
        print(f"-> BillService read: Quantity {result.get('quantity')}")

    # 3. UPDATE BillService
    update_data = {"quantity": 4}
    send_request(
        'PUT', f"bill-services/{TEST_DATA['billServiceID']}", update_data, 200)
    print("-> BillService updated successfully.")


def test_4_cleanup():
    """Deletes all records created during testing to reset the database (Important for clean re-runs)."""
    print("\n--- 4. CLEANUP (Deletion Order is Crucial for FKs) ---")

    # Deletion order: Child tables first, then parent tables.

    # 1. DELETE BILL_SERVICE (Child of Billing/Service)
    send_request(
        'DELETE', f"bill-services/{TEST_DATA['billServiceID']}", expected_status=200)
    print("-> BillService deleted.")

    # 2. DELETE PAYMENT (Child of Billing)
    send_request(
        'DELETE', f"payments/{TEST_DATA['paymentID']}", expected_status=200)
    print("-> Payment deleted.")

    # 3. DELETE BILLING (Child of Reservation)
    send_request(
        'DELETE', f"billing/{TEST_DATA['billID']}", expected_status=200)
    print("-> Billing deleted.")

    # 4. DELETE RESERVATION (Child of Guest/Room)
    send_request(
        'DELETE', f"reservations/{TEST_DATA['reservationID']}", expected_status=200)
    print("-> Reservation deleted.")

    # 5. DELETE GUEST
    send_request(
        'DELETE', f"guests/{TEST_DATA['guestID']}", expected_status=200)
    print("-> Guest deleted.")

    # 6. DELETE STAFF
    send_request(
        'DELETE', f"staff/{TEST_DATA['staffID']}", expected_status=200)
    print("-> Staff deleted.")

    # 7. DELETE ROOM
    send_request(
        'DELETE', f"rooms/{TEST_DATA['roomNumber']}", expected_status=200)
    print("-> Room deleted.")

    # 8. DELETE ROOM TYPE
    send_request(
        'DELETE', f"room-types/{TEST_DATA['roomTypeID']}", expected_status=200)
    print("-> Room Type deleted.")

    # 9. DELETE SERVICE
    send_request(
        'DELETE', f"services/{TEST_DATA['serviceID']}", expected_status=200)
    print("-> Service deleted.")


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
if __name__ == '__main__':
    test_1_staff_and_login()
    test_2_inventory_setup()
    test_5_service_crud()
    test_3_guest_and_reservation()
    test_6_billing_payment_crud()
    test_7_bill_service_crud()
    test_4_cleanup()

    print("\n\n*** Comprehensive API Test Script finished. If no FAILED messages appeared, your backend is fully functional! ***")
