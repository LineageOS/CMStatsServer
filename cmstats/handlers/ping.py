import tornado.web
import logging
import socket
import time
import os

from tornado.web import asynchronous

from cmstats.handlers import BaseHandler
from cmstats import __version__, summary
from cmstats.model.schema.devices import Device

PAGE_TEMPLATE = """
<html>
  <head>
  </head>
  <body>
    <b>CMStatsServer (v%(version)s) | %(hostname)s:%(port)s</b>
    <hr/>
    %(status)s
    <hr/>
    totalCheckins - %(totalCheckins)s
    <br/>
    lastCheckin - %(lastCheckin)s seconds ago
    <br/>
    lastGAReport - %(lastGAReport)s seconds ago
    <br/>
    freeSpace - %(freeSpace)sMB
    <br/>
    databaseExceptions - %(databaseExceptions)s
    <br/>
    databaseQueueSize - %(databaseQueueSize)s
  </body>
</html>
"""

class PingHandler(BaseHandler):
    @asynchronous
    def get(self):
        status = '** OK **'

        lastGAReport = int(time.time()) - self.health['lastGAReport']
        if lastGAReport > 600:
            status = '** ERROR **'

        lastCheckin = int(time.time()) - self.health['lastCheckin']
        if lastCheckin > 600:
            status = '** ERROR **'

        totalCheckins = summary.submits
        if totalCheckins < 100:
            status = '** ERROR **'

        st = os.statvfs("/")
        freeSpace = (st.f_bsize * st.f_bavail) / (1024**2)
        if freeSpace < 512:
            status = '** ERROR **'

        databaseExceptions = summary.databaseExceptions
        if databaseExceptions > 1000:
            status = '** ERROR **'

        databaseQueueSize = self.queue('database').qsize()
        if databaseQueueSize > 2000:
            status = '** ERROR **'

        content = PAGE_TEMPLATE % {
                'version': __version__,
                'hostname': socket.gethostname(),
                'port': self.application.settings['port'],
                'status': status,
                'lastGAReport': lastGAReport,
                'lastCheckin': lastCheckin,
                'freeSpace': freeSpace,
                'totalCheckins': totalCheckins,
                'databaseExceptions': databaseExceptions,
                'databaseQueueSize': databaseQueueSize
                }

        self.write(content)
        self.finish()
