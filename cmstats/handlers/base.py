import tornado.web

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    @property
    def arguments(self):
        return self.request.arguments

    def queue(self, name):
        return self.application.queues.get(name, None)
