"""Minimaler lokaler HTTP-Server für die Playwright-Tests der Arabisch-App.

Serviert ein Verzeichnis (Standard: cwd) und setzt für .html-Dateien den
Header `Content-Type: text/html; charset=utf-8`, damit Browser die
UTF-8-kodierten arabischen Texte (vollständiges Taschkīl) korrekt lesen.

Usage: python serve.py <port> [directory]
"""
import http.server
import sys


class UTF8HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        '': 'application/octet-stream',
        '.html': 'text/html; charset=utf-8',
    }


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    directory = sys.argv[2] if len(sys.argv) > 2 else None

    def handler(*args, **kwargs):
        UTF8HTTPRequestHandler(*args, directory=directory, **kwargs)

    server = http.server.ThreadingHTTPServer(('127.0.0.1', port), handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
