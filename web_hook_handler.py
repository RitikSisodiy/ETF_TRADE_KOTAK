from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
import os

# Define the path to your Git repository
REPO_PATH = ''  # Update this to your repository path


class GitWebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Only handle POST requests
        if self.path == '/webhook':
            try:
                # Change to the repository directory
                os.chdir(REPO_PATH)

                # Execute `git pull`
                result = subprocess.run(['git', 'pull'], capture_output=True, text=True, check=True)

                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Success: ' + result.stdout.encode())
            except subprocess.CalledProcessError as e:
                self.send_response(500)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Error: ' + e.stderr.encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')


def run(server_class=HTTPServer, handler_class=GitWebhookHandler, port=4040):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()


if __name__ == "__main__":
    run()
