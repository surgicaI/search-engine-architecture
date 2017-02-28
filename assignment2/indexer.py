import pickle
import xml.etree.ElementTree as etree
import inventory as inv
from nltk.tokenize import RegexpTokenizer
import unicodedata
import re
import os.path

#function definitions
def addToInvertedIndex(key,dict,doc_id,weight=1):
    if key in dict:
        list = dict[key]
        id,freq = list[-1]
        if id == doc_id:
            list[-1] = (id,freq+weight)
        else:
            id_freq_tuple = (doc_id,weight)
            list.append(id_freq_tuple)
    else:
        list = []
        id_freq_tuple = (doc_id,weight)
        list.append(id_freq_tuple)
        dict[key] = list

def start_indexing():
    #if pickled files are already present no need to index again
    already_indexed = True
    for i in range(0,inv.index_partitions):
        file_name = 'inverted_index'+str(i)+'.pickle'
        if not os.path.isfile(file_name):
            already_indexed = False
            break
    if already_indexed:
        for i in range(0,inv.document_partitions):
            file_name = 'document_stores'+str(i)+'.pickle'
            if not os.path.isfile(file_name):
                already_indexed = False
                break
    if already_indexed:
        return
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

    #starting doc_id from 100
    doc_id = 100

    #iterating over documents and creating inverted index
    for page in root.findall('my_ns:page', namespace):
        #reading title
        title = page.find('my_ns:title',namespace).text
        #reading url
        base_url = "https://en.wikipedia.org/wiki/"
        #incrementing doc_id 
        doc_id += 1
        #reading doc text
        doc = page.find('my_ns:revision',namespace).find('my_ns:text',namespace).text
        #convert form unicode to string
        #if isinstance(doc,unicode) :
            #doc = unicodedata.normalize('NFKD', doc).encode('ascii','ignore')
        #removing punctuation and tokenizing after converting to lower case
        tokenizer = RegexpTokenizer(r'\w+')
        text_tokens = tokenizer.tokenize(doc.lower())
        #adding to dictionary for inverted index
        doc_id_hash = doc_id%inv.index_partitions
        dict = inverted_indices[doc_id_hash]
        for token in text_tokens:
            addToInvertedIndex(token,dict,doc_id)
        #removing special symbols and numbers from title (is it required ?)
        #title = re.sub('\W+',' ', title)
        #adding Title to inverted index and giving it extra weight
        title_tokens = title.split()
        #adding lowercase in side forloop so that title and url contains exact same case as title
        for title_token in title_tokens:
            addToInvertedIndex(title_token.lower(),dict,doc_id,weight=inv.WEIGHT_TO_TITLE)
        #adding to dictionary for document stores
        doc_id_hash = doc_id%inv.document_partitions
        document_store_dict = document_stores[doc_id_hash]
        new_dict = {}
        new_dict['title'] = title
        new_dict['url'] = base_url+'_'.join(title_tokens)
        new_dict['text'] = " ".join(text_tokens)
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

