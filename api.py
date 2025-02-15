from flask import Flask, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from flask_caching import Cache
import json
import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from functools import wraps

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure logging
if not os.path.exists('logs'):
    os.makedirs('logs')
file_handler = RotatingFileHandler('logs/api.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('API startup')

# Initialize CORS
CORS(app)

# Initialize Caching
cache_config = {
    "CACHE_TYPE": os.getenv("CACHE_TYPE", "simple"),
    "CACHE_DEFAULT_TIMEOUT": int(os.getenv("CACHE_DEFAULT_TIMEOUT", 300))
}
cache = Cache(app, config=cache_config)

# Initialize Rate Limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[f"{os.getenv('RATE_LIMIT', '100')}/day"],
    storage_uri="memory://"
)

# Security headers middleware
@app.after_request
def add_security_headers(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

# Error handling decorator
def handle_errors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            app.logger.error(f'Error: {str(e)}')
            return jsonify({'error': 'Internal server error'}), 500
    return wrapper

# Swagger documentation
SWAGGER_DOC = {
    "openapi": "3.0.0",
    "info": {
        "title": "Wikipedia Book API",
        "description": "API for accessing and searching Wikipedia book data",
        "version": "1.0.0"
    },
    "paths": {
        "/health": {
            "get": {
                "summary": "Health check endpoint",
                "responses": {
                    "200": {
                        "description": "API is healthy",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string"},
                                        "version": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/all": {
            "get": {
                "summary": "Get all books with pagination",
                "parameters": [
                    {
                        "name": "limit",
                        "in": "query",
                        "description": "Number of books per page",
                        "schema": {"type": "integer", "default": 100}
                    },
                    {
                        "name": "page",
                        "in": "query",
                        "description": "Page number",
                        "schema": {"type": "integer", "default": 1}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "books": {"type": "array"},
                                        "total": {"type": "integer"},
                                        "page": {"type": "integer"},
                                        "limit": {"type": "integer"},
                                        "total_pages": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/search": {
            "get": {
                "summary": "Search books by various fields",
                "parameters": [
                    {
                        "name": "name",
                        "in": "query",
                        "description": "Book name",
                        "schema": {"type": "string"}
                    },
                    {
                        "name": "author",
                        "in": "query",
                        "description": "Author name",
                        "schema": {"type": "string"}
                    },
                    {
                        "name": "language",
                        "in": "query",
                        "description": "Book language",
                        "schema": {"type": "string"}
                    },
                    {
                        "name": "genre",
                        "in": "query",
                        "description": "Book genre",
                        "schema": {"type": "string"}
                    },
                    {
                        "name": "publisher",
                        "in": "query",
                        "description": "Publisher name",
                        "schema": {"type": "string"}
                    },
                    {
                        "name": "release_date",
                        "in": "query",
                        "description": "Release date",
                        "schema": {"type": "string"}
                    },
                    {
                        "name": "media_type",
                        "in": "query",
                        "description": "Media type",
                        "schema": {"type": "string"}
                    },
                    {
                        "name": "pages",
                        "in": "query",
                        "description": "Number of pages",
                        "schema": {"type": "string"}
                    },
                    {
                        "name": "isbn",
                        "in": "query",
                        "description": "ISBN",
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "books": {"type": "array"},
                                        "total": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Invalid request",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

@app.route('/swagger.json')
def swagger():
    return jsonify(SWAGGER_DOC)

# Initialize Swagger UI
SWAGGER_URL = '/docs'
API_URL = '/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Wikipedia Book API"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Load and parse the NDJSON file
books = []
data_file = os.getenv('DATA_FILE', 'data/found_books_filtered.ndjson')

try:
    with open(data_file, 'r', encoding='utf-8') as f:
        for line in f:
            book_data = json.loads(line)[1]  # Get the second element (book data)
            # Extract relevant fields
            book = {
                'name': book_data.get('name', ''),
                'author': book_data.get('author', ''),
                'language': book_data.get('language', ''),
                'genre': book_data.get('genre', ''),
                'publisher': book_data.get('publisher', ''),
                'release_date': book_data.get('release_date', ''),
                'media_type': book_data.get('media_type', ''),
                'pages': book_data.get('pages', ''),
                'isbn': book_data.get('isbn', '')
            }
            books.append(book)
    app.logger.info(f'Successfully loaded {len(books)} books from {data_file}')
except Exception as e:
    app.logger.error(f'Error loading books: {str(e)}')
    books = []

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0'
    })

@app.route('/all')
@limiter.limit("100/day")
@cache.cached(timeout=300)
@handle_errors
def get_all_books():
    limit = request.args.get('limit', default=100, type=int)
    page = request.args.get('page', default=1, type=int)
    
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    
    paginated_books = books[start_idx:end_idx]
    
    return jsonify({
        'books': paginated_books,
        'total': len(books),
        'page': page,
        'limit': limit,
        'total_pages': (len(books) + limit - 1) // limit
    })

@app.route('/search')
@limiter.limit("200/day")
@handle_errors
def search_books():
    query_params = request.args.to_dict()
    
    if not query_params:
        return jsonify({'error': 'No search parameters provided'}), 400
    
    filtered_books = books
    for field, value in query_params.items():
        if field not in books[0].keys():
            app.logger.warning(f'Invalid search field attempted: {field}')
            return jsonify({'error': f'Invalid field: {field}'}), 400
            
        # Case-insensitive substring search
        filtered_books = [
            book for book in filtered_books 
            if str(value).lower() in str(book[field]).lower()
        ]
    
    return jsonify({
        'books': filtered_books,
        'total': len(filtered_books)
    })

if __name__ == '__main__':
    # Use environment variable for port with a default of 8080
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)