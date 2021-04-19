# MedNIST

If you cloned this whole repo then we need to find our way to this directory:
```
MedICI-Challenge-Bundles/aks_MedNIST_bundle
```

At this "root" level is where the following commands will be run.

# Download Data
```bash
wget -q https://www.dropbox.com/s/5wwskxctvcxiuea/MedNIST.tar.gz;
tar -zxf MedNIST.tar.gz;
mv MedNIST input_data_all;
```

# Training (Tutorial In Progress)
## Build Training Docker Image:
```bash
docker build -f docker_code_training/Dockerfile -t medicichallenges/mednist:training .;
```

## Create Train, Validation and Test Splits and Solutions - Run by Challenge Organizer
```bash
cd ../;
mkdir -p input_data/training-data;
mkdir -p input_data/validation-data;
mkdir -p input_data/testing-data;

docker run \
  -it \
  --rm \
  --shm-size=256m \
  -v `pwd`:`pwd` \
  -w `pwd` \
  medicichallenges/mednist:training \
  bash
  python create_solution.py;
```


## Start docker for training - Run by Participant

> Note the training/validation splits from earlier are designed to be used for the training phase and the testing data for inference or final prediction phase.

```bash
cd ../;
docker run \
  -it \
  --rm \
  --shm-size=256m \
  -v $PWD/input_data:/mnt/in \
  -v $PWD/model_output:/mnt/out \
  medicichallenges/mednist:training \
  bash
```
Run ```python app.py```

There should be a model in ```$PWD/model_output```, saved by ```torch.save(model.state_dict(), os.path.join(OUT,'best_metric_model.pth'))``` on line ~160


# Inference - Run by Challenge Platform

Now that you have a model created and saved, we need to package that up with inference code to do the inference phase.

## Build first
```bash
docker build -f docker_code_inference/Dockerfile -t medicichallenges/mednist:inference .
```

```bash
docker run \
  -it \
  --rm \
  --shm-size=256m \
  -v $PWD/input_data/test-data:/mnt/in \
  -v $PWD/output_pred:/mnt/out \
  medicichallenges/mednist:inference \
  bash
```
<!-- CMD ["python", "inference_on_test.py"] -->
<!-- #medicichallenges/mednist:inference_sleep -->


# Scoring - Run by Challenge Platform
```bash
docker run \
  -it \
  --rm \
  -v $PWD/submission_directory:$PWD/submission_directory \
  -w $PWD/submission_directory \
  medicicodalabdev.azurecr.io/competitions-v1-compute-worker:docker \
  python $PWD/submission_directory/program/score.py $PWD/submission_directory/input $PWD/submission_directory/output
  # bash
```
<!-- -v $PWD/reference_data:/mnt/solution \ -->


docker run \
  --rm \
  -v /tmp/codalab/tmpZt7f5n/run:/tmp/codalab/tmpZt7f5n/run \
  -v /tmp/codalab/tmp_wvavE:/tmp/codalab/tmp_wvavE\
  -w /tmp/codalab/tmpZt7f5n/run \
  codalab/codalab-legacy:latest \
  python /tmp/codalab/tmpZt7f5n/run/program/score $results_container_name /tmp/codalab/tmpZt7f5n/run/output\

<!-- codalabinfrastructure.azurecr.io/aks-compute-worker:3 \ -->