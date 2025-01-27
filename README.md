
# Teltonika GPS Server

This project is a basic implementation of a GPS server that receives AVL data from Teltonika devices, decodes the data, and stores it into a MySQL database. It includes two main components:

1. **database.py** - Handles saving the decoded data into a MySQL database.
2. **gps_server.py** - Listens for incoming connections from Teltonika devices, receives AVL data, decodes it, and saves it using `database.py`.

## Requirements

- Python 3.x
- PyMySQL
- MySQL Server

## Installation

1. Clone the repository:


2. Install the required Python packages:
    ```bash
    pip install pymysql python-dotenv flask
    ```

3. Set up the MySQL database:
    - Create a database and a table to store the GPS data:
    ```sql
    CREATE DATABASE gps_data_db;
    
    USE gps_data_db;
    
    CREATE TABLE gps_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        imei VARCHAR(15) NOT NULL,
        timestamp DATETIME NOT NULL,
        latitude FLOAT NOT NULL,
        longitude FLOAT NOT NULL,
        altitude INT NOT NULL,
        angle INT NOT NULL,
        satellites INT NOT NULL,
        speed INT NOT NULL,
        google_maps_url VARCHAR(255) NOT NULL
    );
    ```

4. Update the database connection details in `database.py`:
    ```python
    connection = pymysql.connect(host='127.0.0.1', user='username', password='password', db='database', cursorclass=pymysql.cursors.DictCursor)
    ```
    Replace `'username'`, `'password'`, and `'database'` with your MySQL credentials.

## Usage

1. Start the GPS server:
    ```bash
    python gps_server.py
    ```    The server will start listening on `0.0.0.0:50262`.

2. The server will accept incoming connections from Teltonika devices, decode the AVL data, and store it into the MySQL database.

3. You can test the server with the `test_client.py` script. 
    ```bash
    python test_client.py
    ```
4. You can also test the server with the `api_server.py` script.
    ```bash
    python api_server.py
    ```
   

