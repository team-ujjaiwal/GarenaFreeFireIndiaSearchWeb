from flask import Flask, request, jsonify
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from data_pb2 import AccountPersonalShowInfo, Players
import urllib3
import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# JWT generate URL
JWT_URL = "https://team-ujjaiwal-jwt.vercel.app/token"

# Simplified credentials for debugging
CREDENTIALS = {
    "IND": {
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
        response = requests.get(JWT_URL, params=params, timeout=10)
        response.raise_for_status()  # Raises exception for 4XX/5XX status
        jwt_data = response.json()
        return jwt_data.get("token")
    except Exception as e:
        logger.error(f"JWT Error: {str(e)}")
        return None

def encrypt_name(nickname):
    try:
        encoded = nickname.encode("utf-8")
        proto_hex = "0a" + format(len(encoded), '02x') + encoded.hex()
        key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
        iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return cipher.encrypt(pad(bytes.fromhex(proto_hex), AES.block_size)).hex()
    except Exception as e:
        logger.error(f"Encryption Error: {str(e)}")
        return None

def convert_timestamp(ts):
    try:
        if ts == 0:
            return None
        dt = datetime.datetime.utcfromtimestamp(ts) + datetime.timedelta(hours=8)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return str(ts)

def safe_get_proto_field(proto_obj, field_name, default=None):
    """Safely get a protobuf field with fallback to default"""
    if proto_obj is None or not proto_obj.HasField(field_name):
        return default
    return getattr(proto_obj, field_name)

def format_player(player_info):
    """Format player info with proper error handling"""
    try:
        basic_info = player_info.basic_info
        captain_info = safe_get_proto_field(player_info, "captain_basic_info")
        clan_info = safe_get_proto_field(player_info, "clan_basic_info")
        social_info = safe_get_proto_field(player_info, "social_info")
        credit_info = safe_get_proto_field(player_info, "credit_score_info")

        response = {
            "basic_info": {
                "account_id": str(basic_info.account_id),
                "nickname": basic_info.nickname,
                "level": basic_info.level,
                "rank": basic_info.rank,
                "last_login": convert_timestamp(basic_info.last_login_at),
                "region": basic_info.region,
                # Add other basic fields as needed
            },
            "clan_info": {
                "clan_id": str(clan_info.clan_id) if clan_info else None,
                "clan_name": clan_info.clan_name if clan_info else None,
            } if clan_info else None,
            "credit_score": {
                "score": credit_info.score if credit_info else None,
            } if credit_info else None
        }
        return response
    except Exception as e:
        logger.error(f"Formatting Error: {str(e)}")
        return {"error": "Failed to format player data"}

@app.route('/search', methods=['GET'])
def search_by_name():
    try:
        name = request.args.get('nickname')
        region = request.args.get('region', 'IND').upper()

        if not name:
            return jsonify({"status": "error", "message": "Missing nickname parameter"}), 400

        creds = CREDENTIALS.get(region)
        if not creds:
            return jsonify({"status": "error", "message": f"Unsupported region '{region}'"}), 400

        logger.debug(f"Searching for {name} in {region}")

        # Get JWT token
        jwt_token = get_jwt(creds["uid"], creds["password"])
        if not jwt_token:
            return jsonify({"status": "error", "message": "Failed to generate JWT"}), 500

        # Encrypt name
        encrypted_data = encrypt_name(name)
        if not encrypted_data:
            return jsonify({"status": "error", "message": "Failed to encrypt name"}), 500

        headers = {
            'X-Unity-Version': '2018.4.11f1',
            'Authorization': f'Bearer {jwt_token}',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)',
        }

        # Make request
        response = requests.post(
            creds["url"],
            headers=headers,
            data=bytes.fromhex(encrypted_data),
            verify=False,
            timeout=10
        )

        logger.debug(f"API Response Status: {response.status_code}")

        if response.status_code == 200 and response.content:
            try:
                players = Players()
                players.ParseFromString(response.content)
                
                results = []
                for p in players.player:
                    formatted = format_player(p)
                    if "error" not in formatted:
                        results.append(formatted)

                return jsonify({
                    "status": "success",
                    "region": region,
                    "name": name,
                    "count": len(results),
                    "results": results
                })
            except Exception as e:
                logger.error(f"Protobuf Parsing Error: {str(e)}")
                return jsonify({
                    "status": "error",
                    "message": "Failed to parse response data",
                    "debug": str(e)
                }), 500
        else:
            return jsonify({
                "status": "error",
                "message": "API request failed",
                "status_code": response.status_code,
                "response": response.text[:200] if response.text else None
            }), 500

    except Exception as e:
        logger.error(f"Unexpected Error: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Internal server error",
            "debug": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)