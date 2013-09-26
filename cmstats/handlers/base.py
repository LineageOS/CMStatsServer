import tornado.web

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    @property
    def summary(self):
        return summary

    @property
    def arguments(self):
        return self.request.arguments

    def get_param(self, name, default=None):
        params = self.request.arguments.get(name, [])
        if params == []:
            return default
        else:
            return params[0]

    def queue(self, name):
        return self.application.queues.get(name, None)
    
    @property
    def health(self):
        return self.application.health
