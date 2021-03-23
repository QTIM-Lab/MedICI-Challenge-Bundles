# Build Docker Image

Get to ```docker_code_submission``` directory in the ```starting_kit``` directory.
```bash
cd /home/bbearce/Documents/azure_codalab/MedICI-Challenge-Bundles/aks_iris_bundle/docker_code_submission
```
> Note: Be sure output_folder has write permissions for all
```bash
chmod o+w ../output_folder
```

Build the image as whatever you want
```bash
docker build -f Dockerfile  -t medicichallenges/iris:latest ../
```

# Test Image
```bash
docker run \
  -it \
  --rm \
  -v /home/bbearce/Documents/azure_codalab/MedICI-Challenge-Bundles/aks_iris_bundle/sample_data:/mnt/inputdata \
  -v /home/bbearce/Documents/azure_codalab/MedICI-Challenge-Bundles/aks_iris_bundle/output_folder:/mnt/output \
  medicichallenges/iris:latest \
  bash
```
To test once inside container
```bash
input=/mnt/inputdata
output=/mnt/output
ingestion_program=ingestion_program
submission_program=sample_code_submission
python ingestion_program/ingestion.py $input $output $ingestion_program $submission_program
```

You should see output in output_folder:
```bash
irist_test.predict
irist_train.predict
irist_valid.predict
```
