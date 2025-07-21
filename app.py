from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

# --- Supabase config ---
SUPABASE_URL = "https://xbxirbxhahlpzxlcmlnx.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # Rút gọn để bảo mật
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

# --- AI phân tích URL ---
@app.route("/analyze-ai")
def analyze_ai():
    url = request.args.get("u", "")
    if not url: return jsonify({"error": "Thiếu URL"}), 400

    ai_response = requests.post(
        "https://api-inference.huggingface.co/models/mrm8488/bert-tiny-finetuned-phishing",
        headers={"Content-Type": "application/json"},
        json={"inputs": url}
    )

    try:
        result = ai_response.json()[0]
        label = result["label"]
        score = result["score"]
        return jsonify({
            "result": "malicious" if label == "LABEL_1" else "safe",
            "confidence": round(score, 2),
            "raw_label": label
        })
    except Exception as e:
        print("❌ AI lỗi:", e)
        return jsonify({"error": "AI model error"}), 500

# --- Run local ---
if __name__ == "__main__":
    app.run(debug=True)
