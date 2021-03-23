zip -j ingestion_program.zip ingestion_program/*;
zip -j input_data.zip sample_data/*;
zip -j reference_data.zip reference_data/*;
zip -j scoring_program.zip scoring_program/*;
zip -j starting_kit.zip starting_kit/*;

zip iris_docker_comp_bundle.zip \
    competition.yaml \
    data.html \
    evaluation.html \
    overview.html \
    terms.html \
    upload_docker_submission.html \
    logo.png \
    ingestion_program.zip \
    input_data.zip \
    reference_data.zip \
    scoring_program.zip \
    starting_kit.zip \
    zip_up.sh

# Create docker submission that can be built from inside first directory post unzip:
zip -j iris_docker_image_submission.zip \
    docker_code_submission/Dockerfile
zip -r iris_docker_image_submission.zip \
    sample_code_submission \
    ingestion_program