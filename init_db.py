import mysql.connector
import bcrypt
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# MySQL Configuration
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

# Real Indian Railway Data
REAL_STATIONS = [
    ("New Delhi", "NDLS"),
    ("Mumbai Central", "MMCT"),
    ("Kolkata Howrah", "HWH"),
    ("Chennai Central", "MAS"),
    ("KSR Bengaluru", "SBC"),
    ("Hyderabad Deccan", "HYB"),
    ("Ahmedabad Junction", "ADI"),
    ("Pune Junction", "PUNE"),
    ("Jaipur Junction", "JP"),
    ("Lucknow Charbagh", "LKO"),
    ("Varanasi Junction", "BSB"),
    ("Trivandrum Central", "TVC"),
    ("Patna Junction", "PNBE"),
    ("Bhopal Junction", "BPL")
]

REAL_TRAINS = [
    # -- New Delhi <-> Varanasi --
    ("Vande Bharat Exp (22436)", "New Delhi", "Varanasi Junction", "06:00:00", "14:00:00", 1128),
    ("Shiv Ganga Express (12560)", "New Delhi", "Varanasi Junction", "18:55:00", "07:00:00", 1200),
    ("Kashi Vishwanath Exp (14258)", "New Delhi", "Varanasi Junction", "11:35:00", "04:30:00", 900),
    ("Mahamana Express (22418)", "New Delhi", "Varanasi Junction", "18:35:00", "08:25:00", 1000),

    # -- Mumbai <-> New Delhi --
    ("Mumbai Rajdhani (12951)", "Mumbai Central", "New Delhi", "17:00:00", "08:30:00", 1200),
    ("August Kranti Rajdhani (12953)", "Mumbai Central", "New Delhi", "17:15:00", "09:40:00", 1100),
    ("Golden Temple Mail (12903)", "Mumbai Central", "New Delhi", "18:45:00", "07:00:00", 1300),
    ("Paschim Express (12925)", "Mumbai Central", "New Delhi", "11:25:00", "10:40:00", 1400),
    ("Maharashtra Sampark Kranti (12907)", "Mumbai Central", "New Delhi", "17:30:00", "13:35:00", 1000),
    
    # -- Kolkata <-> New Delhi --
    ("Howrah Rajdhani (12301)", "Kolkata Howrah", "New Delhi", "16:50:00", "10:00:00", 1200),
    ("Poorva Express (12303)", "Kolkata Howrah", "New Delhi", "08:00:00", "06:00:00", 1300),
    ("Netaji Express (12311)", "Kolkata Howrah", "New Delhi", "21:55:00", "20:55:00", 1100),

    # -- Kolkata <-> Chennai --
    ("Coromandel Express (12841)", "Kolkata Howrah", "Chennai Central", "15:20:00", "16:50:00", 1500),
    ("Howrah - Chennai Mail (12839)", "Kolkata Howrah", "Chennai Central", "23:55:00", "03:50:00", 1200),

    # -- Delhi <-> Bhopal --
    ("Shatabdi Express (12002)", "New Delhi", "Bhopal Junction", "06:00:00", "14:30:00", 900),
    ("Gondwana Express (12406)", "New Delhi", "Bhopal Junction", "15:05:00", "07:30:00", 1100),
    ("Grand Trunk Express (12616)", "New Delhi", "Bhopal Junction", "16:10:00", "03:35:00", 1250),

    # -- Bangalore <-> Delhi --
    ("Karnataka Express (12627)", "KSR Bengaluru", "New Delhi", "19:20:00", "09:00:00", 1400),
    ("Rajdhani Express (22691)", "KSR Bengaluru", "New Delhi", "20:00:00", "05:30:00", 1000),
    ("YPR DEE Duronto (12213)", "KSR Bengaluru", "New Delhi", "23:40:00", "07:00:00", 800),

    # -- Hyderabad <-> Chennai --
    ("Charminar Express (12760)", "Hyderabad Deccan", "Chennai Central", "18:00:00", "08:15:00", 1100),
    ("Chennai Express (12604)", "Hyderabad Deccan", "Chennai Central", "16:50:00", "05:40:00", 1200),
    ("Kacheguda Express (17652)", "Hyderabad Deccan", "Chennai Central", "16:00:00", "07:00:00", 950),

    # -- Hyderabad <-> Bangalore --
    ("Kacheguda Exp (12785)", "Hyderabad Deccan", "KSR Bengaluru", "19:05:00", "06:25:00", 1100),
    ("Wainganga Exp (12252)", "Hyderabad Deccan", "KSR Bengaluru", "21:30:00", "11:00:00", 900),

    # -- Mumbai <-> Ahmedabad --
    ("Shatabdi Express (12010)", "Ahmedabad Junction", "Mumbai Central", "14:40:00", "21:20:00", 800),
    ("Gujarat Mail (12902)", "Ahmedabad Junction", "Mumbai Central", "22:00:00", "06:25:00", 1200),
    ("Karnavati Express (12934)", "Ahmedabad Junction", "Mumbai Central", "04:55:00", "12:15:00", 1000),
    ("Vande Bharat Exp (20902)", "Ahmedabad Junction", "Mumbai Central", "15:00:00", "20:25:00", 1128),
    
    # -- Pune <-> Mumbai --
    ("Deccan Queen (12124)", "Pune Junction", "Mumbai Central", "07:15:00", "10:25:00", 800),
    ("Indrayani Express (22106)", "Pune Junction", "Mumbai Central", "18:35:00", "22:00:00", 900),
    ("Sinhagad Express (11010)", "Pune Junction", "Mumbai Central", "06:05:00", "09:55:00", 1500),
    ("Deccan Express (11008)", "Pune Junction", "Mumbai Central", "15:15:00", "19:05:00", 1200),

    # -- Lucknow <-> Delhi --
    ("Gomti Express (12419)", "Lucknow Charbagh", "New Delhi", "06:00:00", "15:00:00", 1000),
    ("Lucknow Mail (12229)", "Lucknow Charbagh", "New Delhi", "22:00:00", "06:45:00", 1200),
    ("Shatabdi Express (12003)", "Lucknow Charbagh", "New Delhi", "15:35:00", "22:15:00", 900),
    
    # -- Chennai <-> Bangalore --
    ("Shatabdi Express (12027)", "Chennai Central", "KSR Bengaluru", "17:30:00", "22:25:00", 900),
    ("Brindavan Express (12640)", "KSR Bengaluru", "Chennai Central", "15:10:00", "21:10:00", 1200),
    ("Lalbagh Express (12608)", "KSR Bengaluru", "Chennai Central", "06:30:00", "12:35:00", 1100),
    ("Chennai Mail (12658)", "KSR Bengaluru", "Chennai Central", "22:40:00", "04:20:00", 1400),

    # -- Trivandrum <-> Delhi --
    ("Kerala Express (12626)", "New Delhi", "Trivandrum Central", "11:25:00", "14:30:00", 1600),
    ("Rajdhani Express (12432)", "New Delhi", "Trivandrum Central", "10:55:00", "05:15:00", 1000),

    # -- Jaipur <-> Delhi --
    ("Ajmer Shatabdi (12016)", "New Delhi", "Jaipur Junction", "06:10:00", "10:45:00", 800),
    ("Pink City Express (12964)", "Jaipur Junction", "New Delhi", "11:00:00", "16:00:00", 1000),
    ("Double Decker Exp (12985)", "Jaipur Junction", "New Delhi", "06:00:00", "10:30:00", 1300),

    # -- Cross Country --
    ("Sanghamitra Exp (12295)", "KSR Bengaluru", "Patna Junction", "09:00:00", "07:40:00", 1400),
    ("Patna Rajdhani (12309)", "Patna Junction", "New Delhi", "17:30:00", "06:00:00", 1100),
    ("Bhopal Express (12155)", "Bhopal Junction", "New Delhi", "21:00:00", "05:00:00", 1200),
    ("Ganga Kaveri Exp (12670)", "Varanasi Junction", "Chennai Central", "21:00:00", "14:00:00", 1300),
    ("Sabarmati Express (19167)", "Ahmedabad Junction", "Varanasi Junction", "20:00:00", "04:00:00", 900),
    ("Duronto Express (12245)", "Kolkata Howrah", "KSR Bengaluru", "10:50:00", "16:00:00", 1200),
]

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    print("Connected to MySQL successfully!")

    # 1. Clear existing data to avoid duplicates if run multiple times
    # Note: We should be careful with foreign keys. 
    # Ideally this script is run after schema creation, effectively on an empty DB.
    # But to be safe, we can try to empty tables.
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("TRUNCATE TABLE bookings")
        cursor.execute("TRUNCATE TABLE tickets")
        cursor.execute("TRUNCATE TABLE train_schedule")
        cursor.execute("TRUNCATE TABLE stations")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        print("Cleared old data.")
    except Exception as e:
        print(f"Warning clearing data: {e}")

    # 2. Insert Stations
    station_map = {} # Maps Name -> Database ID
    for name, code in REAL_STATIONS:
        try:
            cursor.execute(
                "INSERT INTO stations (station_name, code) VALUES (%s, %s)",
                (name, code)
            )
            station_map[name] = cursor.lastrowid
            print(f"Added station: {name} ({code})")
        except mysql.connector.Error as err:
            print(f"Error adding station {name}: {err}")

    # 3. Insert Schedules
    # First, insert the manual real trains
    existing_routes = set()

    for t_name, src, dest, dep, arr, seats in REAL_TRAINS:
        src_id = station_map.get(src)
        dest_id = station_map.get(dest)

        if src_id and dest_id:
            try:
                cursor.execute(
                    """
                    INSERT INTO train_schedule 
                    (train_name, source_station_id, destination_station_id, departure_time, arrival_time, total_seats)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (t_name, src_id, dest_id, dep, arr, seats)
                )
                existing_routes.add((src, dest))
                print(f"Added Real Train: {t_name}")
            except mysql.connector.Error as err:
                print(f"Error adding train {t_name}: {err}")

    # 4. Generate Synthetic Trains for ALL other combinations
    # The user wants "all possible trains that are available in the dropdown"
    import random
    
    cities = list(station_map.keys())
    for source in cities:
        for destination in cities:
            if source == destination:
                continue
            
            # If we already added a real train for this route, skip (or add more if you want multiple)
            # But let's ensure at least one exists.
            if (source, destination) in existing_routes:
                continue

            # Create a synthetic train
            # Naming convention: Source-Dest Superfast
            train_name = f"{source.split(' ')[0]}-{destination.split(' ')[0]} Express"
            
            # Randomize times
            dep_hour = random.randint(5, 22)
            dep_min = random.choice(["00", "15", "30", "45"])
            duration = random.randint(4, 24)
            
            dep_time = f"{dep_hour:02d}:{dep_min}:00"
            
            # simple arr calc (does not handle date change logic in string but DB time type is simpler)
            arr_hour = (dep_hour + duration) % 24
            arr_min = dep_min
            arr_time = f"{arr_hour:02d}:{arr_min}:00"
            
            seats = random.choice([800, 1000, 1200, 1500])
            
            try:
                cursor.execute(
                    """
                    INSERT INTO train_schedule 
                    (train_name, source_station_id, destination_station_id, departure_time, arrival_time, total_seats)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (train_name, station_map[source], station_map[destination], dep_time, arr_time, seats)
                )
                print(f"Added Generated Train: {train_name}")
            except mysql.connector.Error as err:
                print(f"Error generating train {train_name}: {err}")

    # 5. Ensure Admin User Exists
    try:
        cursor.execute("SELECT COUNT(*) FROM admin WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            hashed_pw = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
            cursor.execute(
                "INSERT INTO admin (username, password, is_admin) VALUES (%s, %s, %s)",
                ('admin', hashed_pw.decode('utf-8'), True)
            )
            print("Created default admin user.")
        else:
            # Updates admin privelege just in case
            cursor.execute("UPDATE admin SET is_admin = TRUE WHERE username = 'admin'")
            print("Verified admin user.")
            
    except mysql.connector.Error as err:
        print(f"Error handling admin user: {err}")

    conn.commit()
    print("\nReal Indian Railway data initialization completed!")

except mysql.connector.Error as err:
    print(f"Database Connection Error: {err}")

finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()