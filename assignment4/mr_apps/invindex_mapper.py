#!/usr/bin/env python

import sys, nltk
import xml.etree.ElementTree as etree
from nltk.tokenize import RegexpTokenizer

namespace = {'my_ns':'http://www.mediawiki.org/xml/export-0.10/'}

input_str = sys.stdin.read()
root = etree.fromstring(input_str)

for page in root.findall('my_ns:page', namespace):
    term_freq_dict ={}
    title = page.find('my_ns:title',namespace).text
    doc = page.find('my_ns:revision',namespace).find('my_ns:text',namespace).text
    doc_id = page.find('my_ns:doc_id',namespace).text
    tokenizer = RegexpTokenizer(r'\w+')
    text_tokens = tokenizer.tokenize(doc.lower())
    for token in text_tokens:
        term_freq_dict[token]=term_freq_dict.get(token,0)+1
    for k,v in term_freq_dict.items():
        print('%s\t%s,%s' % (doc_id, k, v))