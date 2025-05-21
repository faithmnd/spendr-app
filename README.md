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

License  
This project is licensed under the MIT License.

Contact  
For questions, reach me at 202210280@gordoncollege.edu.ph
