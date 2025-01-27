from flask import Flask, jsonify, request
import sqlite3
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Get database file path from environment variable or use default
DB_FILE = os.getenv('DB_FILE', 'gps_data.db')

def get_db_connection():
    """Create a database connection and return it with Row factory"""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/gps-data', methods=['GET'])
def get_gps_data():
    connection = None
    try:
        # Get database connection
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500

        # Get pagination parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        imei = request.args.get('imei')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Calculate offset
        offset = (page - 1) * per_page

        cursor = connection.cursor()

        # Build the base query
        query = "SELECT * FROM gps_data WHERE 1=1"
        count_query = "SELECT COUNT(*) as total FROM gps_data WHERE 1=1"
        params = []

        # Add filters if provided
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
        total_records = cursor.fetchone()[0]

        # Add pagination to main query
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([per_page, offset])

        # Get paginated data
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]

        # Convert datetime objects to string for JSON serialization
        for result in results:
            if 'timestamp' in result:
                result['timestamp'] = str(result['timestamp'])
            if 'created_at' in result:
                result['created_at'] = str(result['created_at'])

        # Calculate pagination metadata
        total_pages = (total_records + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1

        response = {
            'data': results,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_records': total_records,
                'total_pages': total_pages,
                'has_next': has_next,
                'has_prev': has_prev
            }
        }

        return jsonify(response)

    except Exception as e:
        print(f"Error in get_gps_data: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if connection:
            try:
                connection.close()
            except Exception as e:
                print(f"Error closing connection: {e}")

@app.route('/gps-data/<imei>/latest', methods=['GET'])
def get_latest_position(imei):
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = connection.cursor()
        
        query = """
        SELECT * FROM gps_data 
        WHERE imei = ? 
        ORDER BY timestamp DESC 
        LIMIT 1
        """
        cursor.execute(query, (imei,))
        row = cursor.fetchone()

        if row:
            result = dict(row)
            if 'timestamp' in result:
                result['timestamp'] = str(result['timestamp'])
            if 'created_at' in result:
                result['created_at'] = str(result['created_at'])
            return jsonify(result)
        else:
            return jsonify({'error': 'No data found for this IMEI'}), 404

    except Exception as e:
        print(f"Error in get_latest_position: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if connection:
            try:
                connection.close()
            except Exception as e:
                print(f"Error closing connection: {e}")

# Add CORS support
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

if __name__ == '__main__':
    # Verify database exists
    if not os.path.exists(DB_FILE):
        print(f"Warning: Database file {DB_FILE} does not exist. Make sure to run the GPS server first.")
    
    app.run(
        host=os.getenv('API_HOST', '127.0.0.1'),
        port=int(os.getenv('API_PORT', 5000)),
        debug=os.getenv('API_DEBUG', 'False').lower() == 'true'
    ) 