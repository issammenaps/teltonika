import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def save_data(imei, timestamp, latitude, longitude, altitude, angle, satellites, speed):
    connection = pymysql.connect(
        host=os.getenv('DB_HOST', '127.0.0.1'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        db=os.getenv('DB_NAME', 'gps_data_db'),
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with connection.cursor() as cursor:
            google_maps_url = f"https://www.google.com/maps?q={latitude},{longitude}"
            sql = """
            INSERT INTO gps_data (imei, timestamp, latitude, longitude, altitude, angle, satellites, speed, google_maps_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (imei, timestamp, latitude, longitude, altitude, angle, satellites, speed, google_maps_url))
        connection.commit()
    finally:
        connection.close()

