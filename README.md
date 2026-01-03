# Railway Management System

A complete Railway Management System with Flask backend and web frontend. This system allows users to book tickets, check schedules, and administrators to manage trains and stations.

## Features

- User Authentication (Login/Signup)
- Train Schedule Management
- Station Management
- Booking System
- Admin Dashboard
- Responsive Design

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: MySQL
- **Frontend**: HTML, CSS (Tailwind CSS), JavaScript
- **Authentication**: JWT (JSON Web Tokens)

## Prerequisites

- Python 3.8 or higher
- MySQL Server
- pip (Python package manager)

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create the database:
   - Make sure MySQL is running
   - Create the database and tables:
     ```bash
     mysql -u root -p < schema.sql
     ```
   - Or run the SQL commands manually in MySQL

5. Configure environment variables:
   - Update the `.env` file with your database credentials:
     ```
     DB_HOST=localhost
     DB_USER=root
     DB_PASSWORD=your_password
     DB_NAME=railway_db
     SECRET_KEY=your-secret-key-here
     ```

6. Initialize sample data (optional):
   ```bash
   python init_db.py
   ```

## Running the Application

1. Start the Flask server:
   ```bash
   python app.py
   ```

2. Open your web browser and go to `http://localhost:5000`

## User Guide

### For Regular Users:
1. Browse to `http://localhost:5000`
2. Sign up for a new account or log in
3. View train schedules
4. Book tickets by selecting a train schedule
5. View booking details

### For Administrators:
1. Log in with admin credentials (default: admin/admin123)
2. Access the admin panel
3. Manage stations (add, edit, delete)
4. Manage train schedules (add, edit, delete)
5. View booking statistics

## API Endpoints

### Authentication
- `POST /api/admin/login` - Admin login
- `POST /api/signup` - User signup

### Stations
- `GET /api/stations` - Get all stations
- `POST /api/stations` - Add a new station (requires admin token)

### Train Schedules
- `GET /api/schedules` - Get all train schedules
- `POST /api/schedules` - Add a new schedule (requires admin token)

### Bookings
- `POST /api/bookings` - Create a new booking
- `GET /api/bookings/<booking_id>` - Get booking details

## Troubleshooting

- If you encounter database connection issues, ensure:
  - MySQL server is running
  - Database credentials in `.env` are correct
  - The database and tables exist

- If pages don't load properly:
  - Check that the Flask server is running
  - Check the browser console for any JavaScript errors
  - Ensure API endpoints are accessible

## License

This project is licensed under the MIT License - see the LICENSE file for details. 