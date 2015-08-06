#!/bin/env python

import SimpleHTTPServer
import SocketServer

class AllowOriginRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        SimpleHTTPServer.SimpleHTTPRequestHandler.end_headers(self)

if __name__ == '__main__':
    PORT = 18001
    httpd = SocketServer.TCPServer(("", PORT), AllowOriginRequestHandler)
    print "serving at port", PORT
    httpd.serve_forever()
