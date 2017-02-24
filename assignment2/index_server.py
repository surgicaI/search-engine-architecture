import tornado.ioloop
import tornado.web
from tornado.httpclient import AsyncHTTPClient
from tornado import gen, process
import socket
import inventory
import json
import operator
import pickle

def dot_product(vector1,vector2):
    result = 0
    for key,value in vector1.items():
        result = result + value*vector2.get(key,0)
    return result

class DefaultHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello World!")

class MainHandler(tornado.web.RequestHandler):
    def initialize(self, server_id):
        self.server_id = server_id
        with open('inverted_index'+str(self.server_id)+'.pickle', 'rb') as handle:
            self.dict = pickle.load(handle)

    @gen.coroutine
    def get(self):
        query = self.get_argument("q", "Default") 
        tokens = query.split()
        query_vector = {}
        document_vectors = {}
        index_server_output = {}
        posting_list = []
        for token in tokens:
            query_vector[token] = query_vector.get(token,0) + 1
            tf_list = self.dict.get(token,[])
            for doc_id,freq in tf_list:
                if doc_id in document_vectors:
                    inner_dict = document_vectors[doc_id]
                    inner_dict[token] = inner_dict.get(token,0) + freq
                else:
                    inner_dict = {}
                    inner_dict[token] = freq
                    document_vectors[doc_id] = inner_dict
        for doc_id, document_vector in document_vectors.items():
            score = dot_product(document_vector,query_vector)
            posting_list.append([doc_id,score])
        index_server_output['postings'] = posting_list
        self.write(json.dumps(index_server_output))

def main():
    task_id = process.fork_processes(inventory.index_partitions)
    app = tornado.web.Application([(r"/", DefaultHandler),(r"/index", MainHandler,dict(server_id=task_id))])
    app.listen(inventory.index_server_ports[task_id])
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()

