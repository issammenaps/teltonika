import socket
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_sample_avl_data():
    # This is a sample AVL data packet
    # Format: Preamble(4) + Length(4) + CodecID(1) + Number of Data(1) + Timestamp(8) + Priority(1) + GPS Data
    sample_data = bytes.fromhex(
        '00000000'  # Preamble
        '00000001'  # Length
        '08'        # Codec ID
        '01'        # Number of Data
        '00000189A5F3C195'  # Timestamp
        '01'        # Priority
        '0000000A'  # Longitude (0.00001 degrees)
        '0000000A'  # Latitude (0.00001 degrees)
        '0064'      # Altitude (100 meters)
        '00B4'      # Angle (180 degrees)
        '05'        # Satellites (5)
        '0032'      # Speed (50 km/h)
    )
    return sample_data

def test_gps_server():
    # Get server configuration from environment variables
    host = os.getenv('GPS_SERVER_HOST', 'localhost')  # Default to localhost for testing
    port = int(os.getenv('GPS_SERVER_PORT', 50262))   # Default to 50262 if not set
    
    # Connect to the server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    
    # Send IMEI
    imei = os.getenv('TEST_IMEI', '123456789012345')  # Allow IMEI to be configured
    client.send(imei.encode())
    
    # Receive start command
    response = client.recv(1024)
    print(f"Received response: {response.hex()}")
    
    # Get number of packets from environment or default to 3
    num_packets = int(os.getenv('TEST_NUM_PACKETS', '3'))
    delay = float(os.getenv('TEST_PACKET_DELAY', '2'))  # Delay in seconds between packets
    
    # Send sample AVL data
    for _ in range(num_packets):
        avl_data = create_sample_avl_data()
        client.send(avl_data)
        time.sleep(delay)
    
    client.close()

if __name__ == "__main__":
    test_gps_server() 