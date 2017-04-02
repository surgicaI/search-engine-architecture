#!/bin/bash

# This is just a template that demonstrates how you might set up your project. Feel free to edit this file.

python reformatter.py ../assignment2/info_ret.xml --job_path=idf_jobs/ --num_partitions=1
python reformatter.py ../assignment2/info_ret.xml --job_path=docs_jobs/ --num_partitions=3
python reformatter.py ../assignment2/info_ret.xml --job_path=invindex_jobs/ --num_partitions=3

