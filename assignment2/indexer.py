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

#indexer output, inverted indices, list of dictionaries
inverted_indices = []
for i in range(0,inv.index_partitions):
    inverted_indices.append({})
#indexer output, document stores, list of dictionaries
document_stores = []
for i in range(0,inv.document_partitions):
    document_stores.append({})

#iterating over documents and creating inverted index
for page in root.findall('my_ns:page', namespace):
    #reading title
    title = page.find('my_ns:title',namespace).text
    #reading url
    base_url = "https://en.wikipedia.org/wiki/"
    #reading doc_id and converting it to int
    doc_id = page.find('my_ns:id',namespace).text
    doc_id = int(doc_id)
    #reading doc text
    doc = page.find('my_ns:revision',namespace).find('my_ns:text',namespace).text
    #convert form unicode to string
    if isinstance(doc,unicode) :
        doc = unicodedata.normalize('NFKD', doc).encode('ascii','ignore')
    #removing punctuation and tokenizing
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(doc)
    #adding to dictionary for inverted index
    doc_id_hash = doc_id%inv.index_partitions
    dict = inverted_indices[doc_id_hash]
    for token in tokens:
        addToInvertedIndex(token,dict,doc_id)
    #adding to dictionary for document stores
    document_store_dict = document_stores[doc_id_hash]
    new_dict = {}
    new_dict['title'] = title
    new_dict['url'] = base_url+'_'.join(title.split())
    new_dict['text'] = doc
    document_store_dict[doc_id] = new_dict

#pickled dictionary saved in file
index = 0
for dict in inverted_indices:
    with open('inverted_index'+str(index)+'.pickle', 'wb') as handle:
        pickle.dump(dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    index+=1
index = 0
for dict in document_stores:
    with open('document_stores'+str(index)+'.pickle', 'wb') as handle:
        pickle.dump(dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    index+=1




