#!/usr/bin/env python

import sys
import pickle

data = sys.stdin.read()
data = data.strip().split('\n')
data = [item.split('\t') for item in data]
inverted_index = {}
for item in data:
    doc_id = int(item[0])
    [term, term_freq] = item[1].split(',')
    posting_list = inverted_index.get(term,[])
    posting_list.append((int(doc_id),int(term_freq)))
    inverted_index[term] = posting_list

pickled_inverted_index = pickle.dumps(inverted_index,protocol=pickle.HIGHEST_PROTOCOL)
sys.stdout.buffer.write(pickled_inverted_index) 

