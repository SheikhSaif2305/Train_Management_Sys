from config import Config  # Import configuration settings
from flask import Flask  # Import Flask for building the web application
from models import init_db  # Import function to initialize the database
from flask_jwt_extended import JWTManager  # Import JWT for authentication
from apscheduler.schedulers.background import BackgroundScheduler  # Import scheduler for background tasks
import mysql.connector  # Use mysql.connector to connect to MySQL database

# Initialize Flask app
app = Flask(__name__)  # Create Flask application instance
jwt = JWTManager(app)  # Initialize JWT authentication with the app

# Register routes (import and attach blueprints)
from routes.auth import auth_routes
from routes.station import station_routes
from routes.wallet import wallet_routes
from routes.ticket import ticket_routes
from routes.train import train_routes

app.register_blueprint(auth_routes)  # Register auth-related routes
app.register_blueprint(station_routes)  # Register station-related routes
app.register_blueprint(wallet_routes)  # Register wallet-related routes
app.register_blueprint(ticket_routes)  # Register ticket-related routes
app.register_blueprint(train_routes)  # Register train-related routes

# Set MySQL and JWT configurations from the Config class
app.config['MYSQL_HOST'] = Config.MYSQL_HOST
app.config['MYSQL_USER'] = Config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = Config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = Config.MYSQL_DB
app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY

def get_mysql_connection():
    """
    Establish a new MySQL connection using mysql.connector.
    
    Returns:
        MySQL connection object.
    """
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
    )

def expire_tickets():
    """
    Mark expired tickets as invalid in the database.
    
    Uses:
        - A new MySQL connection to run SQL queries.
    
    SQL Logic:
        - Updates `is_valid` to FALSE for tickets that:
            1. Are currently marked as valid (`is_valid = TRUE`)
            AND
            2. if the departure_time < CURRENT_TIME()  
    """
    try:
        connection = get_mysql_connection()  # Get new MySQL connection
        cursor = connection.cursor()  # Create a cursor to execute queries

        # SQL query to invalidate expired tickets
        cursor.execute("""
            UPDATE tickets 
            SET is_valid = FALSE 
            WHERE is_valid = TRUE AND id IN (
                SELECT t.id 
                FROM tickets t
                JOIN train_stops ts ON t.train_id = ts.train_id
                WHERE ts.departure_time < CURRENT_TIME()
            )
        """)
        connection.commit()  # Commit the changes
        cursor.close()  # Close the cursor
        connection.close()  # Close the connection

    except mysql.connector.Error as err:
        # Print error message if MySQL operation fails
        print(f"Error during ticket expiration: {err}")

# Initialize the APScheduler to run periodic tasks in the background
scheduler = BackgroundScheduler()
scheduler.add_job(
    expire_tickets, 'interval', hours=1  # Schedule `expire_tickets` to run every hour
)
scheduler.start()  # Start the scheduler

# Main application entry point
if __name__ == '__main__':
    """
    Initialize the database and start the Flask server.
    
    Steps:
    1. Initialize the database by calling `init_db`.
    2. Start the Flask development server with debugging enabled.
    """
    init_db(app)  # Ensure all tables are created if they don't exist
    app.run(debug=True)  # Start the Flask server with debugging enabled
