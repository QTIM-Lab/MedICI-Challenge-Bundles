#!/usr/bin/env python
import os, pdb, io
from sys import argv
import warnings
warnings.filterwarnings('ignore')
from sklearn.metrics import classification_report

# Submission Directory (/tmp/codalab/tmp######/run)
#   |- input
#     |- ref (This is the reference data unzipped)
#     |- res (This is the user submission unzipped)
#   |- program (This is the scoring program [and any included dependencies] unzipped)
#   |- output (This is where the scores.txt file is written by the scoring program)

# When run by codalab in standard form
# /tmp/codalab/tmp######/run is mounted so we have access to input, output and program

# Code is run like so:
#     python /tmp/codalab/tmpKKIydB/run/program/score.py \
#         /tmp/codalab/tmpKKIydB/run/input 
#         /tmp/codalab/tmpKKIydB/run/output

IN=argv[1] #/tmp/codalab/tmp######/run/input 
OUT=argv[2] #/tmp/codalab/tmp######/run/output 
PREDICTION_RESULTS=os.path.join(IN,"res")
REFERENCE=os.path.join(IN,"ref")

using_blob = False # True for kubernetes

score_file = open(os.path.join(OUT, 'scores.txt'), 'w')
html_file = open(os.path.join(OUT, 'scores.html'), 'w')

# Get soultion
solution_file = os.path.join(REFERENCE, 'testing_solution.csv')
soln_images = []
soln_classes = []

with open(solution_file, 'r') as soln:
    for i, image_class in enumerate(soln):
        if i == 0: #header skip
            pass
        else:
            image_class = image_class.replace('\n','')
            image = image_class.split(',')[0]
            image = image[image.rfind('/')+1:]
            _class = image_class.split(',')[1]
            soln_images.append(image)
            soln_classes.append(_class)

def get_predictions(pred):
    for i,image_class in enumerate(pred):
        if i == 0: #header check
            if image_class.replace('\n','') != 'file,class':
                raise Exception('Incorrect header, should be "file,class".')
        else:
            image_class = image_class.replace('\n','')
            image = image_class.split(',')[0]
            image = image[image.rfind('/')+1:]
            _class = image_class.split(',')[1]
            pred_images.append(image)
            pred_classes.append(_class)
    return pred_images, pred_classes

pred_images = []
pred_classes = []
# Running on infrastructure
if using_blob:
    pred = io.StringIO(unicode(blob_content))
    pred_images, pred_classes = get_predictions(pred)

# Running locally
else:
    prediction_files = [i for i in os.listdir(PREDICTION_RESULTS) if i.find('.csv') != -1]
    if len(prediction_files) != 1:
        raise Exception('Only one csv file allowed...{}'.format(prediction_files))
    else:
        with open(os.path.join(PREDICTION_RESULTS, prediction_files[0]), 'r') as pred:
            pred_images, pred_classes = get_predictions(pred)

# check for same number of images and classes
if len(pred_images) != len(soln_images):
    raise Exception('Expected {} images and got {}.'.format(len(soln_images), len(pred_images)))

if len(pred_classes) != len(soln_classes):
    raise Exception('Expected {} classes and got {}.'.format(len(soln_classes), len(pred_classes)))

# Loop through solution and find prediction and then update new prediction class array for scoring
synced_pred_classes = ['not updated']*len(pred_classes)
for i,image_s in enumerate(soln_images):
    for j,image_p in enumerate(pred_images):
        if image_s == image_p:
            synced_pred_classes[i] = pred_classes[j]
            # pdb.set_trace()

if 'not updated' in set(synced_pred_classes):
    raise Exception('Couldn\'t find a prediction for every test image')

report = classification_report(soln_classes, synced_pred_classes, target_names=set(soln_classes), digits=4, output_dict=True)

score_file.write('set1_score: {}\n'.format(report['weighted avg']['recall']))
score_file.write('set2_score: {}\n'.format(report['weighted avg']['f1-score']))
score_file.write('set3_score: {}\n'.format(report['weighted avg']['precision']))

# detailed results
report = classification_report(soln_classes, synced_pred_classes, target_names=set(soln_classes), digits=4)
html_file.write(report)

score_file.close()
html_file.close()

# set1_score: 0.9463343249097503
# set2_score: 0.9461839772566057
# set3_score: 0.9476273787699148

#   columns:
#     set1_score:
#       label: Recall
#       leaderboard: *id001
#       numeric_format: 3
#       rank: 1

#     set2_score:
#       label: F1 Score
#       leaderboard: *id001
#       numeric_format: 3
#       rank: 2

#     set3_score:
#       label: Precision
#       leaderboard: *id001
#       numeric_format: 3
#       rank: 3
      


# html_file = open(os.path.join(output_dir, 'scores.html'), 'w')
# if 'iris_test.data' in blob_content: # looking for iris_test.data text in run1.log
#     score_file.write('set1_score: 0.1\nset2_score: 0.2\nset3_score: 0.3')
#     html_file.write("======= Run " + container_name +
#                     " : score(Passed)=1.0 =======\n")
#     score_file.close()
#     html_file.close()
#     exit(0)
# else:
#     score_file.write('Passed: 0.0')
#     html_file.write("======= Run " + container_name +
#                     " : score(Passed)=0.0 =======\n")
#     score_file.close()
#     html_file.close()
#     raise ValueError("Unable to find expected output.")

# exit(0)
