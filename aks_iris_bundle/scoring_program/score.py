#!/usr/bin/env python

# Scoring program for the AutoML challenge
# Isabelle Guyon and Arthur Pesah, ChaLearn, August 2014-November 2016

# ALL INFORMATION, SOFTWARE, DOCUMENTATION, AND DATA ARE PROVIDED "AS-IS".
# ISABELLE GUYON, CHALEARN, AND/OR OTHER ORGANIZERS OR CODE AUTHORS DISCLAIM
# ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR ANY PARTICULAR PURPOSE, AND THE
# WARRANTY OF NON-INFRINGEMENT OF ANY THIRD PARTY'S INTELLECTUAL PROPERTY RIGHTS.
# IN NO EVENT SHALL ISABELLE GUYON AND/OR OTHER ORGANIZERS BE LIABLE FOR ANY SPECIAL,
# INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF SOFTWARE, DOCUMENTS, MATERIALS,
# PUBLICATIONS, OR INFORMATION MADE AVAILABLE FOR THE CHALLENGE.

# Some libraries and options
import os, pdb
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


# =============================== MAIN ========================================

if __name__ == "__main__":

    #### INPUT/OUTPUT: Get input and output directory names
    # Default I/O directories:
    input_dir = container_name = argv[1] # BB - Becomes "#-prediction-output" - azure blob
    output_dir = argv[2]                 # BB - /tmp/codalab/tmp######/run/output
    solution_dir = '/data/challenges/iris-challenge-data/'

    testing = False

    if testing:
        input_dir = container_name = "xx-prediction-output" # BB - Becomes "#-prediction-output" - azure blob
        output_dir = argv[2]                 # BB - /tmp/codalab/tmp######/run/output
        solution_dir = '/data/challenges/iris-challenge-data/'

    # Create the output directory, if it does not already exist and open output files
    mkdir(output_dir)
    # Get participant content
    # blob_content = blob_helper.get_blob_to_text(input_dir, 'run1.log')

    score_file = open(os.path.join(output_dir, 'scores.txt'), 'w')
    html_file = open(os.path.join(output_dir, 'scores.html'), 'w')

    # Get the metric
    metric_name, scoring_function = _load_scoring_function()

    # Get all the solution files from the solution directory
    # solution_names = sorted(ls(os.path.join(input_dir, 'ref', '*.solution'))) # original
    solution_names = sorted(ls(os.path.join(solution_dir, '*.solution')))
    # Loop over files in solution directory and search for predictions with extension .predict having the same basename
    for i, solution_file in enumerate(solution_names):
        set_num = i + 1  # 1-indexed
        score_name = 'set%s_score' % set_num

        # Extract the dataset name from the file name
        basename = solution_file[-solution_file[::-1].index(filesep):-solution_file[::-1].index('.') - 1]

        try:
            # Get the last prediction from the res subdirectory (must end with '.predict')
            blob_list = blob_helper.list_blobs(input_dir)
            # predict_file = ls(os.path.join(input_dir, 'res', basename + '*.predict'))[-1] # original
            predict_file = [i for i in blob_list if '.predict' in i][-1]
            if (predict_file == []): raise IOError('Missing prediction file {}'.format(basename))
            # predict_name = predict_file[-predict_file[::-1].index(filesep):-predict_file[::-1].index('.') - 1] # original
            predict_name = predict_file[:predict_file.find('.')]
            # Read the solution and prediction values into numpy arrays
            solution = read_array(solution_file)

            # BB - had to read file first and send data to read_array
            blob_content_for_predict_file = blob_helper.get_blob_to_text(input_dir, predict_file)
            prediction = read_array(blob_content_for_predict_file, blob=True) # changed to accept blob parameters
            if (solution.shape != prediction.shape): raise ValueError(
                "Bad prediction shape. Prediction shape: {}\nSolution shape:{}".format(prediction.shape, solution.shape))

            try:
                # Compute the score prescribed by the metric file
                score = scoring_function(solution, prediction)
                print(
                    "======= Set %d" % set_num + " (" + predict_name.capitalize() + "): score(" + score_name + ")=%0.12f =======" % score)
                html_file.write(
                    "======= Set %d" % set_num + " (" + predict_name.capitalize() + "): score(" + score_name + ")=%0.12f =======\n" % score)
            except:
                raise Exception('Error in calculation of the specific score of the task')

            if debug_mode > 0:
                scores = compute_all_scores(solution, prediction)
                write_scores(html_file, scores)

        except Exception as inst:
            score = missing_score
            print(
                "======= Set %d" % set_num + " (" + basename.capitalize() + "): score(" + score_name + ")=ERROR =======")
            html_file.write(
                "======= Set %d" % set_num + " (" + basename.capitalize() + "): score(" + score_name + ")=ERROR =======\n")
            print(inst)

        # Write score corresponding to selected task and metric to the output file
        score_file.write(score_name + ": %0.12f\n" % score)

    # End loop for solution_file in solution_names

    # Read the execution time and add it to the scores:
    try:
        metadata = yaml.load(open(os.path.join(input_dir, 'res', 'metadata'), 'r'))
        score_file.write("Duration: %0.6f\n" % metadata['elapsedTime'])
    except:
        score_file.write("Duration: 1\n")

        html_file.close()
    score_file.close()

    # Lots of debug stuff
    if debug_mode > 1:
        swrite('\n*** SCORING PROGRAM: PLATFORM SPECIFICATIONS ***\n\n')
        show_platform()
        show_io(input_dir, output_dir)
        show_version(scoring_version)

        # exit(0)


    # Insert Patricks Code to talk to blobs and read prediction and create scores:

