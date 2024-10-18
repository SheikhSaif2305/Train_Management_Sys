


# **API Documentation**

## **Overview**  
This project offers a set of RESTful APIs for managing trains, stations, tickets, and wallets. The system utilizes **JWT authentication** for security and interacts with a MySQL database. 

---

## **Authentication**
**Authorization Header:** Required for protected routes  
```
Authorization: Bearer <your_token>
```

Make sure to include the JWT token in the `Authorization` header for every secured endpoint.

---

## **Endpoints**

### **1. User Authentication**  

#### **POST /register**  
**Description:** Register a new user.  
**Method:** `POST`  
**Path:** `/register`  
**Request Header:**
```
Content-Type: application/json
```
**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```
**Response:**
- **201 Created**
  ```json
  {
    "message": "User registered successfully"
  }
  ```
- **409 Conflict**
  ```json
  {
    "message": "User already exists"
  }
  ```

---

#### **POST /login**  
**Description:** Authenticate a user and receive a JWT token.  
**Method:** `POST`  
**Path:** `/login`  
**Request Header:**
```
Content-Type: application/json
```
**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```
**Response:**
- **200 OK**
  ```json
  {
    "access_token": "<jwt_token>"
  }
  ```
- **401 Unauthorized**
  ```json
  {
    "message": "Invalid credentials"
  }
  ```

---

### **2. Station Management**  

#### **POST /addstations**  
**Description:** Add a new train station.  
**Method:** `POST`  
**Path:** `/addstations`  
**Request Header:**
```
Authorization: Bearer <your_token>
Content-Type: application/json
```
**Request Body:**
```json
{
  "name": "Station A",
  "location": "City A"
}
```
**Response:**
- **201 Created**
  ```json
  {
    "message": "Station added successfully"
  }
  ```

---

#### **PUT /updatestation/<station_id>**  
**Description:** Update an existing station.  
**Method:** `PUT`  
**Path:** `/updatestation/<station_id>`  
**Request Header:**
```
Authorization: Bearer <your_token>
Content-Type: application/json
```
**Request Body:**
```json
{
  "name": "Updated Station",
  "location": "Updated City"
}
```
**Response:**
- **200 OK**
  ```json
  {
    "message": "Station <station_id> updated successfully"
  }
  ```

---

#### **GET /stations**  
**Description:** Retrieve all stations.  
**Method:** `GET`  
**Path:** `/stations`  
**Response:**
- **200 OK**
  ```json
  [
    {"id": 1, "name": "Station A", "location": "City A"},
    {"id": 2, "name": "Station B", "location": "City B"}
  ]
  ```

---

### **3. Train Management**  

#### **POST /trains**  
**Description:** Create a new train with stops.  
**Method:** `POST`  
**Path:** `/trains`  
**Request Header:**
```
Authorization: Bearer <your_token>
Content-Type: application/json
```
**Request Body:**
```json
{
  "name": "Express Train",
  "description": "Fast train from A to B",
  "stops": [
    {"station_id": 1, "arrival_time": "08:00", "departure_time": "08:15"},
    {"station_id": 2, "arrival_time": "09:00", "departure_time": "09:15"}
  ]
}
```
**Response:**
- **201 Created**
  ```json
  {
    "message": "Train and stops added successfully"
  }
  ```

---

#### **PUT /trains/<train_id>/stops/<stop_id>**  
**Description:** Update a stop's details for a specific train.  
**Method:** `PUT`  
**Path:** `/trains/<train_id>/stops/<stop_id>`  
**Request Header:**
```
Authorization: Bearer <your_token>
Content-Type: application/json
```
**Request Body:**
```json
{
  "arrival_time": "10:00",
  "departure_time": "10:15"
}
```
**Response:**
- **200 OK**
  ```json
  {
    "message": "Train stop updated successfully"
  }
  ```
- **400 Bad Request**
  ```json
  {
    "message": "No valid fields provided for update"
  }
  ```

---

#### **GET /trains**  
**Description:** Retrieve all train schedules.  
**Method:** `GET`  
**Path:** `/trains`  
**Response:**
- **200 OK**
  ```json
  [
    {
      "id": 1,
      "name": "Express Train",
      "description": "Fast train from A to B",
      "stops": [
        {"station_id": 1, "station_name": "Station A", "arrival_time": "08:00", "departure_time": "08:15"},
        {"station_id": 2, "station_name": "Station B", "arrival_time": "09:00", "departure_time": "09:15"}
      ]
    }
  ]
  ```

---

### **4. Ticket Management**  

#### **POST /tickets/purchase**  
**Description:** Purchase a ticket.  
**Method:** `POST`  
**Path:** `/tickets/purchase`  
**Request Header:**
```
Authorization: Bearer <your_token>
Content-Type: application/json
```
**Request Body:**
```json
{
  "train_id": 1,
  "from_station": "Station A",
  "to_station": "Station B",
  "price": 200
}
```
**Response:**
- **201 Created**
  ```json
  {
    "message": "Ticket purchased successfully"
  }
  ```
- **400 Bad Request**
  ```json
  {
    "message": "Insufficient funds"
  }
  ```

---

### **5. Wallet Management**  

#### **POST /wallet/add**  
**Description:** Add funds to the user’s wallet.  
**Method:** `POST`  
**Path:** `/wallet/add`  
**Request Header:**
```
Authorization: Bearer <your_token>
Content-Type: application/json
```
**Request Body:**
```json
{
  "amount": 500
}
```
**Response:**
- **200 OK**
  ```json
  {
    "message": "Funds added successfully"
  }
  ```

---

#### **GET /wallet/history**  
**Description:** Retrieve transaction history.  
**Method:** `GET`  
**Path:** `/wallet/history`  
**Request Header:**
```
Authorization: Bearer <your_token>
```
**Response:**
- **200 OK**
  ```json
  [
    {"amount": 500, "type": "add", "timestamp": "2024-10-18 12:00:00"},
    {"amount": 200, "type": "deduct", "timestamp": "2024-10-18 12:15:00"}
  ]
  ```

---

## **Error Codes**  
| **Status Code** | **Description**                         |
|-----------------|-----------------------------------------|
| 200 OK          | Request completed successfully          |
| 201 Created     | Resource created successfully           |
| 400 Bad Request | Invalid data or missing fields          |
| 401 Unauthorized| Authentication failed                   |
| 409 Conflict    | Resource already exists                 |

