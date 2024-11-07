# Patlytics API

A RESTful API service built with Flask for patent analysis system.

## Requirements

- Python 3.11
- Docker
- AWS Credentials

## Quick Start

1. Set AWS credentials environment variables:
> **Note**: The API currently uses personal AWS credentials for development. You can either:
> - Contact hsps955201@gmail.com for development credentials
> - Access the API directly at: http://xxxxx
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
```

2. Run with Docker:
```bash
# Build image
docker build -t patlytics-api .

# Run container
docker run -p 5001:5001 patlytics-api
```

The service will be running at http://localhost:5001

## API Endpoints

### Authentication (/api/auth)

#### Register
```http
POST /api/auth/register
Content-Type: application/json

Request:
{
    "email": "user@example.com",
    "password": "password"
}

Response:
{
    "success": true,
    "message": "User registered successfully"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

Request:
{
    "email": "user@example.com",
    "password": "password"
}

Response:
{
    "success": true,
    "data": {
        "token": "eyJhbGciOiJIUzI1..."
    }
}
```

#### Get Current User Info
```http
GET /api/auth/me
Headers: 
    Authorization: Bearer <token>

Response:
{
    "success": true,
    "data": {
        "user": {
            "id": 1,
            "email": "user@example.com"
        }
    }
}
```

#### Refresh Token
```http
POST /api/auth/refresh
Headers: 
    Authorization: Bearer <token>

Response:
{
    "success": true,
    "data": {
        "access_token": "eyJhbGciOiJIUzI1..."
    }
}
```

### Patent Analysis (/api/patent)

#### Check Infringement
```http
POST /api/patent/infringements
Headers: 
    Authorization: Bearer <token>
Content-Type: application/json

Request:
{
    // Patent infringement check parameters
}

Response:
{
    "success": true,
    "data": {
        // Infringement analysis results
    }
}
```

## Project Structure
```
.
├── app.py              # Application entry point
├── config/            # Configuration files
├── patlytics/         # Main application code
│   ├── auth/         # Authentication related code
│   ├── patent/       # Patent analysis related code
│   └── utils/        # Utility functions
├── migrations/        # Database migrations
├── data/             # Data files
├── aws/              # AWS configuration templates
└── requirements.txt   # Python dependencies
```

## Environment Variables

### AWS Configuration
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_DEFAULT_REGION`: AWS region (default: ap-northeast-1)

### Database Configuration
- `DB_HOST`: Database host
- `DB_PORT`: Database port
- `DB_USER`: Database user
- `DB_PWD`: Database password
- `DB_NAME`: Database name

### OpenSearch Configuration
- `OS_HOST`: OpenSearch host
- `OS_PORT`: OpenSearch port
- `OS_USER`: OpenSearch user
- `OS_PWD`: OpenSearch password

### Application Configuration
- `SECRET_KEY`: Application secret key for JWT

## Development

To run the application in development mode:

1. Clone the repository
2. Set up environment variables
3. Build and run with Docker

## Error Responses

All endpoints may return the following error responses:

```http
400 Bad Request
{
    "success": false,
    "message": "Invalid request parameters"
}

401 Unauthorized
{
    "success": false,
    "message": "Invalid token"
}

403 Forbidden
{
    "success": false,
    "message": "Access denied"
}

500 Internal Server Error
{
    "success": false,
    "message": "Internal server error"
}
```

## Testing

To run tests:
```bash
python -m pytest --cov=patlytics --cov-report=term-missing
```

## License

MIT License