import http.server
import socketserver

PORT = 8000

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("サーバーを起動しました。ポート:", PORT)
    print("テストを停止するには Control + C を押してください。")
    httpd.serve_forever()