# Brain Vibe Backend

This is the backend API for the Brain Vibe project, built with Django and Django REST Framework.

## Setup

1. Ensure you have Python 3.8+ and PostgreSQL installed
2. Create a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up PostgreSQL database:
   - Create a database named `brain_vibe_db`
   - Update credentials in `core/settings.py` if needed
5. Run migrations:
   ```
   python3 manage.py migrate
   ```
6. Run the development server:
   ```
   python3 manage.py runserver
   ```

## Project Structure

- `core/` - Main Django project settings
- `main/` - Primary application for Brain Vibe functionality
  - `models.py` - Data models (Projects, Topics, etc.)
  - `views.py` - API endpoints
  - `serializers.py` - JSON serializers for models
  - `urls.py` - URL routing

## API Endpoints

- `/api/hello/` - Test endpoint
- `/admin/` - Django admin interface
- `/api-auth/` - DRF authentication
- `/docs/` - API documentation

## Future Development

The system is designed to be easily extended with additional apps, models, and endpoints. 