import pandas as pd
import sys, os
import pdb

from sklearn.metrics import confusion_matrix

# As per CodaLab
# Submission Directory:
#   |- input
#     |- ref (This is the reference data unzipped)
#     |- res (This is the user submission unzipped)
#   |- program (This is the scoring program [and any included dependencies] unzipped)
#   |- output (This is where the scores.txt file is written by the scoring program)

# NOTE: this program is being run where you see 'program' in the above tree


input_dir = sys.argv[1] #/tmp/codalab/tmpZbR1Aj/run/input
output_dir = sys.argv[2] #/tmp/codalab/tmpZbR1Aj/run/output

# input_dir = 'input'
# output_dir = 'output'

# pdb.set_trace()
truth_dir = os.path.join(input_dir, 'ref')
submit_dir = os.path.join(input_dir, 'res')

# Test 0: make sure the submission/output directory is setup properly
if len(filter(lambda x: x != '__MACOSX' and x != 'metadata', os.listdir(submit_dir))) != 1:
    "This condition is tricky: so CodaLab drops a 'metadata' file in 'res'. "
    raise Exception('Incorrect number of files in the submission directory')

if not os.path.isdir(submit_dir):
    raise Exception("{} doesn't exist".format(submit_dir))

if os.path.isdir(submit_dir) and os.path.isdir(truth_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
# --

tru_file = os.path.join(truth_dir, os.listdir(truth_dir)[0])
inp_file = os.path.join(submit_dir, filter(lambda x: x != '__MACOSX' and x != 'metadata', os.listdir(submit_dir))[0])

# read data
inp_data = pd.read_csv(inp_file,sep=',')
tru_data = pd.read_csv(tru_file,sep=',')

# QA Test 1: tests for correct header
if 'key' not in inp_data.columns:
    raise Exception('ERROR. Can\'t find index column key.')
elif 'class' not in inp_data.columns:
    raise Exception('ERROR. Can\'t find class column.')

# QA Test 2: submitted results have less than or equal to 2 columns
if len(inp_data.columns)<2:
   raise Exception('ERROR. Input file has fewer than 2 columns: {}'.format(len(inp_data.columns)))

# QA Test 3: submitted results have same length
if len(inp_data)!=len(tru_data):
   raise Exception('ERROR. Input file is not the same length as ground truth file: {} != {}'.format(len(inp_data), len(tru_data)))

# QA Test 4: tests for duplicate rows
if len(inp_data.loc[:,'key'].unique()) < inp_data.shape[0]:
    raise Exception('ERROR. There are duplicate rows')

# QA Test 5: Keys between file match
inp_data = inp_data.sort_values(by=['key'])
tru_data = tru_data.sort_values(by=['key'])

for index, row in inp_data.iterrows():
    # QA: inner join like comparision to make sure each key is being compared to the same key
    inp_case = inp_data.iloc[index]['key']
    tru_case = tru_data.iloc[index]['key']
    if tru_case!=inp_case:
       print('ERROR. Input case does not match ground truth case: ',inp_case, ' != ', tru_case, 'at line: ', index)
       sys.exit(1)

correct = 0
for index, row in inp_data.iterrows():
    inp_case = inp_data.iloc[index]['class']
    tru_case = tru_data.iloc[index]['class']
    if inp_case == tru_case:
        correct += 1

# Scores 
p_correct = correct / float(len(tru_data['key']))

tn, fp, fn, tp = confusion_matrix(tru_data['class'], inp_data['class']).ravel()
sensitivity = tp / float(tp+fn)
specificity = tn / float(tn+fp)


# Create and populate output directory with score:
output_filename = os.path.join(output_dir, 'scores.txt')              
output_file = open(output_filename, 'wb')

detailed_results_filename = os.path.join(output_dir, 'detailed_results.html')
detail_file = open(detailed_results_filename, 'wb')

testing_results_filename = os.path.join("/tmp/codalab/docker_images", 'detailed_results.html')
testing_file = open(testing_results_filename, 'wb')

# output_file write
output_file.write('score_2:' + format(p_correct, '.3f') + '\n')
output_file.write('score_3:' + format(sensitivity, '.3f') + '\n')
output_file.write('score_4:' + format(specificity, '.3f') + '\n')
output_file.close()

detail_file.write('score_2:' + format(p_correct, '.3f') + '\n')
detail_file.write('score_3:' + format(sensitivity, '.3f') + '\n')
detail_file.write('score_4:' + format(specificity, '.3f') + '\n')
detail_file.close()

testing_file.write('score_2:' + format(p_correct, '.3f') + '\n')
testing_file.write('score_3:' + format(sensitivity, '.3f') + '\n')
testing_file.write('score_4:' + format(specificity, '.3f') + '\n')
testing_file.close()


# stdout write
sys.stdout.write('score_2:' + format(p_correct, '.3f') + '\n')
sys.stdout.write('score_3:' + format(sensitivity, '.3f') + '\n')
sys.stdout.write('score_4:' + format(specificity, '.3f') + '\n')

sys.exit(0)

