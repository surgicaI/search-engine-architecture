BASE_PORT = 55700

index_partitions = 3
document_partitions = 3

items_to_display = 10
items_returned_by_index_server = 10

WEIGHT_TO_TITLE = 100

index_server_ports = [55701,55702,55703]
doc_server_ports = [55704,55705,55706]

#servers provided as example in assignment
#index_servers = ["http://linserv2.cims.nyu.edu:35315","http://linserv2.cims.nyu.edu:35316","http://linserv2.cims.nyu.edu:35317"]
#doc_servers = ["http://linserv2.cims.nyu.edu:35318","http://linserv2.cims.nyu.edu:35319","http://linserv2.cims.nyu.edu:35320"]

#local servers
index_servers = ["http://127.0.0.1:55701","http://127.0.0.1:55702","http://127.0.0.1:55703"]
doc_servers = ["http://127.0.0.1:55704","http://127.0.0.1:55705","http://127.0.0.1:55706"]

#cims servers
#frontend_port = "http://linserv2.cims.nyu.edu:"+str(BASE_PORT)
#index_servers = ["http://linserv2.cims.nyu.edu:55701","http://linserv2.cims.nyu.edu:55702","http://linserv2.cims.nyu.edu:55703"]
#doc_servers = ["http://linserv2.cims.nyu.edu:55704","http://linserv2.cims.nyu.edu:55705","http://linserv2.cims.nyu.edu:55706"]

