# Wikipedia Book API

This is a REST API for accessing book data extracted from Wikipedia. The API provides endpoints for retrieving paginated results and performing fuzzy searches based on various book properties.

## Endpoints

### GET /all
Retrieves all books in paginated form.

- **Query Parameters:**
  - `limit` (optional, default: 100): Number of books per page.
  - `page` (optional, default: 1): Page number.

**Example:**  
`/all?page=1&limit=100`

### GET /search
Performs a fuzzy search on the books based on one or more of the following fields:
- `name`
- `author`
- `language`
- `genre`
- `publisher`
- `release_date`
- `media_type`
- `pages`
- `isbn`

Search is case-insensitive and matches any part of the field.

**Examples:**  
`/search?name=harry`  
`/search?author=tolkien&language=english`

## Running the API

1. Create a virtual environment and install dependencies:
   ```
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Run the API:
   ```
   python api.py
   ```
   The API will be available at [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Testing

Run the tests using:
```
python -m unittest test_api.py
```

## Deployment

This project is ready for deployment on hosting platforms such as [Render](https://render.com) or [Koyeb](https://www.koyeb.com).

Ensure that the following recommended files are included in your deployment:
- `api.py`
- `requirements.txt`
- `test_api.py`
- `data/found_books_filtered.ndjson`
- `.gitignore`

Exclude development-only files and directories such as `notebooks` and internal planning documents.
