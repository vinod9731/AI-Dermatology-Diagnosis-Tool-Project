# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import io, os, sqlite3, base64
from functools import wraps
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# ML
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

# OpenAI
from openai import OpenAI

# -------------------- App & Config --------------------
app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-in-.env")
DB_PATH = "database.db"

# -------------------- OpenAI --------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("❌ OPENAI_API_KEY not found. Please check your .env file.")
    client = None
else:
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        print("✅ OpenAI API configured successfully")
    except Exception as e:
        print(f"❌ Error configuring OpenAI API: {e}")
        client = None

# -------------------- Database + Auto-Migration --------------------
def _col_exists(conn, table, column):
    cur = conn.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cur.fetchall())

def init_db():
    """Create tables and ensure required columns exist (auto-migrate)."""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        # Users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT
            )
        """)

        # History table (base shape for very old DBs)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_data TEXT NOT NULL,
                disease_name TEXT NOT NULL,
                query TEXT NOT NULL,
                response TEXT NOT NULL
            )
        """)

        # ---- Ensure new columns exist (migrate older DBs) ----
        if not _col_exists(conn, "history", "user_id"):
            cur.execute("ALTER TABLE history ADD COLUMN user_id INTEGER")

        # IMPORTANT: don't add with DEFAULT CURRENT_TIMESTAMP (not allowed on older SQLite)
        if not _col_exists(conn, "history", "created_at"):
            cur.execute("ALTER TABLE history ADD COLUMN created_at TEXT")
            # Backfill existing rows
            cur.execute("UPDATE history SET created_at = COALESCE(created_at, datetime('now')) WHERE created_at IS NULL OR created_at = ''")

        conn.commit()

def get_db():
    return sqlite3.connect(DB_PATH)

# -------------------- Auth Helpers --------------------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped

# -------------------- Model --------------------
try:
    model = models.resnet50(pretrained=False)  # weights=None (we load our own)
    num_ftrs = model.fc.in_features
    class_to_idx = torch.load('class_to_idx.pth', map_location=torch.device('cpu'))
    model.fc = nn.Linear(num_ftrs, len(class_to_idx))
    model.load_state_dict(torch.load('skin_disease_model.pth', map_location=torch.device('cpu')))
    model.eval()
    idx_to_class = {v: k for k, v in class_to_idx.items()}
except FileNotFoundError as e:
    print(f"Error loading model files: {e}. Please ensure 'skin_disease_model.pth' and 'class_to_idx.pth' are in the root directory.")
    model = None

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# -------------------- Routes: Flow --------------------
@app.route("/")
def root():
    return redirect(url_for("home") if "user_id" in session else url_for("login"))

@app.route("/home")
@login_required
def home():
    return render_template("landing.html", user_name=session.get("user_name"))

@app.route("/analysis")
@login_required
def analysis():
    return render_template("index.html", user_name=session.get("user_name"))

@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            SELECT id, image_data, disease_name, query, response, created_at
            FROM history
            WHERE user_id = ?
            ORDER BY id DESC
        """, (user_id,))
        history_data = cur.fetchall()
    return render_template("dashboard.html", history=history_data, user_name=session.get("user_name"))

# -------------------- Auth: Login / Register / Logout --------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return redirect(url_for("home")) if "user_id" in session else render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    if not email or not password:
        return render_template("login.html", error="Please fill in all fields.")

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name, email, password_hash FROM users WHERE email = ?", (email,))
        row = cur.fetchone()

    if not row or not check_password_hash(row[3], password):
        return render_template("login.html", error="Invalid email or password.")

    session["user_id"], session["user_name"], session["user_email"] = row[0], row[1], row[2]
    return redirect(url_for("home"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return redirect(url_for("home")) if "user_id" in session else render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm = request.form.get("confirm", "")

    if not all([name, email, password, confirm]):
        return render_template("register.html", error="Please fill in all fields.")
    if password != confirm:
        return render_template("register.html", error="Passwords do not match.")

    pwd_hash = generate_password_hash(password)
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, datetime('now'))",
                        (name, email, pwd_hash))
            conn.commit()
            new_id = cur.lastrowid
    except sqlite3.IntegrityError:
        return render_template("register.html", error="Email already registered. Please log in.")

    session["user_id"], session["user_name"], session["user_email"] = new_id, name, email
    return redirect(url_for("home"))

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))

# -------------------- ML Inference --------------------
@app.route("/predict", methods=["POST"])
@login_required
def predict():
    if not model:
        return jsonify({"error": "Model is not loaded. Please check server logs."})
    if "file" not in request.files:
        return jsonify({"error": "No file part"})
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"})

    try:
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_tensor = transform(image).unsqueeze(0)

        with torch.no_grad():
            outputs = model(image_tensor)
            _, predicted = torch.max(outputs, 1)
            disease_name = idx_to_class[predicted.item()].replace("_", " ")

        img_str = base64.b64encode(image_bytes).decode("utf-8")
        return jsonify({"disease": disease_name, "image_data": img_str})
    except Exception as e:
        return jsonify({"error": f"An error occurred during prediction: {str(e)}"})

# -------------------- Chatbot + Save Personal History --------------------
@app.route("/chatbot", methods=["POST"])
@login_required
def chatbot():
    if not client:
        return jsonify({"error": "OpenAI API is not configured correctly."})

    data = request.get_json()
    disease = data.get("disease")
    message = data.get("message")
    image_data = data.get("imageData")
    language = data.get("language", "English")

    if not disease:
        return jsonify({"error": "Disease not provided."})
    if not message:
        return jsonify({"error": "No message provided."})

    try:
        prompt = (
            f"You are an expert dermatologist assistant. The detected skin condition is '{disease}'.\n\n"
            f"The user asked: '{message}'.\n\n"
            f"Provide the answer in **step-by-step bullet points** in {language} (not long paragraphs), covering:\n"
            "1. What it is\n2. How it happens\n3. Reasons/Causes\n4. Symptoms\n"
            "5. Step-by-Step Management/Treatment\n6. Prevention\n\n"
            "⚠️ Always end by advising to consult a certified dermatologist."
        )

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        ai_text = resp.choices[0].message.content

        # Save personal history with explicit created_at to avoid DEFAULT issues
        if all([image_data, disease, message]):
            with sqlite3.connect(DB_PATH) as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO history (user_id, image_data, disease_name, query, response, created_at)
                    VALUES (?, ?, ?, ?, ?, datetime('now'))
                """, (session["user_id"], image_data, disease, message, ai_text))
                conn.commit()

        return jsonify({"response": ai_text})
    except Exception as e:
        return jsonify({"error": f"Failed to get response from OpenAI API: {str(e)}"})

# -------------------- Delete Personal History --------------------
@app.route("/delete_history/<int:id>", methods=["POST"])
@login_required
def delete_history(id):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM history WHERE id = ? AND user_id = ?", (id, session["user_id"]))
        conn.commit()
    return jsonify({"success": True})

# -------------------- Main --------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
