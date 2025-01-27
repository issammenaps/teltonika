from flask import Flask, jsonify, request
import pymysql
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST', '127.0.0.1'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        db=os.getenv('DB_NAME', 'gps_data_db'),
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/gps-data', methods=['GET'])
def get_gps_data():
    # Get pagination parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    imei = request.args.get('imei')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Calculate offset
    offset = (page - 1) * per_page

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Build the base query
            query = "SELECT * FROM gps_data WHERE 1=1"
            count_query = "SELECT COUNT(*) as total FROM gps_data WHERE 1=1"
            params = []

            # Add filters if provided
            if imei:
                query += " AND imei = %s"
                count_query += " AND imei = %s"
                params.append(imei)

            if start_date:
                query += " AND timestamp >= %s"
                count_query += " AND timestamp >= %s"
                params.append(start_date)

            if end_date:
                query += " AND timestamp <= %s"
                count_query += " AND timestamp <= %s"
                params.append(end_date)

            # Add pagination
            query += " ORDER BY timestamp DESC LIMIT %s OFFSET %s"
            params.extend([per_page, offset])

            # Get total count
            cursor.execute(count_query, params[:-2] if params else None)
            total_records = cursor.fetchone()['total']

            # Get paginated data
            cursor.execute(query, params)
            results = cursor.fetchall()

            # Convert datetime objects to string for JSON serialization
            for result in results:
                result['timestamp'] = result['timestamp'].strftime('%Y-%m-%d %H:%M:%S')

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
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

@app.route('/gps-data/<imei>/latest', methods=['GET'])
def get_latest_position(imei):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            query = """
            SELECT * FROM gps_data 
            WHERE imei = %s 
            ORDER BY timestamp DESC 
            LIMIT 1
            """
            cursor.execute(query, (imei,))
            result = cursor.fetchone()

            if result:
                result['timestamp'] = result['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                return jsonify(result)
            else:
                return jsonify({'error': 'No data found for this IMEI'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(
        host=os.getenv('API_HOST', '0.0.0.0'),
        port=int(os.getenv('API_PORT', 5000)),
        debug=os.getenv('API_DEBUG', 'False').lower() == 'true'
    ) 