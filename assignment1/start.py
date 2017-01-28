import tornado.ioloop
import tornado.web
from tornado.httpclient import AsyncHTTPClient
from tornado import gen
import socket

PORT = 55700
backendPorts = [55701, 55702, 55703]
currentPortIndex = -1

class MainHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        global currentPortIndex
        http_client = AsyncHTTPClient()
        currentPortIndex = (currentPortIndex + 1)%3
        response = yield http_client.fetch("http://linserv2.cims.nyu.edu:"+str(backendPorts[currentPortIndex]))
        self.write(response.body)

class Handler_1(tornado.web.RequestHandler):
    def get(self):
        self.write("Socket:"+socket.gethostname()+" Port:"+str(backendPorts[0]))

class Handler_2(tornado.web.RequestHandler):
    def get(self):
        self.write("Socket:"+socket.gethostname()+" Port:"+str(backendPorts[1]))

class Handler_3(tornado.web.RequestHandler):
    def get(self):
        self.write("Socket:"+socket.gethostname()+" Port:"+str(backendPorts[2]))

if __name__ == "__main__":
    app = tornado.web.Application([(r"/", MainHandler),])
    app.listen(PORT)
    backend_1 = tornado.web.Application([(r"/", Handler_1),])
    backend_1.listen(backendPorts[0])
    backend_2 = tornado.web.Application([(r"/", Handler_2),])
    backend_2.listen(backendPorts[1])
    backend_3 = tornado.web.Application([(r"/", Handler_3),])
    backend_3.listen(backendPorts[2])
    tornado.ioloop.IOLoop.current().start()
