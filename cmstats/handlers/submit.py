import tornado.web
import logging

from tornado.web import asynchronous

from cmstats.handlers import BaseHandler
from cmstats.model.schema.devices import Device


class SubmitHandler(BaseHandler):
    @asynchronous
    def get(self):
        return self.post()

    @asynchronous
    def post(self):
        def incomplete():
            self.write("Incomplete Data")
            self.finish()

        device_hash = self.arguments.get('device_hash', None)[0]
        device_name = self.arguments.get('device_name', None)[0]
        device_version = self.arguments.get('device_version', None)[0]
        device_country = self.arguments.get('device_country', None)[0]
        device_carrier_id = self.arguments.get('device_carrier_id', None)[0]

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
        Device.add(**kwargs)

        self.write("Thanks!")
        self.finish()
