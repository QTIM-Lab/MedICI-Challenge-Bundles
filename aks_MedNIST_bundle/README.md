# MedNIST

First we need to download the data:

```bash
wget -q https://www.dropbox.com/s/5wwskxctvcxiuea/MedNIST.tar.gz;
tar -zxf MedNIST.tar.gz;
mv MedNIST input_data_all;
```

# Build Docker Image:
```bash
docker build -f docker_code_training/Dockerfile -t medicichallenges/mednist:training .;
```

# Create Train, Validation and Test Splits and Solutions - Run by Challenge Organizer
```bash
cd ../;
mkdir -p input_data/training;
mkdir -p input_data/validation;
mkdir -p input_data/testing;

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


# Start docker for training - Run by Participant
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

# Inference - Run by Challenge Platform
```bash
docker run \
  -it \
  --rm \
  --shm-size=256m \
  -v $PWD/input_data:/mnt/in \
  -v $PWD/output_pred:/mnt/out \
  medicichallenges/mednist:inference_sleep \
  bash
```
##medicichallenges/mednist:inference


# Scoring - Run by Chalenge Platform
```bash
docker run \
  -it \
  --rm \
  -v $PWD/reference_data:/mnt/solution \
  -v $PWD/output_pred:/mnt/in \
  -v $PWD/output_scoring:/mnt/out \
  -v `pwd`:`pwd` \
  -w `pwd`/scoring_program \
  codalabinfrastructure.azurecr.io/aks-compute-worker:3 \
  bash
```
