import os, pdb, shutil
from subprocess import Popen, PIPE
from zipfile import ZipFile

SERVICE_PRINCIPAL_APPID = "a7bcbc35-443a-45ce-93f4-4714321d7bb0"
SERVICE_PRINCIPAL_CLIENT_SECRET = "G1zr20Dzvf3dXIfU~60EOmL1~IZ_.J1azm"
REGISTRY = "codalabsubmissionregistry.azurecr.io"

# This is the real path
# docker_image_path = "/var/log/docker_images"
docker_image_path = "/home/bbearce/Documents/azure_codalab/MedICI-Challenge-Bundles/aks_MedNIST_bundle" # local development
temp_dir = '/tmp/codalab' # local development; should exist already
# task_args will come with these two keys already
task_args = {'file_name': 'mednist_docker_image.zip',
             'user':'24'}
unzip_dir = os.path.join(temp_dir,'tmp_unzip_dir')

def login(registry="codalabsubmissionregistry.azurecr.io"):
    login_cmd = "docker login {registry} --username {appid} --password {secret}".format(
        appid=SERVICE_PRINCIPAL_APPID, secret=SERVICE_PRINCIPAL_CLIENT_SECRET, registry=registry)

    process = Popen(login_cmd.split(" "), stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print("stdout: " + stdout)
    print("stderr: " + stderr)

def unzip():
    try:
        # pdb.set_trace()
        shutil.rmtree(unzip_dir)
    except:
        print('creating {} directory'.format(unzip_dir))
        os.mkdir(unzip_dir)
        shutil.copyfile(src=os.path.join(docker_image_path, task_args['file_name']),dst=os.path.join(unzip_dir, task_args['file_name']))
    with ZipFile(os.path.join(unzip_dir, task_args['file_name']), 'r') as zipObj:
        zipObj.extractall(path=unzip_dir)

def build(repo,image):
    tag = task_args['file_name'].replace('.zip','').replace('\n','').replace(' ','')
    tag = tag if tag[0] != '.' and tag[0] != '-' else tag[1:]
    try:
        os.chdir(unzip_dir)
    except:
        raise Exception('Can\'t get into {}'.format(unzip_dir))
    print('done')
    docker_build_cmd = "docker build -t {}/user_{}:{} .".format(repo,image,tag)
    process = Popen(docker_build_cmd.split(" "), stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print("stdout: " + stdout)
    print("stderr: " + stderr)

def push(repo,image):
    tag = task_args['file_name'].replace('.zip','').replace('\n','').replace(' ','')
    tag = tag if tag[0] != '.' and tag[0] != '-' else tag[1:]
    docker_push_cmd = "docker push {}/user_{}:{}".format(repo,image,tag)
    process = Popen(docker_push_cmd.split(" "), stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print("stdout: " + stdout)
    print("stderr: " + stderr)

def clean_up(repo,image):
    # Docker image
    tag = task_args['file_name'].replace('.zip','').replace('\n','').replace(' ','')
    tag = tag if tag[0] != '.' and tag[0] != '-' else tag[1:]
    docker_clean_up_cmd = "docker image rm {}/user_{}:{}".format(repo,image,tag)
    process = Popen(docker_clean_up_cmd.split(" "), stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print("stdout: " + stdout)
    print("stderr: " + stderr)
    # Zipfile and extracted directory
    try:
        # pdb.set_trace()
        os.chdir('../') # meant to bring you to path in variable `temp_dir`
        shutil.rmtree(unzip_dir)
        os.remove(os.path.join(docker_image_path, task_args['file_name']))
    except:
        raise Exception( "Can\'t find {} or {}".format( unzip_dir, os.path.join(docker_image_path, task_args['file_name']) ) )




login()
unzip()
build(REGISTRY,task_args['user'])
push(REGISTRY,task_args['user'])
clean_up(REGISTRY,task_args['user'])
