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

### Required for Production

These environment variables MUST be set in your production environment:

- `PORT`: Port the application will listen on (usually 80 for production)
- `FLASK_ENV`: Must be set to 'production'
- `FLASK_APP`: Must be set to 'api.py'

### Optional Configuration

- `RATE_LIMIT`: API rate limit per day (default: 100)
- `CACHE_TYPE`: Cache backend type (default: simple)
- `CACHE_DEFAULT_TIMEOUT`: Cache timeout in seconds (default: 300)
- `DATA_FILE`: Path to the NDJSON data file (default: data/found_books_filtered.ndjson)

## API Endpoints

- `GET /health`: Health check endpoint
- `GET /docs`: Swagger UI documentation
- `GET /all`: Get all books with pagination
  - Query params: limit (default: 100), page (default: 1)
- `GET /search`: Search books by various fields
  - Query params: name, author, language, genre, publisher, release_date, media_type, pages, isbn

## Production Deployment

### Required Setup

The application is configured to run with gunicorn in production as specified in the Procfile:
```bash
web: gunicorn api:app
```

### Platform-Specific Instructions

#### Render

The application includes a `render.yaml` configuration file that specifies:
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn api:app`
- Runtime: Python
- Environment variables setup

To deploy on Render:
1. Connect your repository to Render
2. Render will automatically detect the `render.yaml` configuration
3. Deploy the application

The application will automatically:
- Use Python runtime
- Run in production mode
- Listen on port 80
- Use the correct FLASK_APP setting

#### Heroku

1. Set the environment variables:
```bash
heroku config:set FLASK_ENV=production
heroku config:set FLASK_APP=api.py
```

2. Deploy your application:
```bash
git push heroku main
```

#### Docker

1. Build the image:
```bash
docker build -t wikipedia-book-api .
```

2. Run the container:
```bash
docker run -p 80:80 \
  -e PORT=80 \
  -e FLASK_ENV=production \
  -e FLASK_APP=api.py \
  wikipedia-book-api
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
