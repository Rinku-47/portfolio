from flask import Flask, render_template, request, redirect, flash, url_for
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'static/certificates'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

load_dotenv()

# ✅ SQLite database connection
def get_db_connection():
    conn = sqlite3.connect('portfolio.db')
    conn.row_factory = sqlite3.Row
    return conn

# ✅ Flask-Login setup
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if user:
        return User(user["id"], user["username"], user["password_hash"])
    return None

@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM achievements ORDER BY id DESC")
    achievements = cursor.fetchall()

    cursor.execute("SELECT * FROM projects ORDER BY id DESC")
    projects = cursor.fetchall()
    return render_template('index.html', achievements=achievements, projects=projects)

@app.route('/contact', methods=['POST'])
def contact():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASS")
    receiver_email = os.getenv("EMAIL_RECEIVER")

    subject = f"Portfolio contact - From {name}"
    body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print("✅ Email sent successfully!")
    except Exception as e:
        print("❌ Email Error:", e)
        flash("Failed to send email. Check SMTP credentials or app password.", "danger")
        return redirect(url_for('index'))

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO feedbacks (name, email, message) VALUES (?, ?, ?)", (name, email, message))
        db.commit()
        print("✅ Feedback saved in database!")
        flash("Message sent and saved successfully!", "success")
    except Exception as e:
        print("❌ Database Error:", e)
        flash("Email sent but failed to save message to database.", "warning")

    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            login_user(User(user['id'], user['username'], user['password_hash']))
            flash("Login successful!", "success")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid username or password", "danger")

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "info")
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html', user=current_user)

@app.route('/admin/feedbacks')
@login_required
def view_feedbacks():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM feedbacks ORDER BY id DESC")
    feedbacks = cursor.fetchall()
    return render_template('admin_feedbacks.html', feedbacks=feedbacks)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/admin/achievements', methods=['GET', 'POST'])
@login_required
def manage_achievements():
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        file = request.files['certificate']
        filename = None

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)

        cursor.execute(
            "INSERT INTO achievements (title, description, certificate_filename) VALUES (?, ?, ?)",
            (title, description, filename)
        )
        db.commit()
        flash("Achievement added successfully!", "success")

    cursor.execute("SELECT * FROM achievements ORDER BY id DESC")
    achievements = cursor.fetchall()
    return render_template('admin_achievements.html', achievements=achievements)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)

