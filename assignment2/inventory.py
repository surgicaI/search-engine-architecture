BASE_PORT = 55700

index_partitions = 3
document_partitions = 3

items_to_display = 10

index_servers = ["http://linserv2.cims.nyu.edu:35315","http://linserv2.cims.nyu.edu:35316","http://linserv2.cims.nyu.edu:35317"]
doc_servers = ["http://linserv2.cims.nyu.edu:35318","http://linserv2.cims.nyu.edu:35319","http://linserv2.cims.nyu.edu:35320"]
frontend_port = "http://linserv2.cims.nyu.edu:"+str(BASE_PORT)
