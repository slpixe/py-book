from flask import Flask, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
import json
import os

app = Flask(__name__)

# Swagger documentation
SWAGGER_DOC = {
    "openapi": "3.0.0",
    "info": {
        "title": "Wikipedia Book API",
        "description": "API for accessing and searching Wikipedia book data",
        "version": "1.0.0"
    },
    "paths": {
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
from flask_swagger_ui import get_swaggerui_blueprint

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
with open('data/found_books_filtered.ndjson', 'r', encoding='utf-8') as f:
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

@app.route('/all')
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
def search_books():
    query_params = request.args.to_dict()
    
    if not query_params:
        return jsonify({'error': 'No search parameters provided'}), 400
    
    filtered_books = books
    for field, value in query_params.items():
        if field not in books[0].keys():
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