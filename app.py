import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename
from forms import ReportForm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
DB_PATH = os.path.join(BASE_DIR, 'items.db')
ALLOWED_EXT = {'png','jpg','jpeg','gif'}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'  # change in production
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXT

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
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    q = request.args.get('q','').strip()
    category = request.args.get('category','').strip()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    query = "SELECT id,title,description,category,status,image_filename,created_at FROM items WHERE 1=1"
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

@app.route('/report', methods=['GET','POST'])
def report():
    form = ReportForm()
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        category = form.category.data
        status = form.status.data
        image_filename = None
        file = request.files.get('image')
        if file and file.filename != '':
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # avoid name clash
                base, ext = os.path.splitext(filename)
                filename = f"{base}_{int(os.times()[4])}{ext}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
            else:
                flash('File type not allowed. Use png/jpg/jpeg/gif.')
                return redirect(request.url)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO items (title,description,category,status,image_filename) VALUES (?,?,?,?,?)',
                  (title,description,category,status,image_filename))
        conn.commit()
        conn.close()
        flash('Item reported successfully.')
        return redirect(url_for('index'))
    return render_template('report_item.html', form=form)

@app.route('/items')
def items():
    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    init_db()
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

    import sqlite3

conn = sqlite3.connect('instance/lost_and_found.db')
cur = conn.cursor()

# Create admin table if not exists
cur.execute('''CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)''')

# Insert a default admin user (username: admin, password: admin123)
try:
    cur.execute("INSERT INTO admin (username, password) VALUES (?, ?)", ('admin', 'admin123'))
    conn.commit()
except:
    pass

conn.close()



