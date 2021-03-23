
# Some libraries and options
import os
from sys import argv

# PF BB
import urllib
from urlparse import urlsplit
from aad_blob_helper import AadBlobHelper


import libscores
import yaml
from libscores import ls, filesep, mkdir, read_array, compute_all_scores, write_scores

# Blob Helper
blob_helper = AadBlobHelper()

# Default I/O directories:
root_dir = "/Users/isabelleguyon/Documents/Projects/ParisSaclay/Projects/ChaLab/Examples/iris/"
default_input_dir = root_dir + "scoring_input_1_2"
default_output_dir = root_dir + "scoring_output"

# Debug flag 0: no debug, 1: show all scores, 2: also show version amd listing of dir
debug_mode = 0

# Constant used for a missing score
missing_score = -0.999999

# Version number
scoring_version = 1.0


def _HERE(*args):
    h = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(h, *args)


def _load_scoring_function():
    with open(_HERE('metric.txt'), 'r') as f:
        metric_name = f.readline().strip()
        return metric_name, getattr(libscores, metric_name)

input_dir = '110-prediction-output'
output_dir = '/tmp/codalab/tmp7d9q7s/run/output'
solution_dir = '/data/challenges/iris-challenge-data/'

mkdir(output_dir)
# Get participant content
# blob_content = blob_helper.get_blob_to_text(input_dir, 'run1.log')

score_file = open(os.path.join(output_dir, 'scores.txt'), 'w')
html_file = open(os.path.join(output_dir, 'scores.html'), 'w')

# Get the metric
__file__ = 'scoring.py'
metric_name, scoring_function = _load_scoring_function()

# Get all the solution files from the solution directory
# solution_names = sorted(ls(os.path.join(input_dir, 'ref', '*.solution'))) # original
solution_names = sorted(ls(os.path.join(solution_dir, '*.solution')))


#------
set_num = 1
score_name = 'set%s_score' % set_num

blob_list = blob_helper.list_blobs(input_dir)
predict_file = [i for i in blob_list if '.predict' in i][-1]
predict_name = predict_file[:predict_file.find('.')]
solution_file = solution_names[0]
solution = read_array(solution_file)
blob_content_for_predict_file = blob_helper.get_blob_to_text(input_dir, predict_file)
prediction = read_array(blob_content_for_predict_file, blob=True)

score = scoring_function(solution, prediction)

print(
    "======= Set %d" % set_num + " (" + predict_name.capitalize() + "): score(" + score_name + ")=%0.12f =======" % score)
html_file.write(
    "======= Set %d" % set_num + " (" + predict_name.capitalize() + "): score(" + score_name + ")=%0.12f =======\n" % score)

score_file.write(score_name + ": %0.12f\n" % score)

try: # fails
    metadata = yaml.load(open(os.path.join(input_dir, 'res', 'metadata'), 'r'))
    score_file.write("Duration: %0.6f\n" % metadata['elapsedTime'])
except:
    score_file.write("Duration: 0\n")


html_file.close()
score_file.close()








