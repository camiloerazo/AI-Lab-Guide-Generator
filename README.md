# Flask Application

A simple Flask web application with SQLAlchemy integration.

## Setup

1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your web browser and visit: `http://localhost:5000`

## Project Structure

- `app.py` - Main application file with Flask and SQLAlchemy setup
- `requirements.txt` - Project dependencies
- `templates/` - Directory containing HTML templates
  - `index.html` - Main template file
- `site.db` - SQLite database file (created automatically on first run)

## Features

- Basic Flask setup
- SQLAlchemy integration with SQLite database
- User model with username, email, and creation timestamp
- Simple routing
- Template rendering
- Modern, responsive design
- Debug mode enabled for development

## Database

The application uses SQLAlchemy with SQLite as the database backend. The database file (`site.db`) will be created automatically when you first run the application.

### Models

- `User`: A basic user model with the following fields:
  - `id`: Primary key
  - `username`: Unique username (80 characters max)
  - `email`: Unique email address (120 characters max)
  - `created_at`: Timestamp of user creation

## Note

This project is set up without a virtual environment. Make sure you have Python installed on your system and that you're comfortable with installing packages globally. 