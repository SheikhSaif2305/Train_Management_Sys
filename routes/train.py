from flask import Blueprint, request, jsonify
from models import mysql
from flask_jwt_extended import jwt_required

train_routes = Blueprint('train', __name__)

@train_routes.route('/trains', methods=['POST'])
@jwt_required()
def create_train():
    """
    Create a new train and add its stops.

    This endpoint allows you to create a train and associate multiple stops with it.
    A valid JWT authentication token must be included in the request header.

    Request Body:
        - name (str): The name of the train.
        - description (str, optional): A description of the train.
        - stops (list): A list of stops, where each stop contains:
            - station_id (int): The ID of the station.
            - arrival_time (str): The arrival time in 'HH:MM:SS' format.
            - departure_time (str): The departure time in 'HH:MM:SS' format.

    Headers:
        - Authorization: Bearer <your_jwt_token>

    Example Request:
        POST /trains
        Headers:
            Authorization: Bearer <your_jwt_token>
        Body:
        {
            "name": "Express Train",
            "description": "Fast train service",
            "stops": [
                {"station_id": 1, "arrival_time": "10:00:00", "departure_time": "10:15:00"},
                {"station_id": 2, "arrival_time": "11:00:00", "departure_time": "11:10:00"}
            ]
        }

    Example Response:
        {
            "message": "Train and stops added successfully."
        }

    Response Codes:
        - 201: Train and stops added successfully.
        - 400: Bad request if the input data is invalid.
    """

    data = request.get_json()
    train_name = data['name']
    description = data.get('description', '')

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO trains (name, description) VALUES (%s, %s)", (train_name, description))
    train_id = cursor.lastrowid

    stops = data['stops']
    for stop in stops:
        station_id = stop['station_id']
        arrival_time = stop['arrival_time']
        departure_time = stop['departure_time']
        cursor.execute("""
            INSERT INTO train_stops (train_id, station_id, arrival_time, departure_time)
            VALUES (%s, %s, %s, %s)
        """, (train_id, station_id, arrival_time, departure_time))

    mysql.connection.commit()
    cursor.close()
    return jsonify({"message": "Train and stops added successfully."}), 201

@train_routes.route('/trains/<int:train_id>/stops/<int:stop_id>', methods=['PUT'])
@jwt_required()
def update_train_stop(train_id, stop_id):

    """
    Update arrival and/or departure time of a specific train stop.

    This endpoint allows you to update the times for a train stop.
    A valid JWT authentication token must be included in the request header.

    Request Body:
        - arrival_time (str, optional): The new arrival time.
        - departure_time (str, optional): The new departure time.

    Headers:
        - Authorization: Bearer <your_jwt_token>

    Example Request:
        PUT /trains/1/stops/2
        Headers:
            Authorization: Bearer <your_jwt_token>
        Body:
        {
            "arrival_time": "10:30:00",
            "departure_time": "10:45:00"
        }

    Example Response:
        {
            "message": "Train stop updated successfully."
        }

    Response Codes:
        - 200: Train stop updated successfully.
        - 400: No valid fields provided for update.
    """


    data = request.get_json()
    arrival_time = data.get('arrival_time')
    departure_time = data.get('departure_time')

    cursor = mysql.connection.cursor()
    if arrival_time and departure_time:
        cursor.execute("""
            UPDATE train_stops SET arrival_time = %s, departure_time = %s 
            WHERE id = %s AND train_id = %s
        """, (arrival_time, departure_time, stop_id, train_id))
    elif arrival_time:
        cursor.execute("""
            UPDATE train_stops SET arrival_time = %s WHERE id = %s AND train_id = %s
        """, (arrival_time, stop_id, train_id))
    elif departure_time:
        cursor.execute("""
            UPDATE train_stops SET departure_time = %s WHERE id = %s AND train_id = %s
        """, (departure_time, stop_id, train_id))
    else:
        return jsonify({"message": "No valid fields provided for update."}), 400

    mysql.connection.commit()
    cursor.close()
    return jsonify({"message": "Train stop updated successfully."}), 200

@train_routes.route('/trains', methods=['GET'])
def get_all_train_schedules():
    """
    Retrieve all train schedules, including stops and timings.

    This endpoint returns a list of all trains and their respective stops with arrival and departure times.

    Example Request:
        GET /trains

    Example Response:
        [
            {
                "id": 1,
                "name": "Express Train",
                "description": "Fast train service",
                "stops": [
                    {
                        "station_id": 1,
                        "station_name": "Station A",
                        "arrival_time": "10:00:00",
                        "departure_time": "10:15:00"
                    },
                    {
                        "station_id": 2,
                        "station_name": "Station B",
                        "arrival_time": "11:00:00",
                        "departure_time": "11:10:00"
                    }
                ]
            }
        ]

    Response Codes:
        - 200: Successfully retrieved train schedules.
        - 500: Internal server error if something goes wrong.
    """
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT t.id, t.name, t.description, ts.station_id, s.name AS station_name, 
               ts.arrival_time, ts.departure_time
        FROM trains t
        JOIN train_stops ts ON t.id = ts.train_id
        JOIN stations s ON ts.station_id = s.id
        ORDER BY t.id, ts.arrival_time
    """)
    results = cursor.fetchall()
    cursor.close()

    train_schedules = {}
    for row in results:
        train_id, train_name, description, station_id, station_name, arrival, departure = row
        if train_id not in train_schedules:
            train_schedules[train_id] = {
                "name": train_name,
                "description": description,
                "stops": []
            }
        train_schedules[train_id]["stops"].append({
            "station_id": station_id,
            "station_name": station_name,
            "arrival_time": str(arrival),
            "departure_time": str(departure)
        })

    train_list = [{"id": k, **v} for k, v in train_schedules.items()]
    return jsonify(train_list), 200
