#!/usr/bin/env python

import sys
import pickle

data = sys.stdin.read()
data = data.strip().split('\n')
data = [item.split('\t') for item in data]
doc_store = {}
for item in data:
    doc_id = item[0]
    [title, body] = item[1].split(',')
    title = '_'.join(title.split())
    doc_store[doc_id] = (title,body)

pickled_doc_store = pickle.dumps(doc_store,protocol=pickle.HIGHEST_PROTOCOL)
sys.stdout.buffer.write(pickled_doc_store) 

