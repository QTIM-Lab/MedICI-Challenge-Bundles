#!/usr/bin/env python
import os
from sys import argv
import urllib
from urlparse import urlsplit
from aad_blob_helper import AadBlobHelper

if __name__ == "__main__":
    container_name = argv[1]  # #-prediction-output - azure blob
    output_dir = argv[2]  # /tmp/codalab/tmp######/run/output -

    blob_helper = AadBlobHelper()

    score_file = open(os.path.join(output_dir, 'scores.txt'), 'w')

    blob_content = blob_helper.get_blob_to_text(container_name, 'run1.log')

    html_file = open(os.path.join(output_dir, 'scores.html'), 'w')
    if 'iris_test.data' in blob_content: # looking for iris_test.data text in run1.log
        score_file.write('set1_score: 0.1\nset2_score: 0.2\nset3_score: 0.3')
        html_file.write("======= Run " + container_name +
                        " : score(Passed)=1.0 =======\n")
        score_file.close()
        html_file.close()
        exit(0)
    else:
        score_file.write('Passed: 0.0')
        html_file.write("======= Run " + container_name +
                        " : score(Passed)=0.0 =======\n")
        score_file.close()
        html_file.close()
        raise ValueError("Unable to find expected output.")

    exit(0)
