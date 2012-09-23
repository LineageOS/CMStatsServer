import tornado.web
import logging

from tornado.web import asynchronous

from cmstats.handlers import BaseHandler


class SubmitHandler(BaseHandler):
    @asynchronous
    def get(self):
        return self.post()

    @asynchronous
    def post(self):
        def incomplete():
            self.write("Incomplete Data")
            self.finish()

        device_hash = self.get_param('device_hash', None)
        device_name = self.get_param('device_name')
        device_version = self.get_param('device_version', None)
        device_country = self.get_param('device_country', None)
        device_carrier_id = self.get_param('device_carrier_id', None)

        kwargs = {
            'hash': device_hash,
            'name': device_name,
            'version': device_version,
            'country': device_country,
            'carrier_id': device_carrier_id,
        }

        if device_hash == "":
            return incomplete()

        if device_name == "":
            return incomplete()

        for v in kwargs.itervalues():
            if v == None:
                return incomplete()

        # Create device record.
        self.queue('database').put(kwargs)

        self.write("Thanks!")
        self.finish()
