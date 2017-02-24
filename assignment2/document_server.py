import tornado.ioloop
import tornado.web
from tornado.httpclient import AsyncHTTPClient
from tornado import gen, process
import socket
import inventory
import json
import operator
import pickle

class DefaultHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello World!")

class MainHandler(tornado.web.RequestHandler):
    def initialize(self, server_id):
        self.server_id = server_id
        with open('document_stores'+str(self.server_id)+'.pickle', 'rb') as handle:
            self.dict = pickle.load(handle)

    @gen.coroutine
    def get(self):
        doc_server_output = {}
        doc_id = self.get_argument("id", "Default") 
        doc_id = int(doc_id)
        query = self.get_argument("q", "Default") 
        inner_dict = {}
        inner_dict['url'] = self.dict[doc_id]['url']
        inner_dict['title'] = self.dict[doc_id]['title']
        inner_dict['doc_id'] = doc_id
        text = self.dict[doc_id]['text']
        tokens = query.split()
        index = text.index(tokens[0])
        pre = 15
        after = 40
        snippet = text[index-pre:index+after]
        inner_dict['snippet'] = snippet
        doc_server_output['results'] = [inner_dict]
        self.write(json.dumps(doc_server_output))

def main():
    task_id = process.fork_processes(inventory.document_partitions)
    app = tornado.web.Application([(r"/", DefaultHandler),(r"/doc", MainHandler,dict(server_id=task_id))])
    app.listen(inventory.doc_server_ports[task_id])
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()



