import tornado.web
import logging
import json

from tornado.web import asynchronous

from cmstats.handlers import BaseHandler
from cmstats.model.schema.devices import Device


class ApiHandler(BaseHandler):
    @asynchronous
    def get(self):
        self.method = self.arguments.get('method', None)[0]

        if not self.method:
            self.set_status(500)
            return self.fail("method must be specified")

        try:
            fn = getattr(self, 'method_%s' % self.method)
        except AttributeError:
            self.set_status(405)
            return self.fail("Unknown method")
        else:
            fn()

    def fail(self, error_message):
        self.write(json.dumps({
            'result': None,
            'error': error_message
        }, indent=True))
        return self.finish()

    def success(self, result):
        self.set_header("Content-Type", "application/json")
        callback = self.arguments.get('callback', [None])[0]
        data = json.dumps({
            'result': result,
            'error': None
        })
        if callback is not None:
            self.write("%s(%s)" % (callback, data))
        else:
            self.write(data)

        return self.finish()

    def method_get_counts(self):
        kang = Device.count_kang()
        official = Device.count_nonkang()
        result = {
            'kang': kang,
            'official': official,
            'total': official + kang,
            'device': Device.device_count(),
            'version': Device.version_count(),
            'last_day': Device.count_last_day()
        }
        return self.success(result)
