#!/bin/bash

# This is just a template that demonstrates how you might set up your project. Feel free to edit this file.

python -m assignment4.reformatter assignment2/info_ret.xml --job_path=assignment4/idf_jobs/ --num_partitions=1
python -m assignment4.reformatter assignment2/info_ret.xml --job_path=assignment4/docs_jobs/ --num_partitions=3
python -m assignment4.reformatter assignment2/info_ret.xml --job_path=assignment4/invindex_jobs/ --num_partitions=3

