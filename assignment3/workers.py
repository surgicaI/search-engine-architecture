import tornado.ioloop
import tornado.web
from tornado.httpclient import AsyncHTTPClient
from tornado import gen, process
import socket
import inventory
import logging
import os

log = logging.getLogger(__name__)

class DefaultHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello World!")

class MapperHandlerMap(tornado.web.RequestHandler):
    def initialize(self, server_id):
        self.server_id = server_id

    @gen.coroutine
    def get(self):
        mapper_path = self.get_argument("mapper_path", "wordcount/mapper.py")
        input_file = self.get_argument("input_file", "./starter/oos_jobs/0.in")
        num_reducers = self.get_argument("num_reducers", 3)
        for filename in os.listdir(job_path):
            if filename.endswith('.in'):
                filename = "/".join([job_path,filename])
                cmd = "cat " + filename + " |"
                os.system(" ".join([cmd,inventory.env,reducer_path]))
        self.write(mapper_path+"<br/>"+input_file+"<br/>"+str(num_reducers))

class MapperHandlerRetrieve(tornado.web.RequestHandler):
    def initialize(self, server_id):
        self.server_id = server_id

    @gen.coroutine
    def get(self):
        reducer_ix = self.get_argument("reducer_ix", 0)
        map_task_id = self.get_argument("map_task_id", "task_id") 
        self.write(str(reducer_ix)+"<br/>"+map_task_id)

class ReducerHandler(tornado.web.RequestHandler):
    def initialize(self, server_id):
        self.server_id = server_id

    @gen.coroutine
    def get(self):
        reducer_ix = self.get_argument("reducer_ix", 0)
        reducer_path = self.get_argument("reducer_path", "wordcount/reducer.py")
        map_task_ids = self.get_argument("map_task_ids", "tsdk_id").split(',')
        job_path = self.get_argument("job_path", "fish_jobs")
        http = httpclient.AsyncHTTPClient()
        server = inventory.mapper_servers[i]
        params = urllib.parse.urlencode({'reducer_ix': reducer_ix,
                                         'map_task_id': map_task_ids[i]})
        url = "http://%s/retrieve_map_output?%s" % (server, params)
        http.fetch(url)
        self.write(str(reducer_ix)+"<br/>"+reducer_path+"<br/>"+map_task_ids+"<br/>"+job_path)

def main():
    task_id = process.fork_processes(inventory.num_workers+inventory.num_workers)
    #starting Mapper servers
    if task_id < inventory.num_workers:
        server_id = task_id
        app = tornado.web.Application([(r"/", DefaultHandler),
            (r"/map", MapperHandlerMap,dict(server_id=server_id)),
            (r"/retrieve_map_output", MapperHandlerRetrieve,dict(server_id=server_id))])
        app.listen(inventory.mapper_ports[server_id])
        log.info("Mapper server "+str(server_id)+" listening on " + str(inventory.mapper_ports[server_id]))
    #starting Reducing servers
    else:
        server_id = task_id-inventory.num_workers
        app = tornado.web.Application([(r"/", DefaultHandler),(r"/reduce", ReducerHandler,dict(server_id=server_id))])
        app.listen(inventory.reducer_ports[server_id])
        log.info("Index server "+str(server_id)+" listening on " + str(inventory.reducer_ports[server_id]))
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    #indexer will only index if pickled files are not present in current directory
    logging.basicConfig(format='%(levelname)s - %(asctime)s - %(message)s', level=logging.DEBUG)
    main()
    

