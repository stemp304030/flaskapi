from flask import Flask, jsonify, render_template
import os

app = Flask(__name__)

# Sample API data
tasks = [
    {"id": 1, "task": "Learn Flask", "status": "Pending"},
    {"id": 2, "task": "Build API", "status": "In Progress"},
    {"id": 3, "task": "Integrate Frontend", "status": "Completed"}
]

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)