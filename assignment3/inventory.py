
env = "python"

num_workers = 4

mapper_ports = [55701,55702,55703,55704]
reducer_ports = [55711,55712,55713,55714]

#local servers for testing
mapper_servers = ["127.0.0.1:55701","127.0.0.1:55702","127.0.0.1:55703","127.0.0.1:55704"]
reducer_servers = ["127.0.0.1:55711","127.0.0.1:55712","127.0.0.1:55713","127.0.0.1:55714"]

#cims servers
#mapper_servers = ["linserv2.cims.nyu.edu:55701","linserv2.cims.nyu.edu:55702","linserv2.cims.nyu.edu:55703","linserv2.cims.nyu.edu:55704"]
#reducer_servers = ["linserv2.cims.nyu.edu:55711","linserv2.cims.nyu.edu:55712","linserv2.cims.nyu.edu:55713","linserv2.cims.nyu.edu:55713"]
