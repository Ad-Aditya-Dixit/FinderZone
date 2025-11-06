# FinderZone — Lost & Found Portal (Simple Flask App)

This is a minimal Lost & Found portal built with Flask. It allows users to:
- Report a lost or found item with a photo.
- View all reported items with basic search and filter.
- Upload and serve item images.

## Prerequisites
- Python 3.8+ installed.
- VS Code (optional) with Python extension recommended.

## How to run (step-by-step) in VS Code

1. Open VS Code, then open the folder `lost_and_found_portal` (File → Open Folder...).

2. Create and activate a virtual environment (recommended).
   - On Windows (PowerShell):
     ```
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - On Windows (cmd):
     ```
     python -m venv venv
     venv\Scripts\activate
     ```
   - On macOS / Linux:
     ```
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Initialize the app database (the app will auto-create `items.db` on first run).
   No extra command required.

5. Run the Flask app:
   ```
   # Unix/macOS
   export FLASK_APP=app.py
   export FLASK_ENV=development
   flask run --host=0.0.0.0 --port=5000

   # Windows (cmd)
   set FLASK_APP=app.py
   set FLASK_ENV=development
   flask run

   # Or simply:
   python app.py
   ```

6. Open your browser and go to `http://127.0.0.1:5000/` to use FinderZone.

## Project structure
- app.py           -> Main Flask application
- forms.py         -> WTForms definitions
- templates/       -> HTML templates (Jinja2)
- static/css/      -> Styling
- static/uploads/  -> Uploaded photos (created automatically)
- requirements.txt -> Python dependencies
- README.md        -> This file

## Notes & Next steps
- This is a simple starting project. For production, add:
  - User authentication
  - Input validation & sanitization
  - CSRF protection (Flask-WTF included)
  - Image size/format checks
  - Pagination and search indexing
