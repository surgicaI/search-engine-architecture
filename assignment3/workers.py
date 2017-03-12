import tornado.ioloop
import tornado.web
from tornado.httpclient import AsyncHTTPClient
from tornado import gen, process
import socket
import inventory
import logging
import subprocess
import json
import uuid
import urllib

log = logging.getLogger(__name__)
map_output_dict = {}

class DefaultHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello World!")

class MapperHandlerMap(tornado.web.RequestHandler):
    def initialize(self, server_id):
        self.server_id = server_id

    @gen.coroutine
    def get(self):
        task_id = uuid.uuid4().hex
        mapper_path = self.get_argument("mapper_path", "wordcount/mapper.py")
        input_file = self.get_argument("input_file", "fish_jobs/0.in")
        num_reducers = int(self.get_argument("num_reducers", 3))
        map_output = [[] for _ in range(num_reducers)]
        with open(input_file,'r') as f:
            input_file_content = f.read()
        map_sub_process=subprocess.Popen([inventory.env,mapper_path],
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        (map_output_raw,_) = map_sub_process.communicate(input=input_file_content.encode())
        map_output_raw = map_output_raw.decode().strip().split('\n')
        map_output_raw = [x.strip().split('\t') for x in map_output_raw]
        #sorting the list
        map_output_raw.sort(key=lambda x: x[0])
        #hashing list and finding reducer partition
        for item in map_output_raw:
            reducer_partition = hash(item[0])%num_reducers
            map_output[reducer_partition].append(item)
        map_output_dict[task_id]=map_output
        display_info={}
        display_info['map_task_id'] = task_id
        display_info['status'] = 'success'
        self.write(json.dumps(display_info))

class MapperHandlerRetrieve(tornado.web.RequestHandler):
    def initialize(self, server_id):
        self.server_id = server_id

    @gen.coroutine
    def get(self):
        reducer_ix = int(self.get_argument("reducer_ix", 0))
        map_task_id = self.get_argument("map_task_id", "task_id")
        map_output = map_output_dict.get(map_task_id,[])
        if len(map_output)>reducer_ix:
            map_output_partition = map_output[reducer_ix]
        else:
            map_output_partition = []
        self.write(json.dumps(map_output_partition))

class ReducerHandler(tornado.web.RequestHandler):
    def initialize(self, server_id):
        self.server_id = server_id

    @gen.coroutine
    def get(self):
        reducer_ix = self.get_argument("reducer_ix", 0)
        reducer_path = self.get_argument("reducer_path", "wordcount/reducer.py")
        map_task_ids = self.get_argument("map_task_ids", "tsdk_id").split(',')
        job_path = self.get_argument("job_path", "fish_jobs")
        num_mappers = len(map_task_ids)
        http = AsyncHTTPClient()
        futures = []

        for i in range(num_mappers):
            server = inventory.worker_servers[i]
            params = urllib.parse.urlencode({'reducer_ix': reducer_ix,
                                             'map_task_id': map_task_ids[i]})
            url = "http://%s/retrieve_map_output?%s" % (server, params)
            #print("Fetching", url)
            http.fetch(url)
            futures.append(http.fetch(url))
        responses = yield futures

        kv_pairs = []
        for r in responses:
            #print(json.loads(r.body.decode()))
            kv_pairs.extend(json.loads(r.body.decode()))
        kv_pairs.sort(key=lambda x: x[0])

        kv_string = "\n".join([pair[0] + "\t" + pair[1] for pair in kv_pairs])
        p = subprocess.Popen(reducer_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        (out, _) = p.communicate(kv_string.encode())

        with open('{0}/{1}.out'.format(job_path,reducer_ix), "w") as f:
            f.write(out.decode())

        #print(out.decode())
        reducer_display_info = {'status':'success'}
        self.write(json.dumps(reducer_display_info))

def main():
    task_id = process.fork_processes(inventory.num_workers)
    #starting workers
    server_id = task_id
    app = tornado.web.Application([(r"/", DefaultHandler),
        (r"/map", MapperHandlerMap,dict(server_id=server_id)),
        (r"/retrieve_map_output", MapperHandlerRetrieve,dict(server_id=server_id)),
        (r"/reduce", ReducerHandler,dict(server_id=server_id))])
    app.listen(inventory.worker_ports[server_id])
    log.info("Worker "+str(server_id)+" listening on " + str(inventory.worker_ports[server_id]))
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s - %(asctime)s - %(message)s', level=logging.DEBUG)
    main()
    

