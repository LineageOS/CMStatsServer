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
from Queue import Queue

from model import DBSession, init_database
from handlers import SubmitHandler
from threads import DatabaseThread

define('port', 6543)
define('debug', True)

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

        # Queues
        self.queues = {
            'database': Queue()
        }

        # Background threads
        self.threads = {
            'database': DatabaseThread(self.queues['database'])
        }

        for thread in self.threads.itervalues():
            thread.start()

def run_server():
    # Define command line options
    define("config", default="/etc/cmstats.ini", type=unicode, help="Path to configuration file")
    tornado.options.parse_command_line()
    app = Application()

    server = tornado.httpserver.HTTPServer(app, xheaders=True)
    server.listen(int(options.port))
    try:
        IOLoop.instance().start()
    except KeyboardInterrupt:
        logging.info("Shutting down all threads")
        for thread in app.threads.itervalues():
            thread.running = False

if __name__ == '__main__':
    run_server()
