"""
run_frontend.py
---------------
A simple Python script to serve the frontend Vanilla HTML/CSS/JS files locally.
"""

import http.server
import socketserver
import os

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def start_server():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("\n" + "="*50)
        print("🚀 Frontend Server Started Successfully!")
        print(f"👉 Local URL: http://localhost:{PORT}")
        print("="*50 + "\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Shutting down frontend server.")
            httpd.server_close()

if __name__ == "__main__":
    start_server()
