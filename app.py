from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/check-url')
def check_url():
    url = request.args.get('u', '')
    
    # Giả lập logic kiểm tra URL
    if "facebook" in url:
        status = "malicious"
    elif "wikipedia" in url:
        status = "safe"
    else:
        status = "suspicious"

    return jsonify({"status": status})
