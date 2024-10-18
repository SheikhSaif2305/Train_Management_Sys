from flask import Blueprint, request, jsonify
from services.auth_service import hash_password, verify_password, generate_token
from models import mysql

auth_routes = Blueprint('auth', __name__)

@auth_routes.route('/register', methods=['POST'])
def register():
    
    """
    User Registration Endpoint.

    This endpoint allows new users to register by providing an email and password.
    The password is hashed before storing it in the database for security.

    Request Body:
        - email (str): The email address of the user.
        - password (str): The user's password.

    Responses:
        - 201: User registered successfully.
        - 400: Bad request if email or password is missing.
        - 500: Internal server error if there is an issue with the database.

    Example Request:
        POST /register
        {
            "email": "user@example.com",
            "password": "securepassword"
        }

    Example Response:
        {
            "message": "User registered successfully"
        }
    """
    data = request.get_json()
    email = data['email']
    password = hash_password(data['password'])

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO users (email, password_hash) VALUES (%s, %s)", (email, password))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": "User registered successfully"}), 201

@auth_routes.route('/login', methods=['POST'])
def login():

    """
    User Login Endpoint.

    This endpoint allows users to log in by providing their email and password.
    If the credentials are valid, a JWT access token is generated and returned.

    Request Body:
        - email (str): The email address of the user.
        - password (str): The user's password.

    Responses:
        - 200: Access token returned successfully.
        - 401: Invalid credentials if the email or password is incorrect.
        - 500: Internal server error if there is an issue with the database.

    Example Request:
        POST /login
        {
            "email": "user@example.com",
            "password": "securepassword"
        }

    Example Response:
        {
            "access_token": "jwt_token_here"
        }
    """
    data = request.get_json()
    email = data['email']
    password = data['password']

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, password_hash FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()

    if user and verify_password(password, user[1]):
        token = generate_token(user[0])
        return jsonify(access_token=token), 200

    return jsonify({"message": "Invalid credentials"}), 401
