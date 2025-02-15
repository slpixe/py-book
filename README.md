# Wikipedia Book API

A production-ready REST API for accessing and searching Wikipedia book data.

## Features

- RESTful API endpoints for book data
- OpenAPI/Swagger documentation
- Pagination support
- Advanced search functionality
- Rate limiting
- Response caching
- CORS support
- Security headers
- Health check endpoint
- Logging system
- Environment-based configuration
- Production-ready error handling

## Requirements

- Python 3.8+
- pip (Python package installer)

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Copy .env.example to .env and configure your environment variables:
```bash
cp .env.example .env
```
4. Edit .env with your specific configuration

## Environment Variables

- `FLASK_ENV`: Set to 'production' for production environment
- `FLASK_APP`: Application entry point (default: api.py)
- `SECRET_KEY`: Secret key for Flask session security
- `RATE_LIMIT`: API rate limit per day (default: 100)
- `CACHE_TYPE`: Cache backend type (default: simple)
- `CACHE_DEFAULT_TIMEOUT`: Cache timeout in seconds (default: 300)
- `DATA_FILE`: Path to the NDJSON data file
- `PORT`: Port to run the application (default: 8080)

## API Endpoints

- `GET /health`: Health check endpoint
- `GET /docs`: Swagger UI documentation
- `GET /all`: Get all books with pagination
  - Query params: limit (default: 100), page (default: 1)
- `GET /search`: Search books by various fields
  - Query params: name, author, language, genre, publisher, release_date, media_type, pages, isbn

## Running in Production

1. Ensure all environment variables are properly configured in .env
2. Run using Gunicorn:
```bash
gunicorn api:app
```

## Security Features

- HTTPS enforcement through HSTS headers
- XSS protection headers
- Content type sniffing prevention
- Clickjacking protection
- Rate limiting per IP
- Secure error handling

## Monitoring

- Request logging to rotating log files in ./logs/
- Health check endpoint for uptime monitoring
- Error tracking and logging

## Caching

The API implements caching for the following endpoints:
- `/all` endpoint: 5-minute cache
- Configurable cache backend through CACHE_TYPE environment variable

## Rate Limiting

- `/all` endpoint: 100 requests per day per IP
- `/search` endpoint: 200 requests per day per IP
- Configurable through RATE_LIMIT environment variable

## Deployment

The application is configured for deployment on Heroku or similar platforms using Gunicorn.
A Procfile is included for Heroku deployment.

## Testing

To run the tests:
```bash
pytest test_api.py
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
