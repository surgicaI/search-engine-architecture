## After a fresh clone please follow following steps.
* Run the code on linserv2.
* After loggin in on linserv2, use command "module load python-3.5.2"
* To create .in files for all MapReduce programs use following command in sea-assignments directory ie root folder.  
    ./assignment4/reformat_all.sh
* To start up MapReduce framework use following command in root folder.  
    python -m assignment3.workers
* To run three MapReduce jobs and generate all of the index files, use following command in root folder.  
    python -m assignment4.start
* To start up the search engine, use following command in root folder.  
    python -m assignment2.start
* Use the following url in browser to test the results  
    http://linserv2.cims.nyu.edu:55700/search?q=personalized
* To change the number of index or document partitions, change in assignment2.inventory
* To change the number of workers for map reduce, change in assignment3.inventory