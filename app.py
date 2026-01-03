from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import os
from dotenv import load_dotenv
import jwt
import bcrypt
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
import json

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# MySQL Configuration
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

# Custom JSON serializer for handling time values
def process_row_values(row):
    if not row:
        return row
    
    result = {}
    for key, value in row.items():
        if isinstance(value, timedelta):
            # Convert timedelta to string in format HH:MM:SS
            seconds = value.total_seconds()
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            result[key] = f"{hours:02d}:{minutes:02d}:{secs:02d}"
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        else:
            result[key] = value
    return result

# Helper function to execute SQL queries
def execute_query(query, params=None, fetch=True):
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch:
            result = cursor.fetchall()
            # Make sure we consume all results
            while cursor.nextset():
                pass  # Consume any additional result sets
            connection.commit()
            return result
        else:
            connection.commit()
            # For non-fetch queries, we still need to handle any result sets
            while cursor.nextset():
                pass  # Consume any additional result sets
            return None
    except Error as e:
        print(f"Error executing query: {e}")
        return None
    finally:
        if cursor:
            try:
                # Consume any remaining result sets
                while cursor.nextset():
                    pass
                cursor.close()
            except Error:
                # If we still get an error, just pass
                pass
        if connection and connection.is_connected():
            connection.close()

# Authentication middleware
def token_required(f):
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            token = token.split()[1]
            data = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
            return f(*args, **kwargs)
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
    decorated.__name__ = f.__name__
    return decorated

# Admin-only authentication middleware
def admin_required(f):
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            token = token.split()[1]
            data = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
            # Check if the user is an admin
            if not data.get('is_admin', False):
                return jsonify({'message': 'Admin access required!'}), 403
            return f(*args, **kwargs)
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
    decorated.__name__ = f.__name__
    return decorated

# Serve index.html as the root route
@app.route('/')
def serve_index():
    return render_template('index.html')

# Serve other HTML files
@app.route('/<path:path>')
def serve_static(path):
    if path.endswith('.html'):
        return render_template(path)
    return send_from_directory('static', path)

# Admin login route
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = str(data.get('username')).strip()
    password = str(data.get('password')).strip()
    
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # ULTIMATE SELF-HEALING: Force Create or Update the admin user every login attempt
        # This ensures credentials are ALWAYS 'admin' / 'admin123'
        hashed_pw = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Check if table exists, if not create it
        cursor.execute("CREATE TABLE IF NOT EXISTS admin (admin_id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50) UNIQUE, password VARCHAR(100), is_admin BOOLEAN DEFAULT FALSE)")
        
        # Ensure user 'admin' exists with correct privilege and password
        cursor.execute("SELECT * FROM admin WHERE username = 'admin'")
        existing = cursor.fetchone()
        if not existing:
            cursor.execute("INSERT INTO admin (username, password, is_admin) VALUES ('admin', %s, 1)", (hashed_pw,))
        else:
            # Force update password and privileges to ensure they are always correct
            cursor.execute("UPDATE admin SET password = %s, is_admin = 1 WHERE username = 'admin'", (hashed_pw,))
        
        connection.commit()

        # Reload the user record
        cursor.execute("SELECT * FROM admin WHERE username = %s AND is_admin = 1", (username,))
        admin = cursor.fetchall()
        cursor.close()
        
        if not admin:
            connection.close()
            return jsonify({'message': 'User not found in database'}), 401
            
        stored_password = admin[0]['password'].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), stored_password):
            # Fallback for SECRET_KEY if not set in cloud
            secret = os.getenv('SECRET_KEY') or 'super_secret_railway_key_2024'
            token = jwt.encode({
                'user': username,
                'is_admin': True,
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, secret)
            
            connection.close()
            return jsonify({'token': token, 'is_admin': True})
        
        connection.close()
        return jsonify({'message': 'Invalid credentials'}), 401
    
    except Exception as e:
        print(f"FATAL LOGIN ERROR: {e}")
        return jsonify({'message': f'Server Error: {str(e)}'}), 500

# Stations routes
@app.route('/api/stations', methods=['GET'])
def get_stations():
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM stations"
        cursor.execute(query)
        stations = cursor.fetchall()
        
        return jsonify(stations)
    except Error as e:
        print(f"Error fetching stations: {e}")
        return jsonify([]), 500
    finally:
        if cursor:
            try:
                cursor.close()
            except Error:
                pass
        if connection and connection.is_connected():
            connection.close()

@app.route('/api/stations', methods=['POST'])
@admin_required
def add_station():
    data = request.get_json()
    try:
        result = execute_query(
            "INSERT INTO stations (station_name, code) VALUES (%s, %s)",
            (data['station_name'], data['code']),
            fetch=False
        )
        return jsonify({'message': 'Station added successfully'})
    except Exception as e:
        print(f"Error adding station: {e}")
        return jsonify({'message': 'Failed to add station'}), 500

# Train Schedule routes
@app.route('/api/schedules', methods=['GET'])
def get_schedules():
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT s.schedule_id as id, s.train_name, ss.station_name as source, ds.station_name as destination,
               s.departure_time, s.arrival_time, s.total_seats as available_seats
        FROM train_schedule s
        JOIN stations ss ON s.source_station_id = ss.station_id
        JOIN stations ds ON s.destination_station_id = ds.station_id
        """
        
        cursor.execute(query)
        schedules = cursor.fetchall()
        
        # Process all schedules to handle timedelta objects
        processed_schedules = [process_row_values(schedule) for schedule in schedules]
        
        return jsonify(processed_schedules)
    except Exception as e:
        print(f"Error in get_schedules: {e}")
        return jsonify([]), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/api/schedules', methods=['POST'])
@admin_required
def add_schedule():
    data = request.get_json()
    try:
        result = execute_query(
            """
            INSERT INTO train_schedule 
            (train_name, source_station_id, destination_station_id, departure_time, arrival_time, total_seats)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                data['train_name'],
                data['source_station_id'],
                data['destination_station_id'],
                data['departure_time'],
                data['arrival_time'],
                data['total_seats']
            ),
            fetch=False
        )
        return jsonify({'message': 'Schedule added successfully'})
    except Exception as e:
        print(f"Error adding schedule: {e}")
        return jsonify({'message': 'Failed to add schedule'}), 500

@app.route('/api/schedules/<int:id>', methods=['GET'])
def get_schedule_by_id(id):
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT s.schedule_id as id, s.train_name, ss.station_name as source, ds.station_name as destination,
               s.departure_time, s.arrival_time, s.total_seats as available_seats
        FROM train_schedule s
        JOIN stations ss ON s.source_station_id = ss.station_id
        JOIN stations ds ON s.destination_station_id = ds.station_id
        WHERE s.schedule_id = %s
        """
        
        cursor.execute(query, (id,))
        schedule = cursor.fetchone()
        
        if not schedule:
            return jsonify({"message": "Schedule not found"}), 404
        
        # Process the schedule to handle timedelta objects
        processed_schedule = process_row_values(schedule)
        
        return jsonify(processed_schedule)
    except Exception as e:
        print(f"Error in get_schedule_by_id: {e}")
        return jsonify({"message": "Error fetching schedule"}), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

# Booking routes
@app.route('/api/bookings', methods=['POST'])
def create_booking():
    data = request.get_json()
    connection = None
    cursor = None
    
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # First create passenger if not exists
        cursor.execute(
            "INSERT INTO passengers (name, email) VALUES (%s, %s)",
            (data['passenger_name'], data['passenger_email'])
        )
        connection.commit()
        
        cursor.execute("SELECT LAST_INSERT_ID()")
        passenger_id = cursor.fetchone()['LAST_INSERT_ID()']
        
        # Create booking
        cursor.execute(
            "INSERT INTO bookings (passenger_id, schedule_id, booking_date) VALUES (%s, %s, %s)",
            (passenger_id, data['schedule_id'], datetime.now().date())
        )
        connection.commit()
        
        cursor.execute("SELECT LAST_INSERT_ID()")
        booking_id = cursor.fetchone()['LAST_INSERT_ID()']
        
        # Create ticket
        cursor.execute(
            "INSERT INTO tickets (booking_id, seat_number, travel_date) VALUES (%s, %s, %s)",
            (booking_id, data['seat_number'], data['travel_date'])
        )
        connection.commit()
        
        # Create payment
        cursor.execute(
            "INSERT INTO payments (booking_id, amount, payment_date, payment_method) VALUES (%s, %s, %s, %s)",
            (
                booking_id,
                data['amount'],
                datetime.now(),
                data['payment_method']
            )
        )
        connection.commit()
        
        return jsonify({'message': 'Booking created successfully', 'booking_id': booking_id})
        
    except Exception as e:
        print(f"Error creating booking: {e}")
        return jsonify({'message': 'Failed to create booking'}), 500
    finally:
        if cursor:
            try:
                cursor.close()
            except Error:
                pass
        if connection and connection.is_connected():
            connection.close()

@app.route('/api/bookings/<int:booking_id>', methods=['GET'])
def get_booking(booking_id):
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT b.*, p.name, p.email, ts.train_name, 
               s1.station_name as source_name, s2.station_name as destination_name,
               t.seat_number, t.travel_date, py.amount, py.payment_method
        FROM bookings b
        JOIN passengers p ON b.passenger_id = p.passenger_id
        JOIN train_schedule ts ON b.schedule_id = ts.schedule_id
        JOIN stations s1 ON ts.source_station_id = s1.station_id
        JOIN stations s2 ON ts.destination_station_id = s2.station_id
        JOIN tickets t ON b.booking_id = t.booking_id
        JOIN payments py ON b.booking_id = py.booking_id
        WHERE b.booking_id = %s
        """
        cursor.execute(query, (booking_id,))
        booking = cursor.fetchall()
        
        if not booking:
            return jsonify({}), 404
            
        # Process the booking data to handle datetime objects
        processed_booking = process_row_values(booking[0]) if booking else {}
        
        return jsonify(processed_booking)
    except Error as e:
        print(f"Error fetching booking: {e}")
        return jsonify({}), 500
    finally:
        if cursor:
            try:
                cursor.close()
            except Error:
                pass
        if connection and connection.is_connected():
            connection.close()

# Signup route
@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()
    email = data.get('email')
    category = data.get('category')
    message = data.get('message')
    
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        cursor.execute(
            "INSERT INTO feedbacks (user_email, category, message) VALUES (%s, %s, %s)",
            (email, category, message)
        )
        connection.commit()
        
        return jsonify({'message': 'Feedback submitted successfully'})
    except Exception as e:
        print(f"Feedback error: {e}")
        return jsonify({'message': 'Failed to submit feedback'}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'connection' in locals(): connection.close()

@app.route('/api/admin/feedbacks', methods=['GET'])
@admin_required
def get_feedbacks(current_user):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM feedbacks ORDER BY created_at DESC")
        feedbacks = cursor.fetchall()
        return jsonify(feedbacks)
    except Exception as e:
        return jsonify([]), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'connection' in locals(): connection.close()

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    try:
        # Create a new connection for this request
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # Check if username already exists
        cursor.execute("SELECT * FROM admin WHERE username = %s", (username,))
        existing_user = cursor.fetchall()
        
        if existing_user:
            cursor.close()
            connection.close()
            return jsonify({'message': 'Username already exists'}), 400
        
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Insert new user as a regular user (not admin)
        cursor.execute(
            "INSERT INTO admin (username, password) VALUES (%s, %s)",
            (username, hashed_password.decode('utf-8'))
        )
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return jsonify({'message': 'User registered successfully'})
    
    except Exception as e:
        print(f"Signup error: {e}")
        return jsonify({'message': 'An error occurred during signup'}), 500

# Regular user login route
@app.route('/api/login', methods=['POST'])
def user_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    try:
        # Create a new connection for this request
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # Execute query to find user
        cursor.execute("SELECT * FROM admin WHERE username = %s", (username,))
        user = cursor.fetchall()
        cursor.close()
        
        if not user:
            connection.close()
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # Check password
        stored_password = user[0]['password'].encode('utf-8') if user[0]['password'] else b''
        if bcrypt.checkpw(password.encode('utf-8'), stored_password):
            # Create token without admin privileges
            token = jwt.encode({
                'user': username,
                'is_admin': False,
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, os.getenv('SECRET_KEY'))
            
            connection.close()
            return jsonify({'token': token, 'is_admin': False})
        
        connection.close()
        return jsonify({'message': 'Invalid credentials'}), 401
    
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'message': 'An error occurred during login'}), 500

# Get all bookings count
@app.route('/api/bookings/count', methods=['GET'])
@admin_required
def get_bookings_count():
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # Get total bookings count
        cursor.execute("SELECT COUNT(*) as total FROM bookings")
        result = cursor.fetchone()
        
        return jsonify({'count': result['total']})
    except Error as e:
        print(f"Error fetching booking count: {e}")
        return jsonify({'count': 0}), 500
    finally:
        if cursor:
            try:
                cursor.close()
            except Error:
                pass
        if connection and connection.is_connected():
            connection.close()

# Get all bookings for admin
@app.route('/api/bookings', methods=['GET'])
@admin_required
def get_all_bookings():
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT b.booking_id, p.name as passenger_name, ts.train_name, 
               s1.station_name as source, s2.station_name as destination,
               t.travel_date, t.seat_number, py.amount
        FROM bookings b
        JOIN passengers p ON b.passenger_id = p.passenger_id
        JOIN train_schedule ts ON b.schedule_id = ts.schedule_id
        JOIN stations s1 ON ts.source_station_id = s1.station_id
        JOIN stations s2 ON ts.destination_station_id = s2.station_id
        JOIN tickets t ON b.booking_id = t.booking_id
        JOIN payments py ON b.booking_id = py.booking_id
        ORDER BY b.booking_id DESC
        """
        
        cursor.execute(query)
        bookings = cursor.fetchall()
        
        # Process all bookings to handle datetime objects
        processed_bookings = [process_row_values(booking) for booking in bookings]
        
        return jsonify(processed_bookings)
    except Error as e:
        print(f"Error fetching all bookings: {e}")
        return jsonify([]), 500
    finally:
        if cursor:
            try:
                cursor.close()
            except Error:
                pass
        if connection and connection.is_connected():
            connection.close()

# Bullet-proof Route to Initialize Database on Railway
@app.route('/init-db')
def init_database():
    outputs = []
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # 1. Run Schema statement by statement
        with open('schema.sql', 'r') as f:
            schema = f.read()
        
        for statement in schema.split(';'):
            stmt = statement.strip()
            if stmt:
                try:
                    cursor.execute(stmt)
                    outputs.append(f"Executed: {stmt[:30]}...")
                except Exception as e:
                    outputs.append(f"Skipped/Error: {stmt[:30]}... ({str(e)})")
        
        connection.commit()

        # 2. Explicitly ensure Admin user exists (Password: admin123)
        # We handle this in Python to be 100% sure the bcrypt hash is correct
        cursor.execute("SELECT * FROM admin WHERE username = 'admin'")
        if not cursor.fetchone():
            hashed_pw = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("INSERT INTO admin (username, password, is_admin) VALUES ('admin', %s, 1)", (hashed_pw,))
            outputs.append("SUCCESS: Created default admin user (admin / admin123)")
        else:
            outputs.append("INFO: Admin user already exists")

        # 3. Populate Demo Data (Stations & Trains)
        REAL_STATIONS = [
            ("New Delhi", "NDLS"), ("Mumbai Central", "MMCT"), ("Kolkata Howrah", "HWH"),
            ("Chennai Central", "MAS"), ("KSR Bengaluru", "SBC"), ("Hyderabad Deccan", "HYB")
        ]
        
        station_map = {}
        for name, code in REAL_STATIONS:
            cursor.execute("SELECT station_id FROM stations WHERE code = %s", (code,))
            row = cursor.fetchone()
            if not row:
                cursor.execute("INSERT INTO stations (station_name, code) VALUES (%s, %s)", (name, code))
                station_map[name] = cursor.lastrowid
            else:
                station_map[name] = row['station_id']

        connection.commit()
        cursor.close()
        connection.close()
        
        return f"<h3>Database Setup Complete!</h3><pre>{' <br> '.join(outputs)}</pre><br><a href='/'>Go to Home</a>"
    except Exception as e:
        return f"Database initialization failed: {str(e)}"

# Disable Browser Caching
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port) 