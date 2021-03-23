zip -j scoring_program.zip scoring_program/*;
zip -jr public_data.zip public_data/*;
zip -j reference_data.zip reference_data/*;

zip mednist_comp_bundle.zip \
    competition.yaml \
    data.html \
    evaluation.html \
    overview.html \
    terms.html \
    upload_docker_submission.html \
    logo.png \
    public_data.zip \
    reference_data.zip \
    scoring_program.zip \
    zip_up.sh

# Create docker submission for TRAINING that can be built from inside first directory post unzip:
zip -j mednist_docker_image_training.zip \
    docker_code_training/Dockerfile \
    docker_code_training/app.py



# ...zip up INFERENCE image with "model_output"

# Create docker submission for INFERENCE that can be built from inside first directory post unzip:
zip -j mednist_docker_image_inference.zip \
    docker_code_inference/Dockerfile
zip -r mednist_docker_image_inference.zip \
    docker_code_inference/inference_on_test.py \
    model_output

# sleep docker
zip -j mednist_docker_image_inference_sleep.zip \
    docker_code_inference/Dockerfile
zip -r mednist_docker_image_inference_sleep.zip \
    docker_code_inference/inference_on_test.py \
    model_output