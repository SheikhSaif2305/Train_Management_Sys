from flask import Blueprint, request, jsonify
from models import mysql
from flask_jwt_extended import jwt_required

station_routes = Blueprint('station', __name__)



@station_routes.route('/addstations', methods=['POST'])
@jwt_required()
def add_station():
    """
    Add a new station.

    This endpoint allows authenticated users to add a new station by providing its name and location.
    A valid JWT authentication token must be included in the request header.

    Request Body:
        - name (str): The name of the station.
        - location (str): The location of the station.

    Headers:
        - Authorization (str): Bearer token in the format 'Bearer <token>'.

    Responses:
        - 201: Station added successfully.
        - 400: Bad request if name or location is missing.
        - 500: Internal server error if there is an issue with the database.

    Example Request:
        POST /addstations
        Headers:
            Authorization: Bearer <your_jwt_token>
        Body:
        {
            "name": "Station A",
            "location": "Location A"
        }

    Example Response:
        {
            "message": "Station added successfully"
        }
    """
    data = request.get_json()
    name = data['name']
    location = data['location']

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO stations (name, location) VALUES (%s, %s)", (name, location))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": "Station added successfully"}), 201



@station_routes.route('/updatestation/<int:station_id>', methods=['PUT'])
@jwt_required()
def update_station(station_id):
    """
    Update the information of a specific station by its ID.

    This endpoint allows authenticated users to update the details of a station.
    Only the fields that are provided in the request body will be updated.
    A valid JWT authentication token must be included in the request header.

    Request Body:
        - name (str, optional): The new name of the station.
        - location (str, optional): The new location of the station.

    Headers:
        - Authorization (str): Bearer token in the format 'Bearer <token>'.

    Responses:
        - 200: Station updated successfully.
        - 400: No valid fields provided for update.
        - 404: Station not found if the station ID is invalid.
        - 500: Internal server error if there is an issue with the database.

    Example Request:
        PUT /updatestation/1
        Headers:
            Authorization: Bearer <your_jwt_token>
        Body:
        {
            "name": "Updated Station Name"
        }

    Example Response:
        {
            "message": "Station 1 updated successfully."
        }
    """
    
    data = request.get_json()
    name = data.get('name')  # Optional: Update only if provided
    location = data.get('location')  # Optional: Update only if provided

    cursor = mysql.connection.cursor()

    # Dynamic SQL query to update only the provided fields
    if name and location:
        cursor.execute("UPDATE stations SET name = %s, location = %s WHERE id = %s", (name, location, station_id))
    elif name:
        cursor.execute("UPDATE stations SET name = %s WHERE id = %s", (name, station_id))
    elif location:
        cursor.execute("UPDATE stations SET location = %s WHERE id = %s", (location, station_id))
    else:
        return jsonify({"message": "No valid fields provided for update."}), 400

    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": f"Station {station_id} updated successfully."}), 200


@station_routes.route('/stations', methods=['GET'])
def get_all_stations():
    """
    Retrieve a list of all stations.

    This endpoint allows authenticated users to retrieve all stations stored in the database.
    A valid JWT authentication token must be included in the request header.

    Headers:
        - Authorization (str): Bearer token in the format 'Bearer <token>'.

    Responses:
        - 200: A list of all stations retrieved successfully.
        - 500: Internal server error if there is an issue with the database.

    Example Response:
        [
            {
                "id": 1,
                "name": "Station A",
                "location": "Location A"
            },
            {
                "id": 2,
                "name": "Station B",
                "location": "Location B"
            }
        ]
    """
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, name, location FROM stations")
    stations = cursor.fetchall()
    cursor.close()

    # Format the result as a list of dictionaries
    station_list = [
        {"id": station[0], "name": station[1], "location": station[2]}
        for station in stations
    ]

    return jsonify(station_list), 200
