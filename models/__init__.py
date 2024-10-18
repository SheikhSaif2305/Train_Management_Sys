from flask_mysqldb import MySQL  # Import MySQL extension for Flask

# Initialize the MySQL object to be used across the app
mysql = MySQL()

def create_users_table(cursor):
    """
    Create the 'users' table if it does not exist.

    Fields:
    - id: Primary key, auto-incremented.
    - email: User's email, must be unique.
    - password_hash: Hashed password for security.
    - wallet_balance: Default is 0, stores the user's balance.
    """
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(100) UNIQUE,
            password_hash TEXT,
            wallet_balance FLOAT DEFAULT 0
        )
    """)

def create_stations_table(cursor):
    """
    Create the 'stations' table if it does not exist.

    Fields:
    - id: Primary key, auto-incremented.
    - name: Name of the station.
    - location: Location or address of the station.
    """
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            location VARCHAR(100)
        )
    """)

def create_trains_table(cursor):
    """
    Create the 'trains' table if it does not exist.

    Fields:
    - id: Primary key, auto-incremented.
    - name: Name of the train, must be unique.
    - description: Additional details about the train.
    """
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trains (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) UNIQUE,
            description TEXT
        )
    """)

def create_train_stops_table(cursor):
    """
    Create the 'train_stops' table if it does not exist.

    Fields:
    - id: Primary key, auto-incremented.
    - train_id: Foreign key referencing 'trains.id'.
    - station_id: Foreign key referencing 'stations.id'.
    - arrival_time: Time the train arrives at the station.
    - departure_time: Time the train departs from the station.

    Constraints:
    - If a train or station is deleted, related train stops are deleted (ON DELETE CASCADE).
    """
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS train_stops (
            id INT AUTO_INCREMENT PRIMARY KEY,
            train_id INT,
            station_id INT,
            arrival_time TIME,
            departure_time TIME,
            FOREIGN KEY (train_id) REFERENCES trains(id) ON DELETE CASCADE,
            FOREIGN KEY (station_id) REFERENCES stations(id) ON DELETE CASCADE
        )
    """)

def create_tickets_table(cursor):
    """
    Create the 'tickets' table if it does not exist.

    Fields:
    - id: Primary key, auto-incremented.
    - user_id: Foreign key referencing 'users.id'.
    - train_id: Foreign key referencing 'trains.id'.
    - from_station: Foreign key referencing 'stations.id' (departure).
    - to_station: Foreign key referencing 'stations.id' (destination).
    - price: Price of the ticket.
    - timestamp: Timestamp when the ticket was created.
    - is_valid: Boolean indicating if the ticket is still valid (default is TRUE).

    Constraints:
    - Cascading deletes on related entities (users, trains, stations).
    """
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            train_id INT,
            from_station INT,
            to_station INT,
            price FLOAT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_valid BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (train_id) REFERENCES trains(id) ON DELETE CASCADE,
            FOREIGN KEY (from_station) REFERENCES stations(id) ON DELETE CASCADE,
            FOREIGN KEY (to_station) REFERENCES stations(id) ON DELETE CASCADE
        )
    """)

def create_transectionHistory_table(cursor):
    """
    Create the 'transactions' table to log wallet transactions.

    Fields:
    - id: Primary key, auto-incremented.
    - user_id: Foreign key referencing 'users.id'.
    - amount: Amount involved in the transaction.
    - type: Enum type ('add' or 'deduct') indicating the transaction type.
    - timestamp: Timestamp when the transaction was recorded.

    Constraints:
    - On deleting a user, all their transactions are also deleted (ON DELETE CASCADE).
    """
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            amount FLOAT,
            type ENUM('add', 'deduct') NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

def init_db(app):
    """
    Initialize the MySQL database by creating required tables.

    Steps:
    1. Initialize the MySQL instance with the Flask app.
    2. Use the app's context to access the MySQL connection.
    3. Create all necessary tables (users, stations, trains, train stops, tickets, transactions).
    4. Commit the changes and close the cursor.

    Parameters:
    - app: The Flask application instance.
    """
    mysql.init_app(app)  # Bind the MySQL instance to the Flask app

    with app.app_context():  # Access the app context to use MySQL connection
        cursor = mysql.connection.cursor()  # Create a cursor to execute SQL queries

        # Call the table creation functions to set up the database
        create_users_table(cursor)
        create_stations_table(cursor)
        create_trains_table(cursor)
        create_train_stops_table(cursor)
        create_tickets_table(cursor)
        create_transectionHistory_table(cursor)

        # Commit changes to the database and close the cursor
        mysql.connection.commit()
        cursor.close()
