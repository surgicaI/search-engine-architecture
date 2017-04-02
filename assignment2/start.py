import tornado.ioloop
import tornado.web
from tornado.httpclient import AsyncHTTPClient
from tornado import gen, process
import socket
import assignment2.inventory as inventory
import json
import operator
import pickle
import assignment2.indexer as indexer
import assignment2.util as util
import logging

log = logging.getLogger(__name__)

class DefaultHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello World!")

class FrontendHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        dict = {}
        http_client = AsyncHTTPClient()
        frontend_server_response = {}
        query = self.get_argument("q", "Default").replace(' ', '%20').lower()
        for index_server in inventory.index_servers:
            index_server_response = yield http_client.fetch(index_server+"/index?q="+query)
            jsonResponse = json.loads(index_server_response.body.decode('utf-8')) 
            for docIdScorePair in jsonResponse['postings']:
                doc_id = docIdScorePair[0]
                score = docIdScorePair[1]
                dict[doc_id] = score

        sortedList = sorted(dict.items(), key=operator.itemgetter(1), reverse=True)
        frontend_response_list = []
        num_of_items = 0
        for doc_id,score in sortedList:
            num_of_items+=1
            if num_of_items >inventory.items_to_display:
                break
            response = {}
            index = doc_id%len(inventory.doc_servers)
            doc_server_response = yield http_client.fetch(inventory.doc_servers[index]+"/doc?id="+str(doc_id)+"&q="+query)
            json_doc_server_response = json.loads(doc_server_response.body.decode('utf-8'))
            results = json_doc_server_response['results']
            #for debuggin uncomment this line
            #response['doc_id'] = doc_id
            title = results[0]['title']
            if 'category' in title.lower():
                num_of_items -= 1
                continue
            response['title'] = title
            response['url'] = results[0]['url']
            snippet = results[0]['snippet']
            if len(snippet) < 20:
                num_of_items -= 1
                continue
            response['snippet'] = snippet
            frontend_response_list.append(response)
        frontend_server_response['num_results'] = len(frontend_response_list)
        frontend_server_response['results'] = frontend_response_list
        self.write(json.dumps(frontend_server_response))

class IndexServerHandler(tornado.web.RequestHandler):
    def initialize(self, server_id):
        self.server_id = server_id
        with open('assignment4/invindex_jobs/'+str(self.server_id)+'.out', 'rb') as handle:
            self.dict = pickle.load(handle)
        with open('assignment4/idf_jobs/0.out', 'rb') as handle:
            self.term_inv_doc_freq_dict = pickle.load(handle)

    @gen.coroutine
    def get(self):
        query = self.get_argument("q", "Default") 
        tokens = query.split()
        query_vector = {}
        #document_vectors dict will contain a vector for each doc that contains
        # atleast one token in the query
        document_vectors = {}
        index_server_output = {}
        posting_list = []
        for token in tokens:
            #writing a word twice in query wont change results
            if token in query_vector:
                continue
            query_vector[token] = 1.0*(self.term_inv_doc_freq_dict.get(token,1.0))
            tf_list = self.dict.get(token,[])
            for doc_id,freq in tf_list:
                if doc_id in document_vectors:
                    inner_dict = document_vectors[doc_id]
                    inner_dict[token] = inner_dict.get(token,0) + freq*(self.term_inv_doc_freq_dict.get(token,1))
                else:
                    inner_dict = {}
                    inner_dict[token] = freq*(self.term_inv_doc_freq_dict.get(token,1))
                    document_vectors[doc_id] = inner_dict
        for doc_id, document_vector in document_vectors.items():
            score = util.dot_product(document_vector,query_vector)
            posting_list.append([doc_id,score])
        posting_list.sort(key=lambda tup: tup[1],reverse=True)
        index_server_output['postings'] = posting_list[:inventory.items_returned_by_index_server]
        self.write(json.dumps(index_server_output))

class DocumentServerHandler(tornado.web.RequestHandler):
    def initialize(self, server_id):
        self.server_id = server_id
        with open('assignment4/docs_jobs/'+str(self.server_id)+'.out', 'rb') as handle:
            self.dict = pickle.load(handle)

    @gen.coroutine
    def get(self):
        doc_server_output = {}
        #getting doc_id and query and converting doc_id into int
        doc_id = self.get_argument("id", "Default") 
        doc_id = int(doc_id)
        query = self.get_argument("q", "Default")
        #for formatting output as required by the frontend
        inner_dict = {}
        inner_dict['url'] = '_'.join(self.dict[doc_id]['title'].split())
        inner_dict['title'] = self.dict[doc_id]['title']
        inner_dict['doc_id'] = doc_id
        inner_dict['snippet'] = util.get_snippet(self.dict[doc_id]['text'],query)
        doc_server_output['results'] = [inner_dict]
        self.write(json.dumps(doc_server_output))

def main():
    task_id = process.fork_processes(inventory.document_partitions+inventory.index_partitions+1)
    #starting front end server
    if task_id==0 :
        app = tornado.web.Application([(r"/", DefaultHandler),(r"/search", FrontendHandler),])
        app.listen(inventory.BASE_PORT)
        log.info("Frontend listening on " + str(inventory.BASE_PORT))
    #starting document servers
    elif task_id <= inventory.document_partitions:
        server_id = task_id-1
        app = tornado.web.Application([(r"/", DefaultHandler),(r"/doc", DocumentServerHandler,dict(server_id=server_id))])
        app.listen(inventory.doc_server_ports[server_id])
        log.info("Document server "+str(server_id)+" listening on " + str(inventory.doc_server_ports[server_id]))
    #starting index servers
    else:
        server_id = task_id-inventory.document_partitions-1
        app = tornado.web.Application([(r"/", DefaultHandler),(r"/index", IndexServerHandler,dict(server_id=server_id))])
        app.listen(inventory.index_server_ports[server_id])
        log.info("Index server "+str(server_id)+" listening on " + str(inventory.index_server_ports[server_id]))
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    #indexer will only index if pickled files are not present in current directory
    logging.basicConfig(format='%(levelname)s - %(asctime)s - %(message)s', level=logging.DEBUG)
    #indexer.start_indexing()
    main()
    

