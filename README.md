# Secure File Sharing System

A secure file sharing system with two user types (Operations and Client) built with FastAPI and MongoDB.

## Features

- **User Authentication**:
  - User registration with email verification
  - JWT-based authentication
  - Role-based access control (Operations and Client users)

- **File Operations**:
  - File upload (Operations users only)
  - File listing (Client users)
  - Secure file download with encrypted URLs (Client users)

- **Security**:
  - Password hashing with bcrypt
  - JWT token-based authentication
  - Encrypted download URLs
  - Email verification

## Tech Stack

- **Backend**: 
  - [FastAPI](https://fastapi.tiangolo.com/) - High-performance Python web framework
  - [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation and settings management
  - [Python-Jose](https://github.com/mpdavis/python-jose) - JavaScript Object Signing and Encryption for JWT
  - [Passlib](https://passlib.readthedocs.io/) - Password hashing library
  - [PyMongo/Motor](https://motor.readthedocs.io/) - Asynchronous MongoDB driver

- **Database**:
  - [MongoDB](https://www.mongodb.com/) - NoSQL document database

- **Security**:
  - [Bcrypt](https://github.com/pyca/bcrypt/) - Password hashing
  - [Cryptography](https://cryptography.io/) - Cryptographic recipes and primitives

- **Utilities**:
  - [Python-dotenv](https://github.com/theskumar/python-dotenv) - Environment variable management
  - [Uvicorn](https://www.uvicorn.org/) - ASGI server

## Prerequisites

- Python 3.7+
- MongoDB installed and running on localhost:27017
- SMTP server for sending emails (or use a service like Mailtrap for testing)

## Project Structure

```
app/
├── api/
│   └── endpoints/
│       ├── auth.py     # Authentication endpoints
│       └── files.py    # File operation endpoints
├── core/
│   ├── config.py       # Application configuration
│   └── security.py     # Security utilities
├── db/
│   └── database.py     # Database operations
├── models/
│   └── user.py         # Pydantic models
├── utils/
│   └── email.py        # Email utilities
└── main.py             # FastAPI application
```

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd secure-file-sharing
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables (create a .env file):
```
# MongoDB settings
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=file_sharing_db
COLLECTION_NAME=users

# JWT settings
SECRET_KEY=your-secret-key-keep-it-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email settings
MAIL_USERNAME=example@gmail.com
MAIL_FROM=noreply@example.com
MAIL_PASSWORD=your-email-password
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_TLS=true
MAIL_SSL=false

# Development settings
DEV_MODE=false
BYPASS_EMAIL_VERIFICATION=false

# File storage settings
MAX_FILE_SIZE=52428800
ALLOWED_EXTENSIONS=pptx,docx,xlsx
```

4. Run the application:
```bash
python run.py
```

The API will be available at `http://127.0.0.1:8000`

## API Endpoints

### Authentication

- **POST /auth/signup**: Register a new user (defaults to Client type)
  - Request Body:
    ```json
    {
      "username": "username",
      "email": "user@example.com",
      "password": "password123"
    }
    ```

- **GET /auth/verify**: Verify email address
  - Query Parameters:
    - `email`: User's email
    - `token`: Verification token sent to email

- **POST /auth/login**: Login and get access token
  - Request Body:
    ```json
    {
      "email": "user@example.com",
      "password": "password123"
    }
    ```

### Files

- **POST /files/upload**: Upload a file (Operations users only)
  - Request: Form data with file
  - Supported file types: pptx, docx, xlsx

- **GET /files/list**: List all available files (Client users only)

- **GET /files/download/{file_id}**: Get secure download URL for a file (Client users only)

- **GET /files/secure-download**: Download a file using a secure token
  - Query Parameters:
    - `token`: Encrypted download token

## User Types

1. **Operations User**:
   - Can upload files (pptx, docx, xlsx only)
   - Can download files using secure URLs

2. **Client User**:
   - Cannot upload files
   - Can list all available files
   - Can download files using secure URLs

## Security Notes

- In production, replace the `SECRET_KEY` with a secure secret key
- Configure proper CORS settings in production
- Use HTTPS in production
- Set up proper email server configuration
- Consider implementing rate limiting for API endpoints

## API Documentation

Once the server is running, you can access:
- Interactive API documentation at: `http://localhost:8000/docs`
- Alternative API documentation at: `http://localhost:8000/redoc` 

## Default Users

The application automatically creates the following default users for testing purposes:

### Operations Users
These users have privileges to upload files and download files.

1. **ops_admin1**
   - Email: ops_admin1@example.com
   - Password: password123
   - Type: Operations

2. **ops_admin2**
   - Email: ops_admin2@example.com
   - Password: password123
   - Type: Operations

### Client Users
No default client users are pre-created. You can register new client users through the signup endpoint.

> **Note**: In a production environment, you should remove or change these default accounts for security reasons. 