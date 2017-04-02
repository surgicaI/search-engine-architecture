import argparse
import xml.etree.ElementTree as etree
from nltk.tokenize import RegexpTokenizer

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file_name')
    parser.add_argument('--job_path',required=True)
    parser.add_argument('--num_partitions',type=int,required=True)
    args = parser.parse_args()

    file_name = args.file_name
    job_path = args.job_path
    num_partitions = args.num_partitions

    info_ret = etree.parse(file_name)
    root = info_ret.getroot()
    namespace = {'my_ns':'http://www.mediawiki.org/xml/export-0.10/'}

    site_info = root.find('my_ns:siteinfo', namespace)

    total_no_of_docs = float(len(root.findall('my_ns:page', namespace)))
    #taking care of case below if total_no_of_docs is not multiple of num_partitions
    docs_each_partition = int(total_no_of_docs/num_partitions)

    pages = root.findall('my_ns:page', namespace)
    #starting doc_id from 100
    doc_id = 100

    for i in range(num_partitions):
        root = etree.Element('root')
        root.append(site_info)
        start_index = i*docs_each_partition
        if i==num_partitions-1:
            end_index = int(total_no_of_docs)
        else:
            end_index = (i+1)*docs_each_partition
        for page in pages[start_index:end_index]:
            doc_id += 1
            etree.SubElement(page, "{http://www.mediawiki.org/xml/export-0.10/}doc_id").text = str(doc_id)
            root.append(page)
        tree = etree.ElementTree(root)
        tree.write(job_path+str(i)+'.in')


if __name__ == "__main__":
    main()