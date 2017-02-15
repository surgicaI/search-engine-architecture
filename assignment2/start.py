import tornado.ioloop
import tornado.web
from tornado.httpclient import AsyncHTTPClient
from tornado import gen
import socket
import inventory


class MainHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        #response = yield http_client.fetch("http://linserv2.cims.nyu.edu:"+str(backendPorts[currentPortIndex]))
        self.write("Hello World")

if __name__ == "__main__":
    app = tornado.web.Application([(r"/", MainHandler),])
    app.listen(inventory.BASE_PORT)
    tornado.ioloop.IOLoop.current().start()
