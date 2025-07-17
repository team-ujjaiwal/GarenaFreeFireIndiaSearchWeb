from flask import Flask, request, jsonify
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from data_pb2 import AccountPersonalShowInfo, Players
import urllib3
import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# JWT generate URL
JWT_URL = "https://team-ujjaiwal-jwt.vercel.app/token"

# Replace these with actual UID/PASSWORD per region
CREDENTIALS = {
    "IND": {
        "uid": "3959793024",
        "password": "CD265B729E2C2FA1882AD14579BA602738670D69B4438C127C31AE08FB9D7C17",
        "url": "https://client.ind.freefiremobile.com/FuzzySearchAccountByName"
    },
    # ... (keep your existing credentials)
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

def format_player(player_info):
    """Format the player info from protobuf into a comprehensive dictionary"""
    basic_info = player_info.basic_info
    captain_info = player_info.captain_basic_info if player_info.HasField("captain_basic_info") else None
    clan_info = player_info.clan_basic_info if player_info.HasField("clan_basic_info") else None
    social_info = player_info.social_info if player_info.HasField("social_info") else None
    
    response = {
        "basic_info": {
            "account_id": str(basic_info.account_id),
            "nickname": basic_info.nickname,
            "level": basic_info.level,
            "exp": basic_info.exp,
            "rank": basic_info.rank,
            "max_rank": basic_info.max_rank,
            "ranking_points": basic_info.ranking_points,
            "region": basic_info.region,
            "last_login": convert_timestamp(basic_info.last_login_at),
            "create_at": convert_timestamp(basic_info.create_at),
            "head_pic": basic_info.head_pic,
            "banner_id": basic_info.banner_id,
            "title": basic_info.title,
            "badge_info": {
                "badge_id": basic_info.badge_id,
                "badge_cnt": basic_info.badge_cnt
            },
            "elite_pass": basic_info.has_elite_pass,
            "show_rank": basic_info.show_rank,
            "show_br_rank": basic_info.show_br_rank,
            "show_cs_rank": basic_info.show_cs_rank,
            "cs_rank": basic_info.cs_rank,
            "cs_max_rank": basic_info.cs_max_rank,
            "cs_ranking_points": basic_info.cs_ranking_points,
            "weapon_skins": list(basic_info.weapon_skin_shows),
            "external_icon": {
                "status": basic_info.external_icon_info.status,
                "show_type": basic_info.external_icon_info.show_type
            },
            "release_version": basic_info.release_version,
            "season_id": basic_info.season_id
        },
        "clan_info": {
            "clan_id": str(clan_info.clan_id) if clan_info else None,
            "clan_name": clan_info.clan_name if clan_info else None,
            "clan_level": clan_info.clan_level if clan_info else None,
            "members": {
                "current": clan_info.current_members if clan_info else None,
                "max": clan_info.max_members if clan_info else None
            },
            "captain_id": str(clan_info.captain_id) if clan_info else None
        } if clan_info else None,
        "social_info": {
            "gender": social_info.gender if social_info else None,
            "language": social_info.language if social_info else None,
            "privacy": social_info.privacy if social_info else None,
            "social_highlight": social_info.social_highlight if social_info else None,
            "region_stats": [
                {
                    "region_code": stat.region_code.decode('utf-8'),
                    "matches": stat.total_matches,
                    "wins": stat.wins,
                    "highest_rank": stat.highest_rank,
                    "last_season": stat.last_season_played,
                    "last_match": convert_timestamp(stat.last_match_time)
                } for stat in (social_info.region_stats if social_info else [])
            ]
        } if social_info else None,
        "captain_info": {
            "account_id": str(captain_info.account_id) if captain_info else None,
            "nickname": captain_info.nickname if captain_info else None,
            "level": captain_info.level if captain_info else None,
            "rank": captain_info.rank if captain_info else None
        } if captain_info else None,
        "ranking_leaderboard_pos": player_info.ranking_leaderboard_pos,
        "credit_score": {
            "score": player_info.credit_score_info.score if player_info.HasField("credit_score_info") else None,
            "status": player_info.credit_score_info.status if player_info.HasField("credit_score_info") else None,
            "period": {
                "start": convert_timestamp(player_info.credit_score_info.start) if player_info.HasField("credit_score_info") else None,
                "end": convert_timestamp(player_info.credit_score_info.end) if player_info.HasField("credit_score_info") else None
            },
            "reason": player_info.credit_score_info.reason if player_info.HasField("credit_score_info") else None
        }
    }
    
    return response

@app.route('/search', methods=['GET'])
def search_by_name():
    name = request.args.get('nickname')
    region = request.args.get('region', 'IND').upper()

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
            "status": "success",
            "region": region,
            "requested_name": name,
            "result_count": len(results),
            "results": results
        })

    else:
        return jsonify({
            "status": "error",
            "error": "Failed to fetch data or empty response",
            "status_code": response.status_code
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)