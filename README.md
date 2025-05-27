# Spendr

Spendr is a personal wallet app backend built with Django and Django REST Framework. This repo contains the backend API with user authentication implemented via JWT tokens.

Project Setup

Prerequisites
- Python 3.8+
- python -m pip
- virtualenv

Installation steps

1. Clone the repo:
   git clone https://github.com/faithmnd/spendr-app.git
   cd backend

2. Create and activate a virtual environment:
   python -m venv env
   env\Scripts\activate

3. Install dependencies:
   python -m pip install -r requirements.txt

4. Run migrations:
   python manage.py migrate

5. Run the server:
   python manage.py runserver

User Authentication API

Register User  
a. Method: POST  
b. Endpoint URL: /api/register/  
c. Expected request body:
{
  "username": "string",
  "password": "string"
}
Headers: Content-Type: application/json  
d. Sample response:
{
  "id": 1,
  "username": "string"
}

Login User  
a. Method: POST  
b. Endpoint URL: /api/login/  
c. Expected request body:
{
  "username": "string",
  "password": "string"
}
Headers: Content-Type: application/json  
d. Sample response:
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}

Refresh Token  
a. Method: POST  
b. Endpoint URL: /api/token/refresh/  
c. Expected request body:
{
  "refresh": "refresh_token"
}
Headers: Content-Type: application/json  
d. Sample response:
{
  "access": "access_token"
}

Access Protected Route  
a. Method: GET  
b. Endpoint URL: /api/protected/  
c. Expected headers: Authorization: Bearer <access_token>  
d. Sample response:
{
  "message": "Hey username, you got access to this protected route."
}

Notes  
- Passwords are securely hashed before storage and never returned by the API.  
- All requests and responses use JSON format.  
- Include the JWT access token in the Authorization header for protected routes.  
- Proper error handling is in place; invalid credentials or unauthorized access attempts return appropriate HTTP status codes.

CRUD Operations API

All CRUD endpoints require the Authorization header with a valid JWT access token:  
Authorization: Bearer <access_token>

Accounts  
- List accounts  
  Method: GET  
  Endpoint: /api/accounts/  
  Headers: Authorization  
  Response:  
  [  
    { "id": 1, "name": "Main Wallet", "balance": "1000.00" },  
    ...  
  ]

- Retrieve account  
  Method: GET  
  Endpoint: /api/accounts/{id}/  
  Headers: Authorization  
  Response:  
  { "id": 1, "name": "Main Wallet", "balance": "1000.00" }

- Create account  
  Method: POST  
  Endpoint: /api/accounts/  
  Headers: Authorization, Content-Type: application/json  
  Body:  
  { "name": "New Wallet", "balance": "500.00" }  
  Response:  
  { "id": 2, "name": "New Wallet", "balance": "500.00" }

- Update account  
  Method: PUT / PATCH  
  Endpoint: /api/accounts/{id}/  
  Headers: Authorization, Content-Type: application/json  
  Body:  
  { "name": "Updated Wallet", "balance": "600.00" }  
  Response: Updated account object

- Delete account  
  Method: DELETE  
  Endpoint: /api/accounts/{id}/  
  Headers: Authorization  
  Response: HTTP 204 No Content

Repeat same patterns for Categories (/api/categories/) and Transactions (/api/transactions/)

Error handling  
- 401 Unauthorized if no/invalid token  
- 404 Not Found if resource does not exist  
- 400 Bad Request for invalid input  

Rate Limiting
Test Rate-Limited Endpoint

Method: GET

URL: /test-rate/

Headers: None

Request Body: None

Sample Success Response:
{
  "message": "This endpoint is rate-limited"
}

Sample Rate Limit Exceeded Response:
{
  "detail": "Rate limit exceeded. Try again later."
}

Status Code: 429 Too Many Requests

License  
This project is licensed under the MIT License.

Contact  
For questions, reach me at 202210280@gordoncollege.edu.ph

