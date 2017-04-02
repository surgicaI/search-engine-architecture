#!/usr/bin/env python

import sys, nltk
import xml.etree.ElementTree as etree
from nltk.tokenize import RegexpTokenizer

namespace = {'my_ns':'http://www.mediawiki.org/xml/export-0.10/'}

input_str = sys.stdin.read()
root = etree.fromstring(input_str)

for page in root.findall('my_ns:page', namespace):
    doc_id = page.find('my_ns:doc_id',namespace).text
    title = page.find('my_ns:title',namespace).text

    doc = page.find('my_ns:revision',namespace).find('my_ns:text',namespace).text
    tokenizer = RegexpTokenizer(r'\w+')
    text_tokens = tokenizer.tokenize(doc.lower())
    body = " ".join(text_tokens)

    print('%s\t%s,%s' % (doc_id, title, body))