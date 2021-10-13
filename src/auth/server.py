
import io
import sys
import threading
import http.server
from http import HTTPStatus
from urllib.parse import urlparse, parse_qs

class EventSink():
    def __init__(self):
        self.message = ""
        self.changed = False

    def log_once(self, message):
        if not self.changed:
            self.message = message
            self.changed = True


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

    def __init__(self, *args, port, notifier, **kwargs):
        self.port = port
        self.notifier = notifier
        super().__init__(*args, **kwargs)

    def run(self):
        self.start_server()

    def start_server(self):
        Handler = MyHTTPRequestHandler

        with MyHTTPServer(("", self.port), Handler, self.notifier) as httpd:
            print("--> waiting for request on port ", self.port)
            httpd.handle_request()
            # httpd.serve_forever()
            print("--> request handled, server exiting")
