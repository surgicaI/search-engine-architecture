import pickle
import xml.etree.ElementTree as etree
import inventory as inv
from nltk.tokenize import RegexpTokenizer
import unicodedata

#function definitions
def addToInvertedIndex(key,dict,doc_id):
    if key in dict:
        list = dict[key]
        id,freq = list[-1]
        if id == doc_id:
            list[-1] = (id,freq+1)
        else:
            id_freq_tuple = (doc_id,1)
            list.append(id_freq_tuple)
    else:
        list = []
        id_freq_tuple = (doc_id,1)
        list.append(id_freq_tuple)
        dict[key] = list

#for parsing xml
info_ret = etree.parse('info_ret.xml')
root = info_ret.getroot()
namespace = {'my_ns':'http://www.mediawiki.org/xml/export-0.10/'}

#indexer output
inverted_indices = []
for i in range(0,inv.index_partitions):
    inverted_indices.append({})

#iterating over documents and creating inverted index
for page in root.findall('my_ns:page', namespace):
    title = page.find('my_ns:title',namespace).text
    doc_id = page.find('my_ns:id',namespace).text
    doc = page.find('my_ns:revision',namespace).find('my_ns:text',namespace).text
    #convert form unicode to string
    if isinstance(doc,unicode) :
        doc = unicodedata.normalize('NFKD', doc).encode('ascii','ignore')
    #removing punctuation and tokenizing
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(doc)
    #adding to dictionary
    doc_id_hash = (int(doc_id))%inv.index_partitions
    dict = inverted_indices[doc_id_hash]
    for token in tokens:
        addToInvertedIndex(token,dict,doc_id)

#pickled dictionary saved in file
index = 1
for dict in inverted_indices:
    with open('inverted_index'+str(index)+'.pickle', 'wb') as handle:
        pickle.dump(dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    index+=1




