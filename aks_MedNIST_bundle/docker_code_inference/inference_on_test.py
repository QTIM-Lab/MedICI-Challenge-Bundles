import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image


import torch
from torch.utils.data import Dataset, DataLoader

# from monai.config import print_config
from monai.transforms import \
    Compose, LoadImage, AddChannel, ScaleIntensity, ToTensor, RandRotate, RandFlip, RandZoom

from monai.networks.nets import densenet121
from monai.metrics import compute_roc_auc

IN = '/mnt/in'
OUT = '/mnt/out'
data_dir = os.path.join(IN, 'testing')

on_platform = True
if on_platform:
    IN = '/mnt/inputdata/MedNIST'
    OUT = '/mnt/output'
    data_dir = os.path.join(IN)
num_class = 6

# Read image filenames from the dataset folders
image_files = [os.path.join(data_dir,x) for x in os.listdir(os.path.join(data_dir))]
label_key = {0: 'AbdomenCT', 1: 'BreastMRI', 2: 'CXR', 3: 'ChestCT', 4: 'Hand', 5: 'HeadCT'}
# reverse_label_key = {label_key[key]:key for key in label_key.keys()}

# Define MONAI transforms, Dataset and Dataloader to pre-process data

val_transforms = Compose([
    LoadImage(image_only=True),
    AddChannel(),
    ScaleIntensity(),
    ToTensor()
])

class MedNISTDataset(Dataset):
    def __init__(self, image_files, transforms):
        self.image_files = image_files
        self.transforms = transforms
    def __len__(self):
        return len(self.image_files)
    def __getitem__(self, index):
        return self.transforms(self.image_files[index])
        #return self.transforms(self.image_files[index]), self.image_files[index] # Kathi recommended this

test_ds = MedNISTDataset(image_files, val_transforms)
test_loader = DataLoader(test_ds, batch_size=300, num_workers=10)

# Define network and optimizer
device = torch.device("cpu")
model = densenet121(
    spatial_dims=2,
    in_channels=1,
    out_channels=num_class
).to(device)
loss_function = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), 1e-5)
epoch_num = 1
val_interval = 1

# model should be in memory and this step is really maybe only necessary during test run
model.load_state_dict(torch.load(os.path.join('best_metric_model.pth')))
model.eval()

y_pred = list()
# This is scoring territory as well
with torch.no_grad():
    data = 0
    for test_data in test_loader:
        print(f'data: {data}'); data += 1;
        test_images = test_data.to(device)
        # test_images, image_paths = test_data[0].to(device), test_data[1] # With Kathi's edit
        pred = model(test_images).argmax(dim=1)
        for i in range(len(pred)):
            y_pred.append(pred[i].item())
            # y_pred.append( (pred[i].item(), image_paths[i]) ) # With Kathi's edit

# Those edits from Kathi make output like:
# [(3, '/mnt/inputdata/MedNIST/000008.jpg'), (...)] # Here 3 is supposed to be 'ChestCT'
# label key = > label_key = {0: 'AbdomenCT', 1: 'BreastMRI', 2: 'CXR', 3: 'ChestCT', 4: 'Hand', 5: 'HeadCT'}

with open(os.path.join(OUT,'classification_results.csv'), 'w') as f:
    f.write(f'file,class\n')

with open(os.path.join(OUT,'classification_results.csv'), 'a') as f:
    for i,image in enumerate(image_files):
        f.write(f'{image},{label_key[y_pred[i]]}\n')
