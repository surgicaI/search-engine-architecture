import tornado.ioloop
import tornado.web
from tornado.httpclient import AsyncHTTPClient
from tornado import gen
import socket
import inventory
import json
import operator

class DefaultHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello World!")

class MainHandler(tornado.web.RequestHandler):
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


if __name__ == "__main__":
    app = tornado.web.Application([(r"/", DefaultHandler),(r"/search", MainHandler),])
    app.listen(inventory.BASE_PORT)
    tornado.ioloop.IOLoop.current().start()
