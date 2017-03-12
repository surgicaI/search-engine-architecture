env = "python"

num_workers = 4

#although there are 10 ports added in the list, the actual 
#number of servers will be configured by value of num_workers

worker_ports = [55701,55702,55703,55704,55705,55706,55707,55708,55709,55710]

#cims servers
worker_servers = ["linserv2.cims.nyu.edu:55701","linserv2.cims.nyu.edu:55702","linserv2.cims.nyu.edu:55703",
"linserv2.cims.nyu.edu:55704","linserv2.cims.nyu.edu:55705","linserv2.cims.nyu.edu:55706",
"linserv2.cims.nyu.edu:55707","linserv2.cims.nyu.edu:55708","linserv2.cims.nyu.edu:55709",
"linserv2.cims.nyu.edu:55710"]
