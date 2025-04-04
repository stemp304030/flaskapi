import os
import json
import uuid
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

DATA_FILE = "data.json"
UPLOAD_FOLDER = "static/images"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

SENDER_EMAIL = "stemp304030@gmail.com"
EMAIL_PASSWORD = "gtib cbjo ieiu oqiy"  # Use Gmail App Password

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add")
def add_page():
    return render_template("add.html")

@app.route("/api/data", methods=["GET"])
def get_data():
    return jsonify(load_data())

@app.route("/api/add", methods=["POST"])
def add_data():
    data = load_data()

    name = request.form.get("name")
    birthdate = request.form.get("birthdate")
    gender = request.form.get("gender")
    category = request.form.get("category")
    file = request.files.get("image")

    if not name or not birthdate or not gender or not category or not file:
        return jsonify({"error": "All fields are required"}), 400

    user_id = str(uuid.uuid4())[:8]

    if file and allowed_file(file.filename):
        filename = secure_filename(f"{user_id}_{file.filename}")
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)
        image_url = f"/static/images/{filename}"
    else:
        return jsonify({"error": "Invalid image format"}), 400

    new_entry = {
        "id": user_id,
        "name": name,
        "birthdate": birthdate,
        "gender": gender,
        "category": category,
        "image": image_url
    }
    data.append(new_entry)
    save_data(data)

    return redirect(url_for("index"))

@app.route("/send_email", methods=["POST"])
def send_email():
    data = load_data()
    entry_id = request.form.get("id")
    recipient_email = request.form.get("recipient")

    entry = next((item for item in data if item["id"] == entry_id), None)
    if not entry:
        return "Data not found", 404

    message_body = f"""
    ID: {entry['id']}
    Name: {entry['name']}
    Birthdate: {entry['birthdate']}
    Gender: {entry['gender']}
    Category: {entry['category']}
    """

    msg = MIMEText(message_body)
    msg["Subject"] = f"Details of {entry['name']}"
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)
        return redirect(url_for("index"))
    except Exception as e:
        return f"Failed to send email: {e}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
