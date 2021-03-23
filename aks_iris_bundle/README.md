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

# Worker Compute (only need for scoring as participant ran model)
```bash
docker run \
  -it \
  --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /home/bbearce/Documents/azure_codalab/MedICI-Challenge-Bundles/aks_iris_bundle/:/tmp/codalab \
  -v /home/bbearce/Documents/azure_codalab/MedICI-Challenge-Bundles/aks_iris_bundle/sample_data:/data/challenges/iris-challenge-data/ \
  codalabinfrastructure.azurecr.io/aks-compute-worker:4 \
  bash
```

Set some env variables:
```bash
export AZURE_CLIENT_ID="a7bcbc35-443a-45ce-93f4-4714321d7bb0"
export AZURE_CLIENT_SECRET="G1zr20Dzvf3dXIfU~60EOmL1~IZ_.J1azm"
export AZURE_TENANT_ID="e72101ce-ef5d-49e3-baec-01191775dcc7"
export AZURE_ACCOUNT_NAME="mgbqtimcodalabstorage"
```

To score once in the container run:
```bash
cd /tmp/codalab;
program=scoring_program
input_scoring=output_folder;
output_scoring=output_scoring;
python $program/score.py $input_scoring $output_scoring
```

