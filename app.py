import os
import sqlite3
import time
import base64
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename
from forms import ReportForm
from ultralytics import YOLO
from PIL import Image

# ---------------- CONFIGURATION ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
DB_PATH = os.path.join(BASE_DIR, 'items.db')
ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'  # change this in production
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB limit

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------- HELPER FUNCTIONS ----------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        category TEXT,
        status TEXT,
        image_filename TEXT,
        latitude TEXT,
        longitude TEXT,
        location_name TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()


# ---------------- ROUTES ----------------
@app.route('/')
def index():
    q = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    query = """SELECT id, title, description, category, status, image_filename,
                      latitude, longitude, location_name, created_at
               FROM items WHERE 1=1"""
    params = []
    if q:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params += [f'%{q}%', f'%{q}%']
    if category:
        query += " AND category = ?"
        params.append(category)
    query += " ORDER BY created_at DESC"
    c.execute(query, params)
    items = c.fetchall()
    conn.close()
    return render_template('index.html', items=items, q=q, category=category)


@app.route('/report', methods=['GET', 'POST'])
def report():
    form = ReportForm()
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        category = form.category.data
        status = form.status.data
        image_filename = None

        # --- CAMERA IMAGE HANDLING + OBJECT DETECTION ---
        camera_image_data = request.form.get('captured_image')
        if camera_image_data:
            try:
                image_data = base64.b64decode(camera_image_data.split(',')[1])
                filename = f"camera_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                with open(file_path, 'wb') as f:
                    f.write(image_data)
                image_filename = filename

                # Run YOLO object detection
                model = YOLO("yolov8n.pt")  # lightweight model
                results = model(file_path)
                detected_objects = set()

                for r in results:
                    boxes = r.boxes
                    for cls_id in boxes.cls:
                        detected_objects.add(model.names[int(cls_id)])

                if detected_objects:
                    flash(f"Detected objects: {', '.join(detected_objects)}")
                else:
                    flash("No recognizable objects detected.")
            except Exception as e:
                flash(f"Error processing camera image: {e}")
                return redirect(request.url)

        # --- FILE UPLOAD HANDLING ---
        else:
            file = request.files.get('image')
            if file and file.filename != '':
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    base, ext = os.path.splitext(filename)
                    filename = f"{base}_{int(time.time())}{ext}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    image_filename = filename
                else:
                    flash('File type not allowed. Please upload png/jpg/jpeg/gif.')
                    return redirect(request.url)

        # --- LOCATION DATA ---
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        location_name = request.form.get('location')

        # --- SAVE TO DATABASE ---
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''INSERT INTO items 
                    (title, description, category, status, image_filename, latitude, longitude, location_name)
                     VALUES (?,?,?,?,?,?,?,?)''',
                  (title, description, category, status, image_filename, latitude, longitude, location_name))
        conn.commit()
        conn.close()

        flash('Item reported successfully with detected location!')
        return redirect(url_for('index'))

    return render_template('report_item.html', form=form)


@app.route('/items')
def items():
    return redirect(url_for('index'))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ---------------- MAIN APP ENTRY ----------------
if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 10000))  # default fallback
    app.run(host='0.0.0.0', port=port)

