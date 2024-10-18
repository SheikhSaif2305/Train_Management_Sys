from flask import Blueprint, request, jsonify
from models import mysql
from flask_jwt_extended import jwt_required, get_jwt_identity

ticket_routes = Blueprint('ticket', __name__)

@ticket_routes.route('/tickets/purchase', methods=['POST'])
@jwt_required()
def purchase_ticket():
    """
    Purchase a ticket using wallet balance.

    This endpoint allows authenticated users to purchase a train ticket using their wallet balance.
    A valid JWT authentication token must be included in the request header.

    Request Body:
        - train_id (int): The ID of the train for which the ticket is being purchased.
        - from_station (str): The starting station of the journey.
        - to_station (str): The destination station of the journey.
        - price (float): The price of the ticket.

    Headers:
        - Authorization (str): Bearer token in the format 'Bearer <token>'.

    Responses:
        - 200: Ticket purchased successfully.
        - 400: Insufficient funds if the user's wallet balance is less than the ticket price.
        - 500: Internal server error if there is an issue with the database.

    Example Request:
        POST /tickets/purchase
        Headers:
            Authorization: Bearer <your_jwt_token>
        Body:
        {
            "train_id": 1,
            "from_station": "Station A",
            "to_station": "Station B",
            "price": 25.0
        }

    Example Response:
        {
            "message": "Ticket purchased successfully."
        }
    """
    
    user_id = get_jwt_identity()
    data = request.get_json()
    train_id = data['train_id']
    from_station = data['from_station']
    to_station = data['to_station']
    price = data['price']

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT wallet_balance FROM users WHERE id = %s", (user_id,))
    balance = cursor.fetchone()[0]

    if balance < price:
        return jsonify({"message": "Insufficient funds."}), 400

    # Deduct the amount and record the transaction
    cursor.execute("UPDATE users SET wallet_balance = wallet_balance - %s WHERE id = %s", (price, user_id))
    cursor.execute("""
        INSERT INTO tickets (user_id, train_id, from_station, to_station, price)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, train_id, from_station, to_station, price))
    cursor.execute("INSERT INTO transactions (user_id, amount, type) VALUES (%s, %s, 'deduct')", (user_id, price))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": "Ticket purchased successfully."}), 200
