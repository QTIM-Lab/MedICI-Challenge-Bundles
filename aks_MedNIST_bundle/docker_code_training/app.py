import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import pdb

import torch
from torch.utils.data import Dataset, DataLoader

from monai.transforms import \
    Compose, LoadImage, AddChannel, ScaleIntensity, ToTensor, RandRotate, RandFlip, RandZoom

from monai.networks.nets import densenet121
from monai.metrics import compute_roc_auc


IN = '/mnt/in'
OUT = '/mnt/out'

# Read image filenames from the dataset folders
data_dir = IN
train_path = os.path.join(data_dir,'training-data')
val_path = os.path.join(data_dir,'validation-data')

# Prepare training, validation and test data lists
trainImages = []
trainLabels = []
validationImages = []
validationLabels = []

def initialize_training_set(which='training'):
    with open(os.path.join(data_dir,f'{which}_solution.csv'), 'r') as solution:
        for line in solution:
            if line[0:4] != 'file': # header check
                file, class_name = line.split(',')[0], line.split(',')[1].replace('\n','')
                if which == 'training':
                    trainImages.append(os.path.join(IN,file))
                    trainLabels.append(class_name)
                elif which == 'validation':
                    validationImages.append(os.path.join(IN,file))
                    validationLabels.append(class_name)

initialize_training_set('training')
initialize_training_set('validation')

class_names = set(validationLabels)
num_class = len(class_names)
label_key = {'AbdomenCT':0, 'BreastMRI':1, 'CXR':2, 'ChestCT':3, 'Hand':4, 'HeadCT':5}

trainLabels = [label_key[i] for i in trainLabels]
validationLabels = [label_key[i] for i in validationLabels]

# Define MONAI transforms, Dataset and Dataloader to pre-process data
train_transforms = Compose([
    LoadImage(image_only=True),
    AddChannel(),
    ScaleIntensity(),
    RandRotate(range_x=15, prob=0.5, keep_size=True),
    RandFlip(spatial_axis=0, prob=0.5),
    RandZoom(min_zoom=0.9, max_zoom=1.1, prob=0.5, keep_size=True),
    ToTensor()
])

val_transforms = Compose([
    LoadImage(image_only=True),
    AddChannel(),
    ScaleIntensity(),
    ToTensor()
])

class MedNISTDataset(Dataset):
    def __init__(self, image_files, labels, transforms):
        self.image_files = image_files
        self.labels = labels
        self.transforms = transforms
    def __len__(self):
        return len(self.image_files)
    def __getitem__(self, index):
        return self.transforms(self.image_files[index]), self.labels[index]

train_ds = MedNISTDataset(trainImages, trainLabels, train_transforms)
train_loader = DataLoader(train_ds, batch_size=100, shuffle=True, num_workers=5)

# Same pattern as train_ds, but we don't train on these. They also aren't used
val_ds = MedNISTDataset(validationImages, validationLabels, val_transforms)
val_loader = DataLoader(val_ds, batch_size=100, num_workers=5)

# Define network and optimizer
device = torch.device("cpu") #CPU
# device = torch.device("cuda:0") #GPU
model = densenet121(
    spatial_dims=2,
    in_channels=1,
    out_channels=num_class
).to(device)
loss_function = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), 1e-5)
epoch_num = 1
val_interval = 1

# Model training
best_metric = -1
best_metric_epoch = -1
epoch_loss_values = list()
metric_values = list()
print(epoch_num)
for epoch in range(epoch_num):
    print('-' * 10)
    print(f"epoch {epoch + 1}/{epoch_num}")
    model.train()
    epoch_loss = 0
    step = 0
    for batch_data in train_loader:
        step += 1
        inputs, labels = batch_data[0].to(device), batch_data[1].to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = loss_function(outputs, labels)
        loss.backward()
        optimizer.step()
        epoch_loss += loss.item()
        print(f"{step}/{len(train_ds) // train_loader.batch_size}, train_loss: {loss.item():.4f}")
        epoch_len = len(train_ds) // train_loader.batch_size
    epoch_loss /= step
    epoch_loss_values.append(epoch_loss)
    print(f"epoch {epoch + 1} average loss: {epoch_loss:.4f}")
    if (epoch + 1) % val_interval == 0:
        model.eval()
        with torch.no_grad():
            y_pred = torch.tensor([], dtype=torch.float32, device=device)
            y = torch.tensor([], dtype=torch.long, device=device)
            for val_data in val_loader:
                val_images, val_labels = val_data[0].to(device), val_data[1].to(device)
                y_pred = torch.cat([y_pred, model(val_images)], dim=0)
                y = torch.cat([y, val_labels], dim=0)
            auc_metric = compute_roc_auc(y_pred, y, to_onehot_y=True, softmax=True)
            metric_values.append(auc_metric)
            acc_value = torch.eq(y_pred.argmax(dim=1), y)
            acc_metric = acc_value.sum().item() / len(acc_value)
            if auc_metric > best_metric:
                best_metric = auc_metric
                best_metric_epoch = epoch + 1
                torch.save(model.state_dict(), os.path.join(OUT,'best_metric_model.pth'))
                print('saved new best metric model')
            print(f"current epoch: {epoch + 1} current AUC: {auc_metric:.4f}"
                  f" current accuracy: {acc_metric:.4f} best AUC: {best_metric:.4f}"
                  f" at epoch: {best_metric_epoch}")

print(f"train completed, best_metric: {best_metric:.4f} at epoch: {best_metric_epoch}")
