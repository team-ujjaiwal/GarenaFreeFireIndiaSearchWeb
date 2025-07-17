from flask import Flask, request, jsonify
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from data_pb2 import AccountPersonalShowInfo
import urllib3
import datetime
import json

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

def format_player_response(player_info):
    """Format the AccountPersonalShowInfo protobuf into the desired JSON structure"""
    response = {
        "basicInfo": {
            "accountId": str(player_info.basic_info.account_id),
            "accountType": player_info.basic_info.account_type,
            "badgeCnt": player_info.basic_info.badge_cnt,
            "badgeId": player_info.basic_info.badge_id,
            "bannerId": str(player_info.basic_info.banner_id),
            "createAt": player_info.basic_info.create_at,
            "csMaxRank": player_info.basic_info.cs_max_rank,
            "csRank": player_info.basic_info.cs_rank,
            "csRankingPoints": player_info.basic_info.cs_ranking_points,
            "exp": str(player_info.basic_info.exp),
            "externalIconInfo": {
                "showType": player_info.basic_info.external_icon_info.show_type,
                "status": player_info.basic_info.external_icon_info.status
            },
            "hasElitePass": player_info.basic_info.has_elite_pass,
            "headPic": str(player_info.basic_info.head_pic),
            "lastLoginAt": convert_timestamp(player_info.basic_info.last_login_at),
            "level": player_info.basic_info.level,
            "liked": player_info.basic_info.liked,
            "maxRank": player_info.basic_info.max_rank,
            "nickname": player_info.basic_info.nickname,
            "rank": player_info.basic_info.rank,
            "rankingPoints": player_info.basic_info.ranking_points,
            "region": player_info.basic_info.region,
            "releaseVersion": player_info.basic_info.release_version,
            "seasonId": player_info.basic_info.season_id,
            "showBrRank": player_info.basic_info.show_br_rank,
            "showCsRank": player_info.basic_info.show_cs_rank,
            "showRank": player_info.basic_info.show_rank,
            "title": player_info.basic_info.title,
            "weaponSkinShows": list(player_info.basic_info.weapon_skin_shows)
        },
        "captainBasicInfo": {
            "accountId": str(player_info.captain_basic_info.account_id),
            "accountType": player_info.captain_basic_info.account_type,
            "badgeCnt": player_info.captain_basic_info.badge_cnt,
            "badgeId": player_info.captain_basic_info.badge_id,
            "bannerId": str(player_info.captain_basic_info.banner_id),
            "createAt": player_info.captain_basic_info.create_at,
            "csMaxRank": player_info.captain_basic_info.cs_max_rank,
            "csRank": player_info.captain_basic_info.cs_rank,
            "csRankingPoints": player_info.captain_basic_info.cs_ranking_points,
            "exp": str(player_info.captain_basic_info.exp),
            "externalIconInfo": {
                "showType": player_info.captain_basic_info.external_icon_info.show_type,
                "status": player_info.captain_basic_info.external_icon_info.status
            },
            "hasElitePass": player_info.captain_basic_info.has_elite_pass,
            "headPic": str(player_info.captain_basic_info.head_pic),
            "lastLoginAt": convert_timestamp(player_info.captain_basic_info.last_login_at),
            "level": player_info.captain_basic_info.level,
            "liked": player_info.captain_basic_info.liked,
            "maxRank": player_info.captain_basic_info.max_rank,
            "nickname": player_info.captain_basic_info.nickname,
            "rank": player_info.captain_basic_info.rank,
            "rankingPoints": player_info.captain_basic_info.ranking_points,
            "region": player_info.captain_basic_info.region,
            "releaseVersion": player_info.captain_basic_info.release_version,
            "seasonId": player_info.captain_basic_info.season_id,
            "showBrRank": player_info.captain_basic_info.show_br_rank,
            "showCsRank": player_info.captain_basic_info.show_cs_rank,
            "showRank": player_info.captain_basic_info.show_rank,
            "title": player_info.captain_basic_info.title,
            "weaponSkinShows": list(player_info.captain_basic_info.weapon_skin_shows)
        },
        "clanBasicInfo": {
            "capacity": player_info.clan_basic_info.max_members,
            "captainId": str(player_info.clan_basic_info.captain_id),
            "clanId": str(player_info.clan_basic_info.clan_id),
            "clanLevel": player_info.clan_basic_info.clan_level,
            "clanName": player_info.clan_basic_info.clan_name,
            "memberNum": player_info.clan_basic_info.current_members
        },
        "diamondCostRes": {
            "diamondCost": player_info.diamond_cost_res.diamond_cost if player_info.HasField("diamond_cost_res") else 0
        },
        "petInfo": {
            "exp": player_info.pet_info.exp if player_info.HasField("pet_info") else 0,
            "id": player_info.pet_info.pet_id if player_info.HasField("pet_info") else 0,
            "isSelected": player_info.pet_info.is_selected if player_info.HasField("pet_info") else False,
            "level": player_info.pet_info.level if player_info.HasField("pet_info") else 0,
            "name": player_info.pet_info.pet_name if player_info.HasField("pet_info") else "",
            "selectedSkillId": player_info.pet_info.selected_skill_id if player_info.HasField("pet_info") else 0,
            "skinId": player_info.pet_info.skin_id if player_info.HasField("pet_info") else 0
        },
        "profileInfo": {
            "avatarId": player_info.profile_info.avatar_id,
            "equipedSkills": list(player_info.profile_info.equipped_skills),
            "pvePrimaryWeapon": player_info.profile_info.pve_primary_weapon
        },
        "socialInfo": {
            "accountId": str(player_info.social_info.account_id),
            "gender": "Gender_MALE" if player_info.social_info.gender == 2 else "Gender_FEMALE" if player_info.social_info.gender == 1 else "Gender_UNKNOWN",
            "language": "Language_ARABIC"  # You'll need to map the language enum values
        }
    }
    
    return response

@app.route('/search', methods=['GET'])
def search_by_name():
    name = request.args.get('nickname')
    region = request.args.get('region', 'ind').upper()

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
        try:
            player_info = AccountPersonalShowInfo()
            player_info.ParseFromString(response.content)
            
            formatted_response = format_player_response(player_info)
            
            return jsonify({
                "region": region.upper(),
                "requested_name": name,
                "result": formatted_response
            })
        except Exception as e:
            return jsonify({"error": f"Failed to parse response: {str(e)}"}), 500
    else:
        return jsonify({"error": "Failed to fetch data or empty response"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)