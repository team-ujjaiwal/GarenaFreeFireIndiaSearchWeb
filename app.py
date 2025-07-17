from flask import Flask, request, jsonify
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from freefire_pb2 import Players
import urllib3
import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# JWT generate URL
JWT_URL = "https://team-ujjaiwal-jwt.vercel.app/token"

# Replace these with actual UID/PASSWORD per region
CREDENTIALS = {
    "END": {
        "uid": "3959793024",
        "password": "CD265B729E2C2FA1882AD14579BA602738670D69B4438C127C31AE08FB9D7C17",
        "url": "https://client.ind.freefiremobile.com/FuzzySearchAccountByName"
    },
    "SG": {
        "uid": "3943739516",
        "password": "BFA0A0D9DF6D4EE1AA92354746475A429D775BCA4D8DD822ECBC6D0BF7B51886",
        "url": "https://clientbp.ggblueshark.com/FuzzySearchAccountByName"
    },
    "NA": {
        "uid": "3943737998",
        "password": "92EB4C721DB698B17C1BF61F8F7ECDEC55D814FB35ADA778FA5EE1DC0AEAEDFF",
        "url": " https://client.us.freefiremobile.com/FuzzySearchAccountByName"
    },
    "BR": {
        "uid": "3943737998",
        "password": "92EB4C721DB698B17C1BF61F8F7ECDEC55D814FB35ADA778FA5EE1DC0AEAEDFF",
        "url": "https://client.us.freefiremobile.com/FuzzySearchAccountByName"
    }, 
    "SAC": {
        "uid": "3943737998",
        "password": "92EB4C721DB698B17C1BF61F8F7ECDEC55D814FB35ADA778FA5EE1DC0AEAEDFF",
        "url": "https://client.us.freefiremobile.com/FuzzySearchAccountByName"
    }, 
    "US": {
        "uid": "3943737998",
        "password": "92EB4C721DB698B17C1BF61F8F7ECDEC55D814FB35ADA778FA5EE1DC0AEAEDFF",
        "url": "https://client.us.freefiremobile.com/FuzzySearchAccountByName"
    }, 
    "ID": {
        "uid": "3943739516",
        "password": "BFA0A0D9DF6D4EE1AA92354746475A429D775BCA4D8DD822ECBC6D0BF7B51886",
        "url": "https://clientbp.ggblueshark.com/FuzzySearchAccountByName"
    },
    "TW": {
        "uid": "3943739516",
        "password": "BFA0A0D9DF6D4EE1AA92354746475A429D775BCA4D8DD822ECBC6D0BF7B51886",
        "url": "https://clientbp.ggblueshark.com/FuzzySearchAccountByName"
    },
    "TH": {
        "uid": "3943739516",
        "password": "BFA0A0D9DF6D4EE1AA92354746475A429D775BCA4D8DD822ECBC6D0BF7B51886",
        "url": "https://clientbp.ggblueshark.com/FuzzySearchAccountByName"
    },
    "BR": {
        "uid": "3943739516",
        "password": "BFA0A0D9DF6D4EE1AA92354746475A429D775BCA4D8DD822ECBC6D0BF7B51886",
        "url": "https://clientbp.ggblueshark.com/FuzzySearchAccountByName"
    },
    "BD": {
        "uid": "3943739516",
        "password": "BFA0A0D9DF6D4EE1AA92354746475A429D775BCA4D8DD822ECBC6D0BF7B51886",
        "url": "https://clientbp.ggblueshark.com/FuzzySearchAccountByName"
    },
    "ME": {
        "uid": "3943739516",
        "password": "BFA0A0D9DF6D4EE1AA92354746475A429D775BCA4D8DD822ECBC6D0BF7B51886",
        "url": "https://clientbp.ggblueshark.com/FuzzySearchAccountByName"
    },
    "RU": {
        "uid": "3943739516",
        "password": "BFA0A0D9DF6D4EE1AA92354746475A429D775BCA4D8DD822ECBC6D0BF7B51886",
        "url": "https://clientbp.ggblueshark.com/FuzzySearchAccountByName"
    },
    "VN": {
        "uid": "3943739516",
        "password": "BFA0A0D9DF6D4EE1AA92354746475A429D775BCA4D8DD822ECBC6D0BF7B51886",
        "url": "https://clientbp.ggblueshark.com/FuzzySearchAccountByName"
    },
    "PK": {
        "uid": "3943739516",
        "password": "BFA0A0D9DF6D4EE1AA92354746475A429D775BCA4D8DD822ECBC6D0BF7B51886",
        "url": "https://clientbp.ggblueshark.com/FuzzySearchAccountByName"
    },
    "CIS": {
        "uid": "3943739516",
        "password": "BFA0A0D9DF6D4EE1AA92354746475A429D775BCA4D8DD822ECBC6D0BF7B51886",
        "url": "https://clientbp.ggblueshark.com/FuzzySearchAccountByName"
    },
    "EROUPE": {
        "uid": "3943739516",
        "password": "BFA0A0D9DF6D4EE1AA92354746475A429D775BCA4D8DD822ECBC6D0BF7B51886",
        "url": "https://clientbp.ggblueshark.com/FuzzySearchAccountByName"
    },
    # Add more servers as needed
}

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
    region = request.args.get('region', 'ind').upper()  # FIXED here 👈

    if not name:
        return jsonify({"error": "Missing 'nickname' parameter"}), 400

    creds = CREDENTIALS.get(region)
    if not creds:
        return jsonify({"error": f"Unsupported region '{region}'"}), 400

    jwt_token = get_jwt(creds["uid"], creds["password"])
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
        'Host': creds["url"].split("//")[1].split("/")[0],
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip'
    }

    try:
        response = requests.post(creds["url"], headers=headers, data=bytes.fromhex(encrypted_data), verify=False)
    except Exception as e:
        return jsonify({"error": f"Request error: {str(e)}"}), 500

    if response.status_code == 200 and response.content:
        players = Players()
        players.ParseFromString(response.content)

        results = [format_player(p) for p in players.player]

        return jsonify({
            "region": region.upper(),
            "requested_name": name,
            "results": results
        })

    else:
        return jsonify({"error": "Failed to fetch data or empty response"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)