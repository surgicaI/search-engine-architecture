import tornado.ioloop
import tornado.web
from tornado.httpclient import AsyncHTTPClient
from tornado import gen, process
import socket
import inventory
import json
import operator
import pickle
import indexer

def dot_product(vector1,vector2):
    result = 0
    for key,value in vector1.items():
        result = result + value*vector2.get(key,0)
    return result

def bold_query_tokens(snippet,tokens):
    start_tag = '<strong>'
    end_tag = '</strong>'
    for token in tokens:
        snippet = snippet.replace(token,start_tag+token+end_tag)
    return snippet

def get_snippet(text, query):
    #words to be considered before and after the token
    words_before_token = 7
    words_after_token = 13
    supposed_words_in_snippet = words_before_token+words_after_token
    dots = '...'

    query_tokens = query.split()
    text_tokens = text.split()

    found_index = -1
    snippet = ''
    #finding snippet for the first word in title and if not found then searching second and so on
    for i in range(0,len(query_tokens)):
        try:
            found_index = text_tokens.index(query_tokens[i])
            break;
        except ValueError:
            pass
            #continue to search next query token in text
    if found_index != -1:
        start_index = max(0,found_index-words_before_token)
        end_index = min(found_index+words_after_token,len(text_tokens))
        actual_words_in_snippet = end_index-start_index
        diff_in_words = supposed_words_in_snippet-actual_words_in_snippet
        if diff_in_words > 0:
            if (end_index + diff_in_words) < len(text_tokens):
                end_index += diff_in_words
            elif start_index-diff_in_words >= 0 :
                start_index -= diff_in_words
        #adding dots to begining and end of snippet
        if start_index>0:
            text_tokens[start_index] = dots+text_tokens[start_index]
        if end_index<len(text_tokens):
            text_tokens[end_index-1]=text_tokens[end_index-1]+dots
        snippet = " ".join(text_tokens[start_index:end_index])
        snippet = bold_query_tokens(snippet,query_tokens)
    return snippet

class DefaultHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello World!")

class FrontendHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        dict = {}
        http_client = AsyncHTTPClient()
        frontend_server_response = {}
        query = self.get_argument("q", "Default")
        for index_server in inventory.index_servers:
            index_server_response = yield http_client.fetch(index_server+"/index?q="+query)
            jsonResponse = json.loads(index_server_response.body.decode('utf-8')) 
            for docIdScorePair in jsonResponse['postings']:
                doc_id = docIdScorePair[0]
                score = docIdScorePair[1]
                dict[doc_id] = score

        sortedList = sorted(dict.items(), key=operator.itemgetter(1))
        sortedList.reverse()
        sortedList = sortedList[0:inventory.items_to_display]
        frontend_response_list = []
        for doc_id,score in sortedList:
            response = {}
            index = doc_id%len(inventory.doc_servers)
            doc_server_response = yield http_client.fetch(inventory.doc_servers[index]+"/doc?id="+str(doc_id)+"&q="+query)
            json_doc_server_response = json.loads(doc_server_response.body.decode('utf-8'))
            results = json_doc_server_response['results']
            response['doc_id'] = doc_id
            response['title'] = results[0]['title']
            response['url'] = results[0]['url']
            response['snippet'] = results[0]['snippet']
            frontend_response_list.append(response)
        frontend_server_response['num_results'] = len(frontend_response_list)
        frontend_server_response['results'] = frontend_response_list
        self.write(json.dumps(frontend_server_response))

class IndexServerHandler(tornado.web.RequestHandler):
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

class DocumentServerHandler(tornado.web.RequestHandler):
    def initialize(self, server_id):
        self.server_id = server_id
        with open('document_stores'+str(self.server_id)+'.pickle', 'rb') as handle:
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
        inner_dict['url'] = self.dict[doc_id]['url']
        inner_dict['title'] = self.dict[doc_id]['title']
        inner_dict['doc_id'] = doc_id
        inner_dict['snippet'] = get_snippet(self.dict[doc_id]['text'],query)
        doc_server_output['results'] = [inner_dict]
        self.write(json.dumps(doc_server_output))

def main():
    task_id = process.fork_processes(inventory.document_partitions+inventory.index_partitions+1)
    #starting front end server
    if task_id==0 :
        app = tornado.web.Application([(r"/", DefaultHandler),(r"/search", FrontendHandler),])
        app.listen(inventory.BASE_PORT)
    #startting document servers
    elif task_id <= inventory.document_partitions:
        server_id = task_id-1
        app = tornado.web.Application([(r"/", DefaultHandler),(r"/doc", DocumentServerHandler,dict(server_id=server_id))])
        app.listen(inventory.doc_server_ports[server_id])
    #starting index servers
    else:
        server_id = task_id-inventory.document_partitions-1
        app = tornado.web.Application([(r"/", DefaultHandler),(r"/index", IndexServerHandler,dict(server_id=server_id))])
        app.listen(inventory.index_server_ports[server_id])
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    #indexer will only index if pickled files are not present in current directory
    indexer.start_indexing()
    print "indexing complete, starting servers"
    main()
    

