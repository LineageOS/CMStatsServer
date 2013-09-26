import tornado.web
import logging
import urllib
import json
import pygeoip
import time

from tornado.web import asynchronous
from tornado.httpclient import AsyncHTTPClient

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

        # Publish message, catch any exceptions while doing so as this isn't critical
        try:
            self.publish_message(kwargs)
        except:
            pass

        # Report event to Google Analytics
        try:
            self.report_google_analytics_event(kwargs)
            self.report_google_analytics_appview(kwargs)
        except:
            pass
        
        # Create device record.
        self.queue('database').put(kwargs)
        self.health['lastCheckin'] = int(time.time())
        self.write("Thanks!")
        self.finish()

    def report_google_analytics_event(self, message):
        def callback(response):
            if response.error:
                logging.error("Error while reporting event to Google Analytics: %s" % response.error)
            else:
                logging.debug("Successfully reported event to Google Analytics: %s" % response.code)
                self.health['lastGAReport'] = int(time.time())

        payload = {
                'v': 1,
                #'tid': 'UA-39737599-4',
                't': 'event',
                'an': 'CyanogenMod',
                'cid': message['hash'],
                'av': message['version'],
                'ec': message['name'],
                'ea': message['version'],
                'el': message['country']
                }
        url = "http://www.google-analytics.com/collect"

        logging.debug("Submitting to Google Analytics: %s" % urllib.urlencode(payload))
        client = AsyncHTTPClient()
        client.fetch(url, callback, method='POST', body=urllib.urlencode(payload))

    def report_google_analytics_appview(self, message):
        def callback(response):
            if response.error:
                logging.error("Error while reporting view to Google Analytics: %s" % response.error)
            else:
                logging.debug("Successfully reported view to Google Analytics: %s" % response.code)
                self.health['lastGAReport'] = int(time.time())

        payload = {
                'v': 1,
                'tid': 'UA-39737599-4',
                't': 'appview',
                'cid': message['hash'],
                'an': 'CyanogenMod',
                'av': message['version'],
                'cd': ""
                }
        url = "http://www.google-analytics.com/collect"

        logging.debug("Submitting to Google Analytics: %s" % urllib.urlencode(payload))
        client = AsyncHTTPClient()
        client.fetch(url, callback, method='POST', body=urllib.urlencode(payload))

    def publish_message(self, message):
        ip = self.request.headers.get('X-Real-Ip')
        gic = pygeoip.GeoIP('/usr/share/GeoIP/GeoIPCity.dat')
        record = gic.record_by_addr(ip)
        message.update({
            'ip': ip,
            'longitude': record['longitude'],
            'latitude': record['latitude']
        })
        params = {
            'channel': 'install',
            'key': self.application.publish_key,
            'message': json.dumps(message)
        }
        url = 'http://localhost:8080/publish?%s' % urllib.urlencode(params)

        client = AsyncHTTPClient()
        client.fetch(url, None)
