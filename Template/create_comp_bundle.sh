
# [1] Ground Truths
zip -j training_data.zip training_data_gt/*
zip -j validation_data.zip validation_data_gt/*
zip -j test_data.zip test_data_gt/*

# [2] Evaluation Scripts
zip -j evaluation_script.zip evaluation_script/*

# [3] Bundle

zip -j Template_Competition_Bundle_2020.zip competition.yaml data.html evaluation.html overview.html terms_and_conditions.html upload_docker_submission.html logo.jpg test_data.zip evaluation_script.zip training_data.zip validation_data.zip

# [3] Create Data submission
zip -j sample_data_submission.zip sample_submission/*

# [4] Create Docker Submission Zip

zip -j docker_submission_v1.zip \
       docker_submission_template/Dockerfile \
       docker_submission_template/submission.py