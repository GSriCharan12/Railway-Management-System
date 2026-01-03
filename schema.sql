-- 1. Stations Table
CREATE TABLE IF NOT EXISTS stations (
  station_id INT AUTO_INCREMENT PRIMARY KEY,
  station_name VARCHAR(100) NOT NULL,
  code VARCHAR(10) UNIQUE NOT NULL
);

-- 2. Train Schedule Table
CREATE TABLE IF NOT EXISTS train_schedule (
  schedule_id INT AUTO_INCREMENT PRIMARY KEY,
  train_name VARCHAR(100),
  source_station_id INT,
  destination_station_id INT,
  departure_time TIME,
  arrival_time TIME,
  total_seats INT,
  FOREIGN KEY (source_station_id) REFERENCES stations(station_id),
  FOREIGN KEY (destination_station_id) REFERENCES stations(station_id)
);

-- 3. Passengers Table
CREATE TABLE IF NOT EXISTS passengers (
  passenger_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  email VARCHAR(100)
);

-- 4. Bookings Table
CREATE TABLE IF NOT EXISTS bookings (
  booking_id INT AUTO_INCREMENT PRIMARY KEY,
  passenger_id INT,
  schedule_id INT,
  booking_date DATE,
  FOREIGN KEY (passenger_id) REFERENCES passengers(passenger_id),
  FOREIGN KEY (schedule_id) REFERENCES train_schedule(schedule_id)
);

-- 5. Tickets Table
CREATE TABLE IF NOT EXISTS tickets (
  ticket_id INT AUTO_INCREMENT PRIMARY KEY,
  booking_id INT,
  seat_number VARCHAR(20),
  travel_date DATE,
  FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
);

-- 6. Payments Table
CREATE TABLE IF NOT EXISTS payments (
  payment_id INT AUTO_INCREMENT PRIMARY KEY,
  booking_id INT,
  amount DECIMAL(10, 2),
  payment_date DATETIME,
  payment_method VARCHAR(50),
  FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
);

-- 7. Feedbacks Table
CREATE TABLE IF NOT EXISTS feedbacks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Optional Admin Table
CREATE TABLE IF NOT EXISTS admin (
  admin_id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) UNIQUE,
  password VARCHAR(100),
  is_admin BOOLEAN DEFAULT FALSE
);

-- Insert default admin user (password: admin123) if not existing
INSERT IGNORE INTO admin (username, password, is_admin) VALUES ('admin', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', TRUE); 