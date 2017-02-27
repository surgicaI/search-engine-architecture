Instructions:
1. info_ret.xml file should be present in this directory, if indexer is not able to find this file it will throw error.
2. Type the command "python start.py"
3. This will first start the indexer and it will create inverted indices and document stores.
4. In case all the inverted indices and documents stores are already present in this directory it will skip this this and not index again.
5. After this step it will start 'N' Index servers and 'M' Document servers