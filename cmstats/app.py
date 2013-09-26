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
from handlers import SubmitHandler, ApiHandler, PingHandler
from threads import DatabaseThread

from cmstats import summary
from cmstats.model.schema.devices import Device

define('port', 6543)
define('debug', True)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/submit", SubmitHandler),
            (r"/api", ApiHandler),
            (r"/ping", PingHandler),
        ]

        settings = {
            'debug': options.debug,
            'port': options.port
        }

        super(Application, self).__init__(handlers, **settings)

        config = ConfigParser()
        config.readfp(open(options.config))

        # One global connection
        init_database(create_engine(config.get('database', 'uri')))
        self.db = DBSession

        # Health Information
        self.health = {
                'lastGAReport': 0,
                'lastCheckin': 0
                }

        # Publish Key
        self.publish_key = config.get('socketio', 'publish_key')

        # Queues
        self.queues = {
            'database': Queue()
        }

        # Background threads
        self.threads = {
            'database': DatabaseThread(self.queues['database'])
        }

        # Populate Summary
        summary.kang = Device.count_kang()
        summary.official = Device.count_nonkang()

        versions = Device.version_count()
        for count, version in versions:
            summary.versions[version] = count
            logging.debug("%s => %s" % (version, count))

        devices = Device.device_count()
        for count, device in devices:
            summary.devices[device] = count
            logging.debug("%s => %s" % (device, count))

        logging.info("Summary populated with kang=[%s], nonkang=[%s]" % (summary.kang, summary.official))

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
