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
import requests

# Constants for LFS
LFS_URL = "https://github.com/slpixe/py-book/raw/refs/heads/master/data/found_books_filtered.ndjson"

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

# Request logging decorator
def log_request(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        app.logger.info(f'Request to {request.path} with params: {request.args}')
        return f(*args, **kwargs)
    return wrapper

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
    "components": {
        "schemas": {
            "Book": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Book name"},
                    "author": {"type": "string", "description": "Author name"},
                    "language": {"type": "string", "description": "Book language"},
                    "genre": {"type": "string", "description": "Book genre"},
                    "publisher": {"type": "string", "description": "Publisher name"},
                    "release_date": {"type": "string", "description": "Release date"},
                    "media_type": {"type": "string", "description": "Media type"},
                    "pages": {"type": "string", "description": "Number of pages"},
                    "isbn": {"type": "string", "description": "ISBN"}
                }
            }
        }
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
                                        "books": {
                                            "type": "array",
                                            "items": {
                                                "$ref": "#/components/schemas/Book"
                                            }
                                        },
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
                                        "books": {
                                            "type": "array",
                                            "items": {
                                                "$ref": "#/components/schemas/Book"
                                            }
                                        },
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
def load_books_data():
    """Load books from data file, handling LFS pointer files if necessary"""
    global books
    data_file = os.getenv('DATA_FILE', 'data/found_books_filtered.ndjson')
    books = []
    
    app.logger.info(f'Attempting to load books from: {data_file}')
    
    # Check if file exists
    if not os.path.exists(data_file):
        app.logger.error(f'Database file not found: {data_file}')
        return False
    
    # Check if file is a Git LFS pointer file
    try:
        with open(data_file, 'r') as f:
            content = f.read().strip()
            if content.startswith('version https://git-lfs'):
                app.logger.info('Found LFS pointer file, downloading actual content...')
                response = requests.get(LFS_URL, stream=True)
                response.raise_for_status()
                
                with open(data_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                app.logger.info('Successfully downloaded actual content from LFS')
                # After downloading LFS content, we need to parse it
                return load_books_data()  # Recursively load books from downloaded content
    except Exception as e:
        app.logger.error(f'Error checking/downloading file: {str(e)}')
        return False
    
    # Load the books data
    try:
        loaded_books = []  # Use a local list first
        with open(data_file, 'r', encoding='utf-8') as f:
            app.logger.info('Successfully opened database file, parsing content...')
            line_count = 0
            error_count = 0
            for line in f:
                try:
                    line_count += 1
                    parsed_line = json.loads(line)
                    if not isinstance(parsed_line, list) or len(parsed_line) < 2:
                        app.logger.warning(f'Invalid data format at line {line_count}: Expected list with at least 2 elements')
                        error_count += 1
                        continue
                    
                    book_data = parsed_line[1]  # Get the second element (book data)
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
                    loaded_books.append(book)
                except (json.JSONDecodeError, IndexError) as e:
                    app.logger.error(f'Error parsing line {line_count}: {str(e)}')
                    error_count += 1
                    continue
            
            app.logger.info(f'Finished processing {line_count} lines with {error_count} errors')
            app.logger.info(f'Found {len(loaded_books)} valid books to load')
            
            if loaded_books:
                # Only update the global books list if we successfully loaded data
                app.logger.info('Updating global books list...')
                books.clear()
                books.extend(loaded_books)
                app.logger.info(f'Successfully loaded {len(books)} books from {data_file}')
                
                # Double check the books were actually loaded
                if not books:
                    app.logger.error('Books list is empty after update!')
                    return False
                return True
            else:
                app.logger.warning('No valid books were loaded from the file')
                return False
    except Exception as e:
        app.logger.error(f'Error reading database file: {str(e)}')
        return False

# Initialize books and load data at startup
books = []
if not load_books_data():
    app.logger.error('Failed to initialize books data')

@app.route('/health')
@limiter.exempt
def health_check():
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'books_loaded': len(books)
    })

@app.route('/all')
@limiter.limit("100/day")
@cache.cached(timeout=300, key_prefix=lambda: f"all_books_{request.args.get('page', 1)}_{request.args.get('limit', 100)}")
@handle_errors
@log_request
def get_all_books():
    limit = request.args.get('limit', default=100, type=int)
    page = request.args.get('page', default=1, type=int)
    
    if not books:
        app.logger.error('No books available in the database')
        return jsonify({'error': 'No books available'}), 500
    
    # Ensure limit is positive and within bounds
    if limit < 1:
        limit = 100
    
    # Validate page number
    total_pages = (len(books) + limit - 1) // limit
    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages
    
    # Calculate slice indices
    start_idx = (page - 1) * limit
    end_idx = min(start_idx + limit, len(books))  # Don't exceed array bounds
    
    # Get exactly 'limit' number of items
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
@log_request
def search_books():
    query_params = request.args.to_dict()
    
    if not query_params:
        app.logger.warning('Search attempted with no parameters')
        return jsonify({'error': 'No search parameters provided'}), 400
    
    if not books:
        app.logger.error('Search attempted but no books available in the database')
        return jsonify({'error': 'No books available'}), 500
    
    app.logger.info(f'Starting search with parameters: {query_params}')
    
    try:
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
            app.logger.info(f'After filtering by {field}={value}: {len(filtered_books)} books remaining')
        
        if not filtered_books:
            app.logger.info('Search returned no results')
        else:
            app.logger.info(f'Search completed successfully with {len(filtered_books)} results')
        
        return jsonify({
            'books': filtered_books,
            'total': len(filtered_books)
        })
    except Exception as e:
        app.logger.error(f'Error during search: {str(e)}')
        return jsonify({'error': 'Internal server error during search'}), 500

if __name__ == '__main__':
    # Use environment variable for port with a default of 8080
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)