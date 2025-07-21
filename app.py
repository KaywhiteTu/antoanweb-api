from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

# --- Supabase config ---
SUPABASE_URL = "https://xbxirbxhahlpzxlcmlnx.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhieGlyYnhoYWhscHp4bGNtbG54Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMwMTkzODgsImV4cCI6MjA2ODU5NTM4OH0.vDzpKx4WTYwf66JVXcWe7ZGniLW8oQ19hGhfJeiwI0w"  # Rút gọn để bảo mật
SUPABASE_HEADERS = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json"
}

# --- Flask setup ---
app = Flask(__name__)
CORS(app)

# --- Supabase INSERT ---
def insert_report(url, user_agent):
    data = { "url": url, "user_agent": user_agent }
    res = requests.post(f"{SUPABASE_URL}/rest/v1/reports", json=data, headers=SUPABASE_HEADERS)
    return res.status_code == 201

def insert_url(data):
    res = requests.post(f"{SUPABASE_URL}/rest/v1/malicious_urls", json=data, headers=SUPABASE_HEADERS)
    return res.status_code == 201

# --- Check URL ---
@app.route("/check-url")
def check_url():
    url = request.args.get("u", "")
    res = requests.get(f"{SUPABASE_URL}/rest/v1/malicious_urls", headers=SUPABASE_HEADERS)
    if res.status_code != 200: return jsonify({"status": "error"})
    for u in res.json():
        if u["url"] in url:
            return jsonify({"status": u["status"]})
    return jsonify({"status": "suspicious"})

# --- Người dùng báo cáo URL ---
@app.route("/report", methods=["POST"])
def report_url():
    data = request.get_json()
    url = data.get("url")
    user_agent = request.headers.get("User-Agent")
    if not url: return jsonify({"error": "Thiếu URL"}), 400
    if insert_report(url, user_agent):
        return jsonify({"success": True})
    else:
        return jsonify({"success": False}), 500

# --- Admin quản lý URL ---
@app.route("/api/urls", methods=["GET", "POST"])
def manage_urls():
    if request.method == "GET":
        res = requests.get(f"{SUPABASE_URL}/rest/v1/malicious_urls?select=*", headers=SUPABASE_HEADERS)
        return jsonify(res.json())
    data = request.get_json()
    return jsonify({"success": insert_url(data)})

@app.route("/api/reports")
def get_reports():
    res = requests.get(f"{SUPABASE_URL}/rest/v1/reports?select=*", headers=SUPABASE_HEADERS)
    return jsonify(res.json())

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

# --- Supabase config ---
SUPABASE_URL = "https://xbxirbxhahlpzxlcmlnx.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhieGlyYnhoYWhscHp4bGNtbG54Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMwMTkzODgsImV4cCI6MjA2ODU5NTM4OH0.vDzpKx4WTYwf66JVXcWe7ZGniLW8oQ19hGhfJeiwI0w"  # Rút gọn
SUPABASE_HEADERS = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json"
}

# --- Flask setup ---
app = Flask(__name__)
CORS(app)

# --- Insert báo cáo vào bảng 'reports' ---
def insert_report(url, user_agent):
    data = {
        "url": url,
        "user_agent": user_agent
    }

    headers = SUPABASE_HEADERS.copy()
    headers["Prefer"] = "return=representation"  # Bắt Supabase trả phản hồi

    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/reports",
        json=data,
        headers=headers
    )

    # 🔥 In log chi tiết để debug
    print("📤 Gửi báo cáo lên Supabase:")
    print("  → URL:", url)
    print("  → User-Agent:", user_agent)
    print("  → Status Code:", response.status_code)
    print("  → Response Body:", response.text)

    return response.status_code in [200, 201]


# --- Insert URL vào bảng 'malicious_urls' ---
def insert_url(data):
    headers = SUPABASE_HEADERS.copy()
    headers["Prefer"] = "return=representation"

    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/malicious_urls",
        json=data,
        headers=headers
    )

    print("📤 Thêm URL độc hại:", response.status_code, response.text)

    return response.status_code in [200, 201]

# --- /check-url ---
@app.route('/check-url')
def check_url():
    url = request.args.get('u', '')

    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/malicious_urls?select=*",
        headers=SUPABASE_HEADERS
    )

    if response.status_code != 200:
        return jsonify({"status": "error"})

    urls = response.json()
    for u in urls:
        if u["url"] in url:
            return jsonify({"status": u["status"]})
    return jsonify({"status": "suspicious"})



# --- POST báo cáo người dùng ---
@app.route('/report', methods=['POST'])
def report_url():
    data = request.get_json()
    url = data.get("url")
    user_agent = request.headers.get("User-Agent")

    print("📥 Nhận báo cáo:", data)

    if not url:
        return jsonify({"error": "Thiếu URL"}), 400

    if insert_report(url, user_agent):
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Gửi lên Supabase thất bại"}), 500

# --- GET + POST malicious URLs ---
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
    
import requests

# --- AI phân tích URL ---
@app.route("/analyze-ai")
def analyze_ai():
    url = request.args.get("u", "")
    if not url:
        return jsonify({"error": "Thiếu URL"}), 400

    model_url = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
    HF_TOKEN = "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"  # ✨ Thay bằng token thật
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "inputs": {
            "hypothesis": "This is a malicious website",
            "premise": f"The website URL is: {url}"
        }
    }

    try:
        response = requests.post(model_url, headers=headers, json=payload)
        print("📡 Trạng thái model:", response.status_code)
        print("📥 Phản hồi:", response.text)

        if response.status_code != 200:
            return jsonify({"error": "Model not available"}), 500

        result = response.json()
        label = result["labels"][0]
        confidence = result["scores"][0]

        return jsonify({
            "result": "malicious" if label == "entailment" else "safe",
            "confidence": confidence
        })
    except Exception as e:
        return jsonify({"error": "AI model exception", "detail": str(e)}), 500

# --- Lấy tất cả báo cáo ---
@app.route("/api/reports", methods=["GET"])
def get_reports():
    res = requests.get(
        f"{SUPABASE_URL}/rest/v1/reports?select=*",
        
        headers=SUPABASE_HEADERS
    )
    return jsonify(res.json())


# --- Run local ---
if __name__ == "__main__":
    app.run(debug=True)
