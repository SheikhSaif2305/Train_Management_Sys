from flask import Blueprint, request, jsonify
from models import mysql
from flask_jwt_extended import jwt_required, get_jwt_identity

wallet_routes = Blueprint('wallet', __name__)




@wallet_routes.route('/wallet/add', methods=['POST'])
@jwt_required()
def add_funds():
    """
    Add funds to the user's wallet.

    This endpoint allows the logged-in user to add a specified amount to their wallet balance.
    A valid JWT authentication token must be included in the request header.

    Request Body:
        - amount (float): The amount to be added to the wallet.

    Headers:
        - Authorization: Bearer <your_jwt_token>

    Example Request:
        POST /wallet/add
        Headers:
            Authorization: Bearer <your_jwt_token>
        Body:
        {
            "amount": 100.50
        }

    Example Response:
        {
            "message": "Funds added successfully."
        }

    Response Codes:
        - 200: Funds added successfully.
        - 400: Bad request if the input data is invalid.
        - 500: Internal server error if the operation fails.
    """
    user_id = get_jwt_identity()
    amount = request.json['amount']

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE users SET wallet_balance = wallet_balance + %s WHERE id = %s", (amount, user_id))
    cursor.execute("INSERT INTO transactions (user_id, amount, type) VALUES (%s, %s, 'add')", (user_id, amount))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": "Funds added successfully."}), 200




@wallet_routes.route('/wallet/history', methods=['GET'])
@jwt_required()
def transaction_history():
    """
    Retrieve the transaction history for the logged-in user.

    This endpoint returns the complete transaction history of the logged-in user, 
    ordered by the latest transactions first. A valid JWT authentication token 
    must be included in the request header.

    Headers:
        - Authorization: Bearer <your_jwt_token>

    Example Request:
        GET /wallet/history
        Headers:
            Authorization: Bearer <your_jwt_token>

    Example Response:
        [
            {
                "amount": 100.50,
                "type": "add",
                "timestamp": "2024-10-18 12:30:45"
            },
            {
                "amount": 50.00,
                "type": "deduct",
                "timestamp": "2024-10-17 14:15:22"
            }
        ]

    Response Codes:
        - 200: Successfully retrieved the transaction history.
        - 500: Internal server error if the operation fails.
    """
    user_id = get_jwt_identity()

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT amount, type, timestamp FROM transactions WHERE user_id = %s ORDER BY timestamp DESC", (user_id,))
    transactions = cursor.fetchall()
    cursor.close()

    # Format the transactions as a list of dictionaries
    transaction_list = [
        {"amount": amount, "type": trans_type, "timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S')}
        for (amount, trans_type, timestamp) in transactions
    ]

    return jsonify(transaction_list), 200
