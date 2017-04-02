#!/usr/bin/env python

import sys
import pickle
import math

data = sys.stdin.read()
data = data.strip().split('\n')
data = [item.split('\t') for item in data]
document_count = {}
idf = {}
doc_ids = set()
for item in data:
    term = item[0]
    doc_id = item[1]
    doc_ids.add(doc_id)
    document_count[term] = document_count.get(term,0) + 1

for k,v in document_count.items():
    idf[k] = math.log(len(doc_ids)/v)

pickled_idf = pickle.dumps(idf,protocol=pickle.HIGHEST_PROTOCOL)
sys.stdout.buffer.write(pickled_idf) 

