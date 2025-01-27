import sqlite3
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Get database file path from environment variable or use default
DB_FILE = os.getenv('DB_FILE', 'gps_data.db')

def init_db():
    """Initialize the SQLite database and create table if it doesn't exist"""
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gps_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                imei TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                altitude INTEGER NOT NULL,
                angle INTEGER NOT NULL,
                satellites INTEGER NOT NULL,
                speed INTEGER NOT NULL,
                google_maps_url TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
    finally:
        conn.close()

def save_data(imei, timestamp, latitude, longitude, altitude, angle, satellites, speed):
    """Save GPS data to SQLite database"""
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.cursor()
        google_maps_url = f"https://www.google.com/maps?q={latitude},{longitude}"
        
        cursor.execute('''
            INSERT INTO gps_data (
                imei, timestamp, latitude, longitude, 
                altitude, angle, satellites, speed, google_maps_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            imei, timestamp, latitude, longitude,
            altitude, angle, satellites, speed, google_maps_url
        ))
        conn.commit()
    finally:
        conn.close()

def get_data(page=1, per_page=10, imei=None, start_date=None, end_date=None):
    """Retrieve GPS data with pagination and filtering"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    try:
        cursor = conn.cursor()
        
        # Build the query
        query = "SELECT * FROM gps_data WHERE 1=1"
        count_query = "SELECT COUNT(*) FROM gps_data WHERE 1=1"
        params = []

        if imei:
            query += " AND imei = ?"
            count_query += " AND imei = ?"
            params.append(imei)

        if start_date:
            query += " AND timestamp >= ?"
            count_query += " AND timestamp >= ?"
            params.append(start_date)

        if end_date:
            query += " AND timestamp <= ?"
            count_query += " AND timestamp <= ?"
            params.append(end_date)

        # Get total count
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]

        # Add pagination
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([per_page, (page - 1) * per_page])

        # Execute the main query
        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Convert rows to dictionaries
        results = []
        for row in rows:
            result = dict(row)
            # Convert datetime objects to strings
            result['timestamp'] = result['timestamp']
            result['created_at'] = result['created_at']
            results.append(result)

        return {
            'data': results,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_records': total_count,
                'total_pages': (total_count + per_page - 1) // per_page
            }
        }
    finally:
        conn.close()

def get_latest_position(imei):
    """Get the latest position for a specific IMEI"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM gps_data 
            WHERE imei = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''', (imei,))
        row = cursor.fetchone()
        
        if row:
            result = dict(row)
            result['timestamp'] = result['timestamp']
            result['created_at'] = result['created_at']
            return result
        return None
    finally:
        conn.close()

# Initialize the database when the module is imported
init_db()

