import pymysql.cursors

from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
import json
from flask_cors import CORS

# ==============================================================================
# 1. DATABASE CONFIGURATION
# ==============================================================================
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'hotel_manage',
    'password': 'dbms123',
    'database': 'hotel_db',
    'cursorclass': pymysql.cursors.DictCursor
}

# ==============================================================================
# 2. FLASK APPLICATION SETUP
# ==============================================================================
app = Flask(__name__)
CORS(app)

# ==============================================================================
# 3. DATABASE CONNECTION FUNCTION
# ==============================================================================


def get_db_connection():
    """Establishes a connection to the MySQL database."""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

# ==============================================================================
# 4. API ENDPOINT FOR LOGIN
# ==============================================================================


@app.route('/api/login', methods=['POST'])
def login():
    """Authenticates a staff member and returns their role."""
    connection = None
    try:
        login_data = request.get_json()
        if not login_data:
            return jsonify({'error': 'Invalid JSON data provided.'}), 400

        username = login_data.get('username')
        password = login_data.get('password')

        if not all([username, password]):
            return jsonify({'error': 'Missing required fields: username, password'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql = "SELECT staffID, username, passwordHash, role FROM Staff WHERE username = %s"
            cursor.execute(sql, (username,))
            staff_member = cursor.fetchone()

            if not staff_member:
                return jsonify({'error': 'Invalid username or password'}), 401

            if check_password_hash(staff_member['passwordHash'], password):
                return jsonify({
                    'message': 'Login successful!',
                    'staffID': staff_member['staffID'],
                    'username': staff_member['username'],
                    'role': staff_member['role']
                }), 200
            else:
                return jsonify({'error': 'Invalid username or password'}), 401

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()

# ==============================================================================
# 5. API ENDPOINTS TO MANAGE GUEST DATA
# ==============================================================================


# ==============================================================================
# 5. API ENDPOINTS TO MANAGE GUEST DATA
# ==============================================================================


@app.route('/api/guests', methods=['POST'])
def add_guest():
    """Adds a new guest to the 'Guest' table."""
    connection = None
    try:
        guest_data = request.get_json()
        if not guest_data:
            return jsonify({'error': 'Invalid JSON data provided.'}), 400

        first_name = guest_data.get('firstName')
        last_name = guest_data.get('lastName')
        email = guest_data.get('email')
        # --- FIX APPLIED HERE ---
        # Convert empty strings from form fields to None, allowing NULL database columns to work.
        phone_number = guest_data.get('phoneNumber')
        if phone_number == "":
            phone_number = None

        address = guest_data.get('address')
        if address == "":
            address = None
        # ------------------------

        id_proof = guest_data.get('idProof')

        if not all([first_name, last_name, email, id_proof]):
            return jsonify({'error': 'Missing required fields: firstName, lastName, email, idProof'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql = """
            INSERT INTO GUEST (firstName, lastName, email, phoneNumber, address, idProof)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (first_name, last_name, email,
                                 # 'address' and 'phoneNumber' are now correctly None or a value
                                 phone_number, address, id_proof))
            connection.commit()

            new_guest_id = cursor.lastrowid

        return jsonify({
            'message': 'Guest added successfully!',
            'guestID': new_guest_id,
            'data': guest_data
        }), 201

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/guests', methods=['GET'])
def get_all_guests():
    """Retrieves and returns all guest records from the 'Guest' table."""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql = "SELECT * FROM GUEST"
            cursor.execute(sql)
            guests = cursor.fetchall()

        return jsonify(guests), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/guests/<int:guest_id>', methods=['GET'])
def get_guest(guest_id):
    """Retrieves a single guest record by guestID."""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql = "SELECT * FROM GUEST WHERE guestID = %s"
            cursor.execute(sql, (guest_id,))
            guest = cursor.fetchone()

        if guest:
            return jsonify(guest), 200
        else:
            return jsonify({'error': 'Guest not found'}), 404

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/guests/<int:guest_id>', methods=['PUT'])
def update_guest(guest_id):
    """Updates an existing guest record by guestID."""
    connection = None
    try:
        guest_data = request.get_json()
        if not guest_data:
            return jsonify({'error': 'Invalid JSON data provided.'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql_check = "SELECT guestID FROM GUEST WHERE guestID = %s"
            cursor.execute(sql_check, (guest_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Guest not found'}), 404

            fields = []
            values = []
            for key, value in guest_data.items():
                fields.append(f"{key} = %s")
                values.append(value)

            if not fields:
                return jsonify({'message': 'No fields to update.'}), 200

            values.append(guest_id)
            sql_update = f"UPDATE GUEST SET {', '.join(fields)} WHERE guestID = %s"

            cursor.execute(sql_update, tuple(values))
            connection.commit()

        return jsonify({'message': 'Guest updated successfully!'}), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/guests/<int:guest_id>', methods=['DELETE'])
def delete_guest(guest_id):
    """Deletes a guest record by guestID."""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql_check = "SELECT guestID FROM GUEST WHERE guestID = %s"
            cursor.execute(sql_check, (guest_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Guest not found'}), 404

            sql_delete = "DELETE FROM GUEST WHERE guestID = %s"
            cursor.execute(sql_delete, (guest_id,))
            connection.commit()

        return jsonify({'message': 'Guest deleted successfully!'}), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()

# ==============================================================================
# 7. API ENDPOINTS TO MANAGE STAFF DATA
# ==============================================================================


@app.route('/api/staff', methods=['POST'])
def add_staff():
    """Adds a new staff member to the 'Staff' table with a hashed password."""
    connection = None
    try:
        staff_data = request.get_json()
        if not staff_data:
            return jsonify({'error': 'Invalid JSON data provided.'}), 400

        first_name = staff_data.get('firstName')
        last_name = staff_data.get('lastName')
        email = staff_data.get('email')
        phone_number = staff_data.get('phoneNumber')
        username = staff_data.get('username')
        password = staff_data.get('password')
        role = staff_data.get('role')
        address = staff_data.get('address')
        date_of_hire = staff_data.get('dateOfHire')
        salary = staff_data.get('salary')

        if not all([first_name, last_name, email, username, password, role]):
            return jsonify({'error': 'Missing required fields: firstName, lastName, email, username, password, role'}), 400

        password_hash = generate_password_hash(password)

        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql = """
            INSERT INTO STAFF (
                firstName, lastName, email, phoneNumber, username, passwordHash, role,
                address, dateOfHire, salary
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                first_name, last_name, email, phone_number, username, password_hash, role,
                address, date_of_hire, salary
            ))
            connection.commit()
            new_staff_id = cursor.lastrowid

        return jsonify({
            'message': 'Staff member added successfully!',
            'staffID': new_staff_id
        }), 201

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/staff', methods=['GET'])
def get_all_staff():
    """Retrieves all staff records."""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql = "SELECT * FROM STAFF"
            cursor.execute(sql)
            staff = cursor.fetchall()

        return jsonify(staff), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/staff/<int:staff_id>', methods=['GET'])
def get_staff(staff_id):
    """Retrieves a single staff record by staffID."""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql = "SELECT * FROM STAFF WHERE staffID = %s"
            cursor.execute(sql, (staff_id,))
            staff = cursor.fetchone()

        if staff:
            return jsonify(staff), 200
        else:
            return jsonify({'error': 'Staff member not found'}), 404

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/staff/<int:staff_id>', methods=['PUT'])
def update_staff(staff_id):
    """Updates an existing staff record by staffID."""
    connection = None
    try:
        staff_data = request.get_json()
        if not staff_data:
            return jsonify({'error': 'Invalid JSON data provided.'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql_check = "SELECT staffID FROM STAFF WHERE staffID = %s"
            cursor.execute(sql_check, (staff_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Staff member not found'}), 404

            fields = []
            values = []
            for key, value in staff_data.items():
                if key == 'password':
                    password_hash = generate_password_hash(value)
                    fields.append("passwordHash = %s")
                    values.append(password_hash)
                else:
                    fields.append(f"{key} = %s")
                    values.append(value)

            if not fields:
                return jsonify({'message': 'No fields to update.'}), 200

            values.append(staff_id)
            sql_update = f"UPDATE STAFF SET {', '.join(fields)} WHERE staffID = %s"

            cursor.execute(sql_update, tuple(values))
            connection.commit()

        return jsonify({'message': 'Staff member updated successfully!'}), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/staff/<int:staff_id>', methods=['DELETE'])
def delete_staff(staff_id):
    """Deletes a staff record by staffID."""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql_check = "SELECT staffID FROM STAFF WHERE staffID = %s"
            cursor.execute(sql_check, (staff_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Staff member not found'}), 404

            sql_delete = "DELETE FROM STAFF WHERE staffID = %s"
            cursor.execute(sql_delete, (staff_id,))
            connection.commit()

        return jsonify({'message': 'Staff member deleted successfully!'}), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()

# ==============================================================================
# 8. API ENDPOINTS FOR RESERVATION MANAGEMENT
# ==============================================================================


@app.route('/api/reservations', methods=['POST'])
def add_reservation():
    """Adds a new reservation to the 'Reservation' table."""
    connection = None
    try:
        reservation_data = request.get_json()
        if not reservation_data:
            return jsonify({'error': 'Invalid JSON data provided.'}), 400

        guest_id = reservation_data.get('guestID')
        room_number = reservation_data.get('roomNumber')
        check_in_date = reservation_data.get('checkInDate')
        check_out_date = reservation_data.get('checkOutDate')
        booking_date = reservation_data.get('bookingDate')
        num_adults = reservation_data.get('numberOfAdults')
        num_children = reservation_data.get('numberOfChildren')
        status = reservation_data.get('reservationStatus')
        price_per_night = reservation_data.get('pricePerNight')

        if not all([guest_id, room_number, check_in_date, check_out_date]):
            return jsonify({'error': 'Missing required fields'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql = """
            INSERT INTO RESERVATION (
                guestID, roomNumber, checkInDate, checkOutDate, bookingDate,
                numberOfAdults, numberOfChildren, reservationStatus, pricePerNight
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                guest_id, room_number, check_in_date, check_out_date, booking_date,
                num_adults, num_children, status, price_per_night
            ))
            connection.commit()
            new_reservation_id = cursor.lastrowid

        return jsonify({
            'message': 'Reservation added successfully!',
            'reservationID': new_reservation_id,
            'data': reservation_data
        }), 201

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/reservations', methods=['GET'])
def get_all_reservations():
    """Retrieves all reservation records."""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql = "SELECT * FROM RESERVATION"
            cursor.execute(sql)
            reservations = cursor.fetchall()

        return jsonify(reservations), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/reservations/<int:reservation_id>', methods=['GET'])
def get_reservation(reservation_id):
    """Retrieves a single reservation record by reservationID."""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql = "SELECT * FROM RESERVATION WHERE reservationID = %s"
            cursor.execute(sql, (reservation_id,))
            reservation = cursor.fetchone()

        if reservation:
            return jsonify(reservation), 200
        else:
            return jsonify({'error': 'Reservation not found'}), 404

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/reservations/<int:reservation_id>', methods=['PUT'])
def update_reservation(reservation_id):
    """Updates an existing reservation record by reservationID."""
    connection = None
    try:
        reservation_data = request.get_json()
        if not reservation_data:
            return jsonify({'error': 'Invalid JSON data provided.'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql_check = "SELECT reservationID FROM RESERVATION WHERE reservationID = %s"
            cursor.execute(sql_check, (reservation_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Reservation not found'}), 404

            fields = []
            values = []
            for key, value in reservation_data.items():
                fields.append(f"{key} = %s")
                values.append(value)

            if not fields:
                return jsonify({'message': 'No fields to update.'}), 200

            values.append(reservation_id)
            sql_update = f"UPDATE RESERVATION SET {', '.join(fields)} WHERE reservationID = %s"

            cursor.execute(sql_update, tuple(values))
            connection.commit()

        return jsonify({'message': 'Reservation updated successfully!'}), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/reservations/<int:reservation_id>', methods=['DELETE'])
def delete_reservation(reservation_id):
    """Deletes a reservation record by reservationID."""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql_check = "SELECT reservationID FROM RESERVATION WHERE reservationID = %s"
            cursor.execute(sql_check, (reservation_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Reservation not found'}), 404

            sql_delete = "DELETE FROM RESERVATION WHERE reservationID = %s"
            cursor.execute(sql_delete, (reservation_id,))
            connection.commit()

        return jsonify({'message': 'Reservation deleted successfully!'}), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()
            connection.close()


@app.route('/api/reservations/<int:reservation_id>/status', methods=['PUT'])
def update_reservation_status(reservation_id):
    """Updates the status of an existing reservation record."""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        # Read status from the request body sent by the frontend
        request_data = request.get_json()
        # Default to Checked-out if missing
        new_status = request_data.get('new_status', 'Checked-out')

        print(
            f"--- DEBUG: Attempting status update for ID {reservation_id} to '{new_status}' ---")

        with connection.cursor() as cursor:
            # Check query capitalization
            sql_check = "SELECT reservationID FROM RESERVATION WHERE reservationID = %s"
            cursor.execute(sql_check, (reservation_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Reservation not found'}), 404

            # Check update query capitalization
            sql_update = "UPDATE RESERVATION SET reservationStatus = %s WHERE reservationID = %s"

            # DEBUG: Print the exact values being executed
            print(
                f"Executing SQL: UPDATE RESERVATION SET reservationStatus = '{new_status}' WHERE reservationID = {reservation_id}")

            cursor.execute(sql_update, (new_status, reservation_id))
            connection.commit()

            # Check if any rows were affected (optional but helpful for confirmation)
            if cursor.rowcount == 0:
                print(
                    f"Warning: No rows updated for reservation ID {reservation_id}. Status might already be {new_status}.")

        return jsonify({'message': f'Reservation {reservation_id} status updated to {new_status}!'}), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()
# ==============================================================================
# 11. API ENDPOINTS FOR ROOM TYPE MANAGEMENT
# ==============================================================================


@app.route('/api/room-types', methods=['POST'])
def add_room_type():
    """Adds a new room type to the 'RoomType' table."""
    connection = None
    try:
        room_type_data = request.get_json()
        if not room_type_data:
            return jsonify({'error': 'Invalid JSON data provided.'}), 400

        type_name = room_type_data.get('typeName')
        description = room_type_data.get('description')
        base_price = room_type_data.get('basePrice')
        capacity = room_type_data.get('capacity')

        if not all([type_name, description, base_price, capacity]):
            return jsonify({'error': 'Missing required fields'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql = """
            INSERT INTO ROOM_TYPE (typeName, description, basePrice, capacity)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (type_name, description, base_price, capacity))
            connection.commit()
            new_room_type_id = cursor.lastrowid

        return jsonify({
            'message': 'Room type added successfully!',
            'roomTypeID': new_room_type_id,
            'data': room_type_data
        }), 201

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/room-types', methods=['GET'])
def get_all_room_types():
    """Retrieves all room type records."""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql = "SELECT * FROM ROOM_TYPE"
            cursor.execute(sql)
            room_types = cursor.fetchall()

        return jsonify(room_types), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/room-types/<int:room_type_id>', methods=['GET'])
def get_room_type(room_type_id):
    """Retrieves a single room type record by roomTypeID."""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql = "SELECT * FROM ROOM_TYPE WHERE roomTypeID = %s"
            cursor.execute(sql, (room_type_id,))
            room_type = cursor.fetchone()

        if room_type:
            return jsonify(room_type), 200
        else:
            return jsonify({'error': 'Room type not found'}), 404

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/room-types/<int:room_type_id>', methods=['PUT'])
def update_room_type(room_type_id):
    """Updates an existing room type record by roomTypeID."""
    connection = None
    try:
        room_type_data = request.get_json()
        if not room_type_data:
            return jsonify({'error': 'Invalid JSON data provided.'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql_check = "SELECT roomTypeID FROM ROOM_TYPE WHERE roomTypeID = %s"
            cursor.execute(sql_check, (room_type_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Room type not found'}), 404

            fields = []
            values = []
            for key, value in room_type_data.items():
                fields.append(f"{key} = %s")
                values.append(value)

            if not fields:
                return jsonify({'message': 'No fields to update.'}), 200

            values.append(room_type_id)
            sql_update = f"UPDATE ROOM_TYPE SET {', '.join(fields)} WHERE roomTypeID = %s"

            cursor.execute(sql_update, tuple(values))
            connection.commit()

        return jsonify({'message': 'Room type updated successfully!'}), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/room-types/<int:room_type_id>', methods=['DELETE'])
def delete_room_type(room_type_id):
    """Deletes a room type record by roomTypeID."""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql_check = "SELECT roomTypeID FROM ROOM_TYPE WHERE roomTypeID = %s"
            cursor.execute(sql_check, (room_type_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Room type not found'}), 404

            sql_delete = "DELETE FROM ROOM_TYPE WHERE roomTypeID = %s"
            cursor.execute(sql_delete, (room_type_id,))
            connection.commit()

        return jsonify({'message': 'Room type deleted successfully!'}), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()

# ==============================================================================
# 13. API ENDPOINTS FOR ROOM MANAGEMENT
# ==============================================================================


@app.route('/api/rooms', methods=['POST'])
def add_room():
    """Adds a new room to the 'Room' table."""
    connection = None
    try:
        room_data = request.get_json()
        if not room_data:
            return jsonify({'error': 'Invalid JSON data provided.'}), 400

        room_number = room_data.get('roomNumber')
        room_type_id = room_data.get('roomTypeID')
        floor_number = room_data.get('floorNumber')
        current_status = room_data.get('currentStatus')

        if not all([room_number, room_type_id, floor_number, current_status]):
            return jsonify({'error': 'Missing required fields'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql = """
            INSERT INTO ROOM (roomNumber, roomTypeID, floorNumber, currentStatus)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (room_number, room_type_id,
                                 floor_number, current_status))
            connection.commit()

        return jsonify({
            'message': 'Room added successfully!',
            'roomNumber': room_number,
            'data': room_data
        }), 201

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/rooms', methods=['GET'])
def get_all_rooms():
    """Retrieves all room records."""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql = "SELECT * FROM ROOM"
            cursor.execute(sql)
            rooms = cursor.fetchall()

        return jsonify(rooms), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/rooms/<room_number>', methods=['GET'])
def get_room(room_number):
    """Retrieves a single room record by roomNumber."""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql = "SELECT * FROM ROOM WHERE roomNumber = %s"
            cursor.execute(sql, (room_number,))
            room = cursor.fetchone()

        if room:
            return jsonify(room), 200
        else:
            return jsonify({'error': 'Room not found'}), 404

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/rooms-details', methods=['GET'])
def get_all_rooms_with_details():
    """
    Retrieves all room records joined with RoomType to provide the name 
    and base price for the dashboard and booking forms.
    """
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            # New query to join ROOM and ROOM_TYPE
            sql = """
            SELECT
                R.roomNumber, R.roomTypeID, R.floorNumber, R.currentStatus,
                RT.typeName AS roomType, RT.basePrice
            FROM ROOM R
            JOIN ROOM_TYPE RT ON R.roomTypeID = RT.roomTypeID
            """
            cursor.execute(sql)
            rooms = cursor.fetchall()

        return jsonify(rooms), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/rooms/<room_number>', methods=['PUT'])
def update_room(room_number):
    """Updates an existing room record by roomNumber."""
    connection = None
    try:
        room_data = request.get_json()
        if not room_data:
            return jsonify({'error': 'Invalid JSON data provided.'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql_check = "SELECT roomNumber FROM ROOM WHERE roomNumber = %s"
            cursor.execute(sql_check, (room_number,))
            if not cursor.fetchone():
                return jsonify({'error': 'Room not found'}), 404

            fields = []
            values = []
            for key, value in room_data.items():
                fields.append(f"{key} = %s")
                values.append(value)

            if not fields:
                return jsonify({'message': 'No fields to update.'}), 200

            values.append(room_number)
            sql_update = f"UPDATE ROOM SET {', '.join(fields)} WHERE roomNumber = %s"

            cursor.execute(sql_update, tuple(values))
            connection.commit()

        return jsonify({'message': 'Room updated successfully!'}), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/rooms/<room_number>', methods=['DELETE'])
def delete_room(room_number):
    """Deletes a room record by roomNumber."""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql_check = "SELECT roomNumber FROM ROOM WHERE roomNumber = %s"
            cursor.execute(sql_check, (room_number,))
            if not cursor.fetchone():
                return jsonify({'error': 'Room not found'}), 404

            sql_delete = "DELETE FROM ROOM WHERE roomNumber = %s"
            cursor.execute(sql_delete, (room_number,))
            connection.commit()

        return jsonify({'message': 'Room deleted successfully!'}), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/rooms/available', methods=['GET'])
def get_available_rooms_by_type():
    """
    Retrieves available room numbers based on a provided roomTypeID.
    This endpoint joins the ROOM and ROOM_TYPE tables.
    Expected URL: /api/rooms/available?roomTypeId=<id>
    """
    # Use request.args.get() to safely read URL parameters
    room_type_id = request.args.get('roomTypeId')
    if not room_type_id:
        return jsonify({'error': 'Missing roomTypeId parameter.'}), 400

    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        # Use DictCursor for a clean JSON output (key-value pairs)
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
            SELECT
                R.roomNumber
            FROM
                ROOM R
            JOIN
                ROOM_TYPE RT ON R.roomTypeID = RT.roomTypeID
            WHERE
                R.roomTypeID = %s AND R.currentStatus = 'Available'
            """
            cursor.execute(sql, (room_type_id,))
            available_rooms = cursor.fetchall()

        return jsonify(available_rooms), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error in available rooms query: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()

# ==============================================================================
# 14. API ENDPOINTS FOR BILLING MANAGEMENT
# ==============================================================================


@app.route('/api/billing', methods=['POST'])
def add_billing():
    """Adds a new bill to the 'Billing' table."""
    connection = None
    try:
        billing_data = request.get_json()
        if not billing_data:
            return jsonify({'error': 'Invalid JSON data provided.'}), 400

        reservation_id = billing_data.get('reservationID')
        bill_date = billing_data.get('billDate')
        sub_total = billing_data.get('subTotal')
        tax_amount = billing_data.get('taxAmount')
        total_amount = billing_data.get('totalAmount')
        payment_status = billing_data.get('paymentStatus')

        if not all([reservation_id, bill_date, total_amount]):
            return jsonify({'error': 'Missing required fields'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql = """
            INSERT INTO BILLING (reservationID, billDate, subTotal, taxAmount, totalAmount, paymentStatus)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (reservation_id, bill_date,
                                 sub_total, tax_amount, total_amount, payment_status))
            connection.commit()
            new_bill_id = cursor.lastrowid

        return jsonify({
            'message': 'Bill added successfully!',
            'billID': new_bill_id,
            'data': billing_data
        }), 201

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/billing', methods=['GET'])
def get_all_billing():
    """Retrieves all billing records."""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql = "SELECT * FROM BILLING"
            cursor.execute(sql)
            billing_records = cursor.fetchall()

        return jsonify(billing_records), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/billing/<int:bill_id>', methods=['GET'])
def get_billing(bill_id):
    """Retrieves a single billing record by billID."""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql = "SELECT * FROM BILLING WHERE billID = %s"
            cursor.execute(sql, (bill_id,))
            billing_record = cursor.fetchone()

        if billing_record:
            return jsonify(billing_record), 200
        else:
            return jsonify({'error': 'Bill not found'}), 404

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/billing/<int:bill_id>', methods=['PUT'])
def update_billing(bill_id):
    """Updates an existing billing record by billID."""
    connection = None
    try:
        billing_data = request.get_json()
        if not billing_data:
            return jsonify({'error': 'Invalid JSON data provided.'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql_check = "SELECT billID FROM BILLING WHERE billID = %s"
            cursor.execute(sql_check, (bill_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Bill not found'}), 404

            fields = []
            values = []
            for key, value in billing_data.items():
                fields.append(f"{key} = %s")
                values.append(value)

            if not fields:
                return jsonify({'message': 'No fields to update.'}), 200

            values.append(bill_id)
            sql_update = f"UPDATE BILLING SET {', '.join(fields)} WHERE billID = %s"

            cursor.execute(sql_update, tuple(values))
            connection.commit()

        return jsonify({'message': 'Bill updated successfully!'}), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/billing/<int:bill_id>', methods=['DELETE'])
def delete_billing(bill_id):
    """Deletes a billing record by billID."""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql_check = "SELECT billID FROM BILLING WHERE billID = %s"
            cursor.execute(sql_check, (bill_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Bill not found'}), 404

            sql_delete = "DELETE FROM BILLING WHERE billID = %s"
            cursor.execute(sql_delete, (bill_id,))
            connection.commit()

        return jsonify({'message': 'Bill deleted successfully!'}), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()

# ==============================================================================
# 15. API ENDPOINTS FOR PAYMENT MANAGEMENT
# ==============================================================================


@app.route('/api/payments', methods=['POST'])
def add_payment():
    """Adds a new payment to the 'Payment' table."""
    connection = None
    try:
        payment_data = request.get_json()
        if not payment_data:
            return jsonify({'error': 'Invalid JSON data provided.'}), 400

        bill_id = payment_data.get('billID')
        payment_method = payment_data.get('paymentMethod')
        payment_date = payment_data.get('paymentDate')
        amount_paid = payment_data.get('amountPaid')
        transaction_id = payment_data.get('transactionID')

        if not all([bill_id, payment_method, payment_date, amount_paid]):
            return jsonify({'error': 'Missing required fields'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql = """
            INSERT INTO PAYMENT (billID, paymentMethod, paymentDate, amountPaid, transactionID)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (bill_id, payment_method,
                                 payment_date, amount_paid, transaction_id))
            connection.commit()
            new_payment_id = cursor.lastrowid

        return jsonify({
            'message': 'Payment added successfully!',
            'paymentID': new_payment_id,
            'data': payment_data
        }), 201

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/payments', methods=['GET'])
def get_all_payments():
    """Retrieves all payment records."""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql = "SELECT * FROM PAYMENT"
            cursor.execute(sql)
            payments = cursor.fetchall()

        return jsonify(payments), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/payments/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    """Retrieves a single payment record by paymentID."""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql = "SELECT * FROM PAYMENT WHERE paymentID = %s"
            cursor.execute(sql, (payment_id,))
            payment = cursor.fetchone()

        if payment:
            return jsonify(payment), 200
        else:
            return jsonify({'error': 'Payment not found'}), 404

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/payments/<int:payment_id>', methods=['PUT'])
def update_payment(payment_id):
    """Updates an existing payment record by paymentID."""
    connection = None
    try:
        payment_data = request.get_json()
        if not payment_data:
            return jsonify({'error': 'Invalid JSON data provided.'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql_check = "SELECT paymentID FROM PAYMENT WHERE paymentID = %s"
            cursor.execute(sql_check, (payment_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Payment not found'}), 404

            fields = []
            values = []
            for key, value in payment_data.items():
                fields.append(f"{key} = %s")
                values.append(value)

            if not fields:
                return jsonify({'message': 'No fields to update.'}), 200

            values.append(payment_id)
            sql_update = f"UPDATE PAYMENT SET {', '.join(fields)} WHERE paymentID = %s"

            cursor.execute(sql_update, tuple(values))
            connection.commit()

        return jsonify({'message': 'Payment updated successfully!'}), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/payments/<int:payment_id>', methods=['DELETE'])
def delete_payment(payment_id):
    """Deletes a payment record by paymentID."""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql_check = "SELECT paymentID FROM PAYMENT WHERE paymentID = %s"
            cursor.execute(sql_check, (payment_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Payment not found'}), 404

            sql_delete = "DELETE FROM PAYMENT WHERE paymentID = %s"
            cursor.execute(sql_delete, (payment_id,))
            connection.commit()

        return jsonify({'message': 'Payment deleted successfully!'}), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()

# ==============================================================================
# 16. API ENDPOINTS FOR SERVICE MANAGEMENT
# ==============================================================================


@app.route('/api/services', methods=['POST'])
def add_service():
    """Adds a new service to the 'Service' table."""
    connection = None
    try:
        service_data = request.get_json()
        if not service_data:
            return jsonify({'error': 'Invalid JSON data provided.'}), 400

        service_name = service_data.get('serviceName')
        description = service_data.get('description')
        unit_price = service_data.get('unitPrice')

        if not all([service_name, unit_price]):
            return jsonify({'error': 'Missing required fields'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql = """
            INSERT INTO SERVICE (serviceName, description, unitPrice)
            VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (service_name, description, unit_price))
            connection.commit()
            new_service_id = cursor.lastrowid

        return jsonify({
            'message': 'Service added successfully!',
            'serviceID': new_service_id,
            'data': service_data
        }), 201

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/services', methods=['GET'])
def get_all_services():
    """Retrieves all service records."""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql = "SELECT * FROM SERVICE"
            cursor.execute(sql)
            services = cursor.fetchall()

        return jsonify(services), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/services/<int:service_id>', methods=['GET'])
def get_service(service_id):
    """Retrieves a single service record by serviceID."""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql = "SELECT * FROM SERVICE WHERE serviceID = %s"
            cursor.execute(sql, (service_id,))
            service = cursor.fetchone()

        if service:
            return jsonify(service), 200
        else:
            return jsonify({'error': 'Service not found'}), 404

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/services/<int:service_id>', methods=['PUT'])
def update_service(service_id):
    """Updates an existing service record by serviceID."""
    connection = None
    try:
        service_data = request.get_json()
        if not service_data:
            return jsonify({'error': 'Invalid JSON data provided.'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql_check = "SELECT serviceID FROM SERVICE WHERE serviceID = %s"
            cursor.execute(sql_check, (service_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Service not found'}), 404

            fields = []
            values = []
            for key, value in service_data.items():
                fields.append(f"{key} = %s")
                values.append(value)

            if not fields:
                return jsonify({'message': 'No fields to update.'}), 200

            values.append(service_id)
            sql_update = f"UPDATE SERVICE SET {', '.join(fields)} WHERE serviceID = %s"

            cursor.execute(sql_update, tuple(values))
            connection.commit()

        return jsonify({'message': 'Service updated successfully!'}), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/services/<int:service_id>', methods=['DELETE'])
def delete_service(service_id):
    """Deletes a service record by serviceID."""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql_check = "SELECT serviceID FROM SERVICE WHERE serviceID = %s"
            cursor.execute(sql_check, (service_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Service not found'}), 404

            sql_delete = "DELETE FROM SERVICE WHERE serviceID = %s"
            cursor.execute(sql_delete, (service_id,))
            connection.commit()

        return jsonify({'message': 'Service deleted successfully!'}), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()

# ==============================================================================
# 17. API ENDPOINTS FOR BILL_SERVICE MANAGEMENT
# ==============================================================================


@app.route('/api/bill-services', methods=['POST'])
def add_bill_service():
    """Adds a new record to the 'Bill_Service' junction table."""
    connection = None
    try:
        bill_service_data = request.get_json()
        if not bill_service_data:
            return jsonify({'error': 'Invalid JSON data provided.'}), 400

        bill_id = bill_service_data.get('billID')
        service_id = bill_service_data.get('serviceID')
        quantity = bill_service_data.get('quantity')
        total_service_price = bill_service_data.get('totalServicePrice')

        if not all([bill_id, service_id, quantity]):
            return jsonify({'error': 'Missing required fields'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql = """
            INSERT INTO BILL_SERVICE (billID, serviceID, quantity, totalServicePrice)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (bill_id, service_id,
                                 quantity, total_service_price))
            connection.commit()
            new_bill_service_id = cursor.lastrowid

        return jsonify({
            'message': 'Bill service added successfully!',
            'billServiceID': new_bill_service_id,
            'data': bill_service_data
        }), 201

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/bill-services', methods=['GET'])
def get_all_bill_services():
    """Retrieves all bill_service records."""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql = "SELECT * FROM BILL_SERVICE"
            cursor.execute(sql)
            bill_services = cursor.fetchall()

        return jsonify(bill_services), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/bill-services/<int:bill_service_id>', methods=['GET'])
def get_bill_service(bill_service_id):
    """Retrieves a single bill_service record by billServiceID."""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql = "SELECT * FROM BILL_SERVICE WHERE billServiceID = %s"
            cursor.execute(sql, (bill_service_id,))
            bill_service = cursor.fetchone()

        if bill_service:
            return jsonify(bill_service), 200
        else:
            return jsonify({'error': 'Bill service record not found'}), 404

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/bill-services/<int:bill_service_id>', methods=['PUT'])
def update_bill_service(bill_service_id):
    """Updates an existing bill_service record by billServiceID."""
    connection = None
    try:
        bill_service_data = request.get_json()
        if not bill_service_data:
            return jsonify({'error': 'Invalid JSON data provided.'}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql_check = "SELECT billServiceID FROM BILL_SERVICE WHERE billServiceID = %s"
            cursor.execute(sql_check, (bill_service_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Bill service record not found'}), 404

            fields = []
            values = []
            for key, value in bill_service_data.items():
                fields.append(f"{key} = %s")
                values.append(value)

            if not fields:
                return jsonify({'message': 'No fields to update.'}), 200

            values.append(bill_service_id)
            sql_update = f"UPDATE BILL_SERVICE SET {', '.join(fields)} WHERE billServiceID = %s"

            cursor.execute(sql_update, tuple(values))
            connection.commit()

        return jsonify({'message': 'Bill service record updated successfully!'}), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/bill-services/<int:bill_service_id>', methods=['DELETE'])
def delete_bill_service(bill_service_id):
    """Deletes a bill_service record by billServiceID."""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed.'}), 500

        with connection.cursor() as cursor:
            sql_check = "SELECT billServiceID FROM BILL_SERVICE WHERE billServiceID = %s"
            cursor.execute(sql_check, (bill_service_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Bill service record not found'}), 404

            sql_delete = "DELETE FROM BILL_SERVICE WHERE billServiceID = %s"
            cursor.execute(sql_delete, (bill_service_id,))
            connection.commit()

        return jsonify({'message': 'Bill service record deleted successfully!'}), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred.', 'details': str(e)}), 500
    finally:
        if connection:
            connection.close()


# ==============================================================================
# 18. RUN THE FLASK APPLICATION
# ==============================================================================
if __name__ == '__main__':
    app.run(debug=True, port=5000)
