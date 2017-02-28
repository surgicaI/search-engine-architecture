Instructions:
1. info_ret.xml file should be present in this directory, if indexer is not able to find this file it will throw error.
2. Type command "module load python-3.5.2" while running on cims server.
3. Type the command "python start.py"
4. This will first start the indexer and it will create inverted indices and document stores.
5. In case all the inverted indices and documents stores are already present in this directory it will skip this this and not index again.
6. After this step it will start 'N' Index servers and 'M' Document servers

Notes:
1. The extra weight to title is given during indexing itself. 
2. Run the code using python3 