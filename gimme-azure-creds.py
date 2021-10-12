import io
import sys
import time
import random
import threading
from http import HTTPStatus
import http.server
import webbrowser
import base64
import requests

from adal import AuthenticationContext
from urllib.parse import urlparse, parse_qs

from config import config as c


RESOURCE_ID = "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d"  # Azure Databricks Resource ID
REDIRECT_URI = f"http://localhost:{c.port}"
STATE = random.randint(10000, 90000)

class EventSink():
    def __init__(self):
        self.message = ""
        self.changed = False

    def log_once(self, message):
        if not self.changed:
            self.message = message
            self.changed = True

notifier = EventSink()

class MyHTTPServer(http.server.HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, event_sink):
        self.event_sink = event_sink
        http.server.HTTPServer.__init__(self, server_address, RequestHandlerClass)

    def finish_request(self, request, client_address):
        self.RequestHandlerClass(request, client_address, self, event_sink=self.event_sink)

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, event_sink=None, **kwargs):
        self.event_sink = event_sink
        super().__init__(*args, **kwargs)

    def do_GET(self):
        print('--> do_GET')
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        code = query['code'][0]
        self.event_sink.log_once(code)

        # Show the authorization code in the browser
        f = io.BytesIO()
        enc = sys.getfilesystemencoding()
        encoded = code.encode(enc, 'surrogateescape')
        f.write(encoded)
        f.seek(0)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.copyfile(f, self.wfile)
        f.close()
        

class ServerThread(threading.Thread):
    def run(self):
        start_server()


def start_server():
    Handler = MyHTTPRequestHandler
    with MyHTTPServer(("", c.port), Handler, notifier) as httpd:
        print("--> waiting for request on port ", c.port)
        httpd.handle_request()
        # httpd.serve_forever()
        print("--> request handled, server exiting")


def get_authorization_code():
    t = ServerThread()
    t.start()

    auth_uri = f'https://login.windows.net/{c.tenant}/oauth2/authorize?response_type=code&client_id={c.client}' + \
               f'&redirect_uri={REDIRECT_URI}&state={STATE}&resource={RESOURCE_ID}'
    webbrowser.open_new(auth_uri)
    try:
        while not notifier.changed:
            time.sleep(3)
    finally:
        t.join()

    return notifier.message


def get_tokens():
    authority = f"https://login.microsoftonline.com/{c.tenant}"
    context = AuthenticationContext(authority)
    auth_code = get_authorization_code()
    response = context.acquire_token_with_authorization_code(auth_code, REDIRECT_URI, RESOURCE_ID, c.client)

    return response['accessToken'], response['refreshToken']


# Get the tokens, upload as a notebook to the workspace and open the workspace in the browser
access_token, refresh_token = get_tokens()
token_code = f"ACCESS_TOKEN = '{access_token}'\nREFRESH_TOKEN = '{refresh_token}'"

# Need to encode for base64 to work but then need to decode the result to avoid serialization issues later
token_content = base64.b64encode(token_code.encode()).decode()
data = {
  "content": token_content,
  "path": c.token_import_path,
  "language": "PYTHON",
  "overwrite": True,
  "format": "SOURCE"
}
headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {access_token}"
}
res = requests.post(f'https://{c.workspace}/api/2.0/workspace/import', json=data, headers=headers)
print('Token notebook import: ' + 'SUCCEEDED' if res.status_code == 200 else f'FAILED ({res.text})')

# Import a test page
with open('token_test.py', 'r') as fin:
    test_code = fin.read()
test_content = base64.b64encode(test_code.encode()).decode()
data["content"] = test_content
data["path"] = c.test_import_path
res = requests.post(f'https://{c.workspace}/api/2.0/workspace/import', json=data, headers=headers)
print('Test notebook import: ' + 'SUCCEEDED' if res.status_code == 200 else f'FAILED ({res.text})')

webbrowser.open_new(f'https://{c.workspace}')
