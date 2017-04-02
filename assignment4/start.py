import subprocess

env = 'python'

#for inverted index
subprocess.Popen([env, '-m', 'assignment3.coordinator', '--mapper_path=assignment4/mr_apps/invindex_mapper.py',
    '--reducer_path=assignment4/mr_apps/invindex_reducer.py', '--job_path=assignment4/invindex_jobs',
    '--num_reducers=3'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

#for document indexes
subprocess.Popen([env, '-m', 'assignment3.coordinator', '--mapper_path=assignment4/mr_apps/docs_mapper.py',
    '--reducer_path=assignment4/mr_apps/docs_reducer.py', '--job_path=assignment4/docs_jobs',
    '--num_reducers=3'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

#for idf
subprocess.Popen([env, '-m', 'assignment3.coordinator', '--mapper_path=assignment4/mr_apps/idf_mapper.py',
    '--reducer_path=assignment4/mr_apps/idf_reducer.py', '--job_path=assignment4/idf_jobs',
    '--num_reducers=3'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)