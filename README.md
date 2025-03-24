# Visibrain Project

A FastAPI-based backend application for Twitch integration.

## Project Structure

```
visibrain_projet/
├── backend/
│   └── app/
│       ├── config/           # Configuration files for different environments
│       ├── models/           # Data models and schemas
│       ├── repositories/     # Database access layer
│       ├── services/         # Business logic layer
│       └── routes/           # API endpoints
├── tests/                   # Test files
└── frontend/               # Frontend application (to be implemented)
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r backend/requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with:
```
CLIENT_ID=your_twitch_client_id
CLIENT_SECRET=your_twitch_client_secret
REDIRECT_URI=your_redirect_uri
MONGODB_URI=your_mongodb_uri
SESSION_SECRET_KEY=your_session_secret
```

4. Run the application:
```bash
uvicorn backend.app.main:app --reload
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

- Backend: FastAPI
- Database: MongoDB
- Authentication: Twitch OAuth2
- Caching: cachetools

## Testing

Run tests with:
```bash
pytest
``` 