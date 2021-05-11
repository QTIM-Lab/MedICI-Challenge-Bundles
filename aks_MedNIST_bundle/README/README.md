# MedNIST

Clone repo:
```
git clone https://github.com/QTIM-Lab/MedICI-Challenge-Bundles.git
```

If you cloned this whole repo then we need to find our way to this directory:
## Linux and MacOS
```
cd MedICI-Challenge-Bundles/aks_MedNIST_bundle
```
## Windows
Change directories into ```.\MedICI-Challenge-Bundles\aks_MedNIST_bundle``` from your present working directory.

At this "root" level is where the following commands will be run.

# Docker Installation
[Official Docs](https://docs.docker.com/engine/install/)

> I noticed during Windows install that the WSL for linux might not properly install by default. In fact it may cause Windows to not install docker at all. If this is the case one thing that worked was to uncheck the "WSL" install option upon installation and install WSL separately. WSL stands for Windows Subsystem in Linux. Installing WSL and docker separately and then restarting the machine seemed to work.

Docker is not by default in the sudoers group on linux and maybe macOS. On linux and macOS you can run this command to add docker to the sudo group:
```
sudo usermod -aG docker $USER
```

On windows it works a little differently I believe and you need to add yourself to the docker group...further instructions are tbd.

# Training
## Build Training Docker Image:
```bash
docker build -f docker_code_training/Dockerfile -t medicichallenges/mednist:training docker_code_training;
```
## Run Training Image

```bash
mkdir model_output;
docker run \
  -it \
  --rm \
  --shm-size=256m \
  -v $PWD/input_data:/mnt/in \
  -v $PWD/model_output:/mnt/out \
  medicichallenges/mednist:training \
  python app.py
```
> Might take ~15 min

There should be a model in ```$PWD/model_output```, saved by ```torch.save(model.state_dict(), os.path.join(OUT,'best_metric_model.pth'))``` on line ~160


# Inference - Run by Challenge Platform

Now that you have a model created and saved, we need to package that up with inference code to do the inference phase.

Before we continue, the platform this will run on operates in a specific directory structure:

```
Submission Directory:
  |- input
    |- ref (This is the reference data unzipped - ground truth participants do not have access to)
    |- res (This is the user submission - classification_results.csv)
  |- program (This is the scoring program [and any included dependencies] unzipped)
  |- output (This is where the scores.txt file is written by the scoring program)
```
The only thing you need to worry about here is that your output from your inference calculation will end up in ```input/res```. The rest is for the challenge organizer. Later in the scoring section I will show how the ```program``` folder will have the score program in it and we will use it to show how scores are calculated.

So make this structure now and copy the score program and test phase reference data into the correct locations:
```
# create submission_directory
mkdir -p submission_directory/input/ref
mkdir -p submission_directory/input/res
mkdir -p submission_directory/program
mkdir -p submission_directory/output

# Load score program and testing solution
cp scoring_program/score.py submission_directory/program/
cp reference_data/testing_solution.csv submission_directory/input/ref/
```

## Build inference image (what participants submit)
```bash
docker build -f docker_code_inference/Dockerfile -t medicichallenges/mednist:inference .
```

```bash
docker run \
  -it \
  --rm \
  --shm-size=256m \
  -v $PWD/input_data/testing-data:/mnt/in \
  -v $PWD/submission_directory/input/res:/mnt/out \
  medicichallenges/mednist:inference \
  python inference_on_test.py
```

> You'll notice I mounted ```$PWD/submission_directory/input/res``` as discussed before in order to make sure the results of classification are available to the scoring program.

# Scoring - Run by Challenge Platform

Create mock scoring docker image for testing:

```bash
docker build -f scoring_program/Dockerfile -t local/score_image:latest scoring_program
```

Now run the score program:
```bash
docker run \
  -it \
  --rm \
  -v $PWD/submission_directory:$PWD/submission_directory \
  -w $PWD/submission_directory \
  local/score_image:latest
```

# Create submission for platform (website submission)

Zip up your inference model, Dockerfile and code into a *.zip file and upload to the platform:

```
zip -j mednist_docker_image_inference.zip \
    docker_code_inference/Dockerfile
zip -r mednist_docker_image_inference.zip \
    docker_code_inference/inference_on_test.py \
    model_output
```
