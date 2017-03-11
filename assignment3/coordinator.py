import os
import urllib
import urllib.request
import inventory
import json

mapper_path = 'wordcount/mapper.py'
reducer_path = 'wordcount/reducer.py'
job_path = 'oos_jobs' 
num_reducers = 4

#delete 0.out file if it exists
index = 0
task_ids = []
for input_file in os.listdir(job_path):
    input_file = '/'.join([job_path,input_file])
    if input_file.endswith('.in'):
        params = urllib.parse.urlencode({'mapper_path': mapper_path,
                                         'num_reducers': num_reducers,
                                         'input_file':input_file})
        server = inventory.mapper_servers[index]
        index += 1
        url = "http://%s/map?%s" % (server, params)
        print('fetching url:'+url)
        response = urllib.request.urlopen(url)
        mapper_response = json.loads(response.read().decode('utf-8'))
        status = mapper_response.get('status','')
        if status=='success':
            task_id = mapper_response.get('map_task_id')
            task_ids.append(task_id)

    else:
        os.remove(input_file)

for index in range(num_reducers):
    server = inventory.reducer_servers[index]
    params = urllib.parse.urlencode({'reducer_ix': index,
                                         'job_path': job_path,
                                         'reducer_path':reducer_path,
                                         'map_task_ids':','.join(task_ids)})
    url = "http://%s/reduce?%s" % (server, params)
    print('fetching url:'+url)
    response = urllib.request.urlopen(url)

        