from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

# --- Supabase config ---
SUPABASE_URL = "https://xbxirbxhahlpzxlcmlnx.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhieGlyYnhoYWhscHp4bGNtbG54Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMwMTkzODgsImV4cCI6MjA2ODU5NTM4OH0.vDzpKx4WTYwf66JVXcWe7ZGniLW8oQ19hGhfJeiwI0w"  # đã rút gọn
SUPABASE_HEADERS = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json"
}

# --- Flask setup ---
app = Flask(__name__)
CORS(app)

# --- Insert URL vào bảng 'reports' ---
def insert_report(url, user_agent):
    data = {
        "url": url,
        "user_agent": user_agent
    }
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/reports",
        json=data,
        headers=SUPABASE_HEADERS
    )
    return response.status_code == 201

# --- Insert URL vào bảng 'malicious_urls' ---
def insert_url(data):
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/malicious_urls",
        json=data,
        headers=SUPABASE_HEADERS
    )
    return response.status_code == 201

# --- /check-url ---
@app.route('/check-url')
def check_url():
    url = request.args.get('u', '')

    # Truy vấn tất cả malicious_urls từ Supabase
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/malicious_urls",
        headers=SUPABASE_HEADERS
    )

    if response.status_code != 200:
        return jsonify({"status": "error"})

    urls = response.json()
    for u in urls:
        if u["url"] in url:
            return jsonify({"status": u["status"]})
    return jsonify({"status": "suspicious"})

# --- POST: người dùng báo cáo URL ---
@app.route('/report', methods=['POST'])
def report_url():
    data = request.get_json()
    url = data.get("url")
    user_agent = request.headers.get("User-Agent")

    if not url:
        return jsonify({"error": "Thiếu URL"}), 400

    if insert_report(url, user_agent):
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Gửi lên Supabase thất bại"}), 500

# --- GET + POST URL độc hại từ Supabase ---
@app.route('/api/urls', methods=["GET", "POST"])
def manage_urls():
    if request.method == "GET":
        res = requests.get(
            f"{SUPABASE_URL}/rest/v1/malicious_urls?select=*",
            headers=SUPABASE_HEADERS
        )
        return jsonify(res.json())

    data = request.get_json()
    success = insert_url(data)
    return jsonify({"success": success})

# --- Lấy tất cả báo cáo từ Supabase ---
@app.route("/api/reports", methods=["GET"])
def get_reports():
    res = requests.get(
        f"{SUPABASE_URL}/rest/v1/reports?select=*",
        headers=SUPABASE_HEADERS
    )
    return jsonify(res.json())
