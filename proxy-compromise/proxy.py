from __future__ import print_function
import time, requests, re, json, threading, socket, collections
from wsgiref.simple_server import make_server, WSGIRequestHandler
from sys import stderr,version as python_version
from cgi import parse_header, parse_multipart

if python_version.startswith('3'):
    import http.client as httplib
    from io import StringIO
    from urllib.parse import parse_qs
    from http.server import BaseHTTPRequestHandler, HTTPServer
    httplib._is_legal_header_name = re.compile(bytes(r'.*')).match
else:
    import httplib as httplib
    from StringIO import StringIO
    from urlparse import parse_qs
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
    httplib._is_legal_header_name = re.compile(r'.*').match

VULNERABLE_WSGI_URL = "http://%s/backend"
LIGHTTPD_ADDRESSES = {
    "external_address" : socket.gethostname(),
    "internal_address" : "127.0.0.1"
}
BANNED_FORWARD_HEADERS = ["host", "src"]
MOCK_FORWARDED_BODY = "A"*50
proxy_server_bind = "0.0.0.0"
proxy_server_port = 8080

class Proxy_Compromise(BaseHTTPRequestHandler):
    def do_POST(self):
        postvars,src = self.parse_custom_headers()

        if postvars and src:
            resp = None
            try:
                resp = requests.post(VULNERABLE_WSGI_URL % LIGHTTPD_ADDRESSES[src], headers=postvars, data=MOCK_FORWARDED_BODY)
            except Exception as e:
                print(e)
                print("PROXY_COMPROMIZE|> Unable to contact vunlerable lighttpd.")

            if resp and resp.ok:
                self.send_response(resp.status_code, message="aok")
                self.send_header("Content-type", resp.headers['Content-type'])
                self.end_headers()
                
                self.wfile.write(resp.content)
                return
        self._404()

    def parse_custom_headers(self):
        postvars = collections.OrderedDict()
        src = None
        if 'content-length' in self.headers.keys() and int(self.headers['content-length']):
            for header in json.loads(self.rfile.read(int(self.headers['content-length']))):
                pairs = header.split(':')
                if len(pairs) >1:
                    if pairs[0].strip().lower() in BANNED_FORWARD_HEADERS:
                        src = pairs[1]
                        continue
                    elif pairs[0] in postvars.keys():
                        postvars[pairs[0]] += ", " + pairs[1].strip()
                    else:
                        postvars[pairs[0]] = pairs[1].strip()
                else:
                    postvars[""] = pairs[0]
        return postvars, src

    def _404(self):
        self.send_response(500)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("[\"Demonstration has failed\"]"))

    def log_message(self, format, *args):
        __import__("sys").stderr.write("PROXY_COMPROMIZE|> %s - - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format%args))

class LOG_MODIFIED_WSGIRequestHandler(WSGIRequestHandler):
    def log_message(self, format, *args):
        __import__("sys").stderr.write("WSGI_BACKEND|> %s - - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format%args))

def start_proxy_compromise_server():
    print("PROXY_COMPROMIZE|> Proxy Server started http://%s:%s" % (proxy_server_bind, proxy_server_port))
    webServer = HTTPServer((proxy_server_bind, proxy_server_port), Proxy_Compromise)
    threading.current_thread().alive = True
    try:
        while(threading.current_thread().alive):
            webServer.handle_request()
        webServer.server_close()
        print("PROXY_COMPROMIZE|> Server stopped.")
    except Exception:
        print("PROXY_COMPROMIZE|> Error occured. Exitting...")

def demo_app(environ,start_response):
    h = sorted(environ.items())
    headers = ["%s: %s" % (k,v) for k,v in h if k.find("HTTP_") == 0]
    headers += ["\n", environ['wsgi.input'].read(len(MOCK_FORWARDED_BODY))]
    if not environ.has_key('HTTP_X_CUSTOM_HEADER'):
        headers += ["\n", "!AUTHENTICATED!"]
    start_response("200 OK", [('Content-Type','text/plain')])
    return str(headers).encode("utf-8")

if __name__ == "__main__":        
    t = threading.Thread(target=start_proxy_compromise_server)
    t.start()

    # run main backend server
    httpd = make_server('127.0.0.1', 8000, demo_app, handler_class=LOG_MODIFIED_WSGIRequestHandler)
    sa = httpd.socket.getsockname()
    print("WSGI_BACKEND|> Serving HTTP on %s port %s ..." % (sa[0], sa[1]) )

    try:
        while(t.is_alive()):
            httpd.handle_request()
        print("WSGI_BACKEND|> Server stopped.")

    except KeyboardInterrupt:
        print("WSGI_BACKEND|> Ayyyy! I am WoRkInG here :geusture")
    except Exception:
        print("WSGI_BACKEND|> Error occured. Exitting...")

    if t.is_alive():
        t.alive = False
        requests.post("http://%s:%d/goodbye" % (proxy_server_bind, proxy_server_port))
        t.join()