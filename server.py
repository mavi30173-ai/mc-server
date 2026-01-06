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
            username = data.get('username', 'Unknown')
            
            print(f"Got: {username}")
            
            # TEST with proper headers
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            try:
                # Test 1
                test_data = json.dumps({"content": "Test"}).encode()
                req = urllib.request.Request(
                    DISCORD_WEBHOOK, 
                    data=test_data,
                    headers=headers
                )
                resp = urllib.request.urlopen(req, timeout=10)
                print(f"✓ Discord OK: {resp.status}")
            except urllib.error.HTTPError as e:
                print(f"✗ Error {e.code}: {e.reason}")
                # Save data locally anyway
                with open('data.txt', 'a') as f:
                    f.write(f"{username}\n")
            
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

print("Server starting")
HTTPServer(('0.0.0.0', 5000), Handler).serve_forever()
