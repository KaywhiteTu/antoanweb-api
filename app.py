from flask import Flask, request, jsonify
from flask_cors import CORS
import json, datetime

app = Flask(__name__)
CORS(app)

def load_data(file):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except:
        return []

def save_data(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/check-url')
def check_url():
    url = request.args.get('u', '')
    urls = load_data("urls.json")
    for u in urls:
        if u["url"] in url:
            return jsonify({"status": u["status"]})
    return jsonify({"status": "suspicious"})

@app.route('/report', methods=['POST'])
def report_url():
    data = request.get_json()
    reports = load_data("reports.json")
    reports.append({"url": data.get("url"), "time": str(datetime.datetime.now())})
    save_data("reports.json", reports)
    return jsonify({"success": True})

@app.route('/api/urls', methods=["GET", "POST"])
def manage_urls():
    if request.method == "GET":
        return jsonify(load_data("urls.json"))
    data = request.get_json()
    urls = load_data("urls.json")
    urls.append(data)
    save_data("urls.json", urls)
    return jsonify({"success": True})

@app.route("/api/reports", methods=["GET"])
def get_reports():
    return jsonify(load_data("reports.json"))
