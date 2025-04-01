import os
import json
import uuid
from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

DATA_FILE = "data.json"
UPLOAD_FOLDER = "static/images"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # Limit file size to 2MB
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load existing data or create an empty list
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

# Function to read data from JSON file
def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# Function to write data to JSON file
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Check allowed file extensions
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Home Page (Search & View Data)
@app.route("/")
def index():
    return render_template("index.html")

# Add Data Page (Form)
@app.route("/add")
def add_page():
    return render_template("add.html")

# API to get stored data
@app.route("/api/data", methods=["GET"])
def get_data():
    return jsonify(load_data())

# API to add new data (with image upload)
@app.route("/api/add", methods=["POST"])
def add_data():
    data = load_data()
    
    # Get form data
    name = request.form.get("name")
    birthdate = request.form.get("birthdate")
    gender = request.form.get("gender")
    category = request.form.get("category")
    file = request.files.get("image")

    if not name or not birthdate or not gender or not category or not file:
        return jsonify({"error": "All fields are required, including an image"}), 400

    # Generate a unique ID
    user_id = str(uuid.uuid4())[:8]

    # Process Image Upload
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{user_id}_{file.filename}")
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)
        image_url = f"/static/images/{filename}"
    else:
        return jsonify({"error": "Invalid image format"}), 400

    # Add new entry
    new_entry = {
        "id": user_id,
        "name": name,
        "birthdate": birthdate,
        "gender": gender,
        "category": category,
        "image": image_url
    }
    data.append(new_entry)
    
    save_data(data)  # Save to JSON file
    return redirect(url_for("index"))  # Redirect to home page

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  
    app.run(host="0.0.0.0", port=port, debug=True)
