from flask import Flask, request, jsonify
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from freefire_pb2 import Players  # Make sure your compiled freefire_pb2.py is here
import urllib3
import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# Credentials for IND
UID = "3959794891"
PASSWORD = "CBECEA7B0F13FD5A4A9075F5831089C286FD5CC791BE9A00EF734CEBC20AC756"

# JWT generate URL
JWT_URL = "https://aditya-jwt-v9op.onrender.com/token"

# SEARCH URL for IND
SEARCH_URL = "https://client.ind.freefiremobile.com/FuzzySearchAccountByName"

def get_jwt(uid, password):
    try:
        params = {'uid': uid, 'password': password}
        response = requests.get(JWT_URL, params=params)
        if response.status_code == 200:
            jwt_data = response.json()
            return jwt_data.get("token")  
        return None
    except Exception as e:
        print(f"Error fetching JWT: {e}")
        return None

def encrypt_name(nickname):
    encoded = nickname.encode("utf-8")
    proto_hex = "0a" + format(len(encoded), '02x') + encoded.hex()
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(bytes.fromhex(proto_hex), AES.block_size)).hex()

def convert_timestamp(ts):
    try:
        dt = datetime.datetime.utcfromtimestamp(ts) + datetime.timedelta(hours=8)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return str(ts)

def format_player(player):
    return {
        "account_id": player.accountId,
        "nickname": player.nickname,
        "region": player.region,
        "level": player.level,
        "last_login": convert_timestamp(player.lastLogin)
    }

@app.route('/search', methods=['GET'])
def search_by_name():
    name = request.args.get('nickname')

    if not name:
        return jsonify({"error": "Missing 'name' parameter"}), 400

    jwt_token = get_jwt(UID, PASSWORD)
    if not jwt_token:
        return jsonify({"error": "Failed to generate JWT"}), 500

    encrypted_data = encrypt_name(name)

    headers = {
        'X-Unity-Version': '2018.4.11f1',
        'ReleaseVersion': 'OB49',
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-GA': 'v1 1',
        'Authorization': f'Bearer {jwt_token}',
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)',
        'Host': SEARCH_URL.split("//")[1].split("/")[0],
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip'
    }

    try:
        response = requests.post(SEARCH_URL, headers=headers, data=bytes.fromhex(encrypted_data), verify=False)
    except Exception as e:
        return jsonify({"error": f"Request error: {str(e)}"}), 500

    if response.status_code == 200 and response.content:
        players = Players()
        players.ParseFromString(response.content)

        results = []
        for p in players.player:
            results.append(format_player(p))

        return jsonify({
            "region": "IND",
            "requested_name": name,
            "Credit": "@Ujjaiwal",  # Added Credit field here
            "results": results
        })

    else:
        return jsonify({"error": "Failed to fetch data or empty response"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)