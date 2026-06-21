from flask import Flask
import json
import os

app = Flask(__name__)

@app.route("/")
def home():

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_FILE = os.path.join(BASE_DIR, "..", "monitor", "data.json")

    with open(DATA_FILE) as f:
        data = json.load(f)

    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="5">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <title>Cloud Monitoring Dashboard</title>
</head>

<body class="bg-light">

<div class="container mt-5">

<h1 class="text-center mb-5">
Cloud Infrastructure Monitoring Dashboard
</h1>

<div class="card shadow p-4">

<h4>CPU Usage: {data['cpu']}%</h4>
<div class="progress mb-4">
    <div class="progress-bar bg-primary"
         style="width:{data['cpu']}%">
         {data['cpu']}%
    </div>
</div>

<h4>RAM Usage: {data['ram']}%</h4>
<div class="progress mb-4">
    <div class="progress-bar bg-success"
         style="width:{data['ram']}%">
         {data['ram']}%
    </div>
</div>

<h4>Disk Usage: {data['disk']}%</h4>
<div class="progress mb-4">
    <div class="progress-bar bg-warning"
         style="width:{data['disk']}%">
         {data['disk']}%
    </div>
</div>

</div>

</div>

</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
