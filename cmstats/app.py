import argparse
import logging
import time
import os
import tornado.web
import tornado.httpserver
import tornado.options

from ConfigParser import ConfigParser
from tornado.options import define, options
from tornado.ioloop import IOLoop
from sqlalchemy import create_engine

from model import DBSession, init_database
from handlers import SubmitHandler
from threads import DatabaseThread

define('port', 6543)
define('debug', True)

logging.basicConfig(level=logging.DEBUG)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/submit", SubmitHandler),
        ]

        settings = {
            'debug': options.debug,
        }

        super(Application, self).__init__(handlers, **settings)

        config = ConfigParser()
        config.readfp(open(options.config))

        # One global connection
        init_database(create_engine(config.get('database', 'uri')))
        self.db = DBSession

        # Background threads
        self.threads = {
            'database': DatabaseThread()
        }

        for thread in self.threads.itervalues():
            thread.start()

def run_server():
    parser = argparse.ArgumentParser(description="CMStats Server")
    parser.add_argument('--port', dest='port', type=int, help="Port", default=6543)
    parser.add_argument('--config', dest='config', type=unicode, help="Path to configuration file", default="/etc/cmstats.ini")
    parser.add_argument('--logging', dest='logging', type=unicode, help="Logging Level", choices=['debug', 'info', 'warning', 'error', 'none'], default='debug')
    args = parser.parse_args()

    define('settings', '')
    options.logging = args.logging
    options.port = args.port
    options.config = args.config

    app = Application()
    server = tornado.httpserver.HTTPServer(app, xheaders=True)
    server.listen(int(options.port))
    try:
        IOLoop.instance().start()
    except KeyboardInterrupt:
        logging.debug("Shutting down all threads")
        for thread in app.threads.itervalues():
            thread.running = False


if __name__ == '__main__':
    run_server()
