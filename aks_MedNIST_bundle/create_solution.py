import os
from PIL import Image
from shutil import copyfile
import pdb
import numpy as np
import pandas as pd

data_dir = './input_data_all'
out = './reference_data'
participant_data_directory = './input_data'



def main():
    class_names = sorted([x for x in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, x))])
    num_class = len(class_names)
    image_files = [[os.path.join(data_dir, class_name, x) 
                    for x in os.listdir(os.path.join(data_dir, class_name))] 
                for class_name in class_names]

    # test = [[i for i in ilist if i.find('000001') != -1] for ilist in image_files][0:5]
    # print(test) # There should only be one file named 000001.jpg, but there are more.

    # Rename files so they are all distinct
    img_number = 0
    for class_image_list in image_files:
        for image in class_image_list:
            img_number += 1
            image_path = image[:image.rfind('/')]
            old_image_name = image[image.rfind('/')+1:]
            new_image_name = str(img_number).rjust(6,'0')+".jpg"
            os.rename(os.path.join(image), os.path.join(image_path,new_image_name))

    # Redefine image list variable
    image_files = [[os.path.join(data_dir, class_name, x) 
                    for x in os.listdir(os.path.join(data_dir, class_name))] 
                for class_name in class_names]

    # test = [[i for i in ilist if i.find('000001') != -1] for ilist in image_files][0:5]
    # print(test) # There should only be one file named 000001.jpg

    label_key = {0: 'AbdomenCT', 1: 'BreastMRI', 2: 'CXR', 3: 'ChestCT', 4: 'Hand', 5: 'HeadCT'}

    image_file_list = []
    image_label_list = []
    for i, class_name in enumerate(class_names):
        image_file_list.extend(image_files[i])
        image_label_list.extend([i] * len(image_files[i]))

    with open(os.path.join(out,'solution.csv'), 'w') as f:
            f.write('image,class\n')

    for (file,label) in zip(image_file_list, image_label_list):
        with open(os.path.join(out,'solution.csv'), 'a') as f:
            f.write(f'{file},{label_key[label]}\n')

    num_total = len(image_label_list)
    image_width, image_height = Image.open(image_file_list[0]).size

    print('Total image count:', num_total)
    print("Image dimensions:", image_width, "x", image_height)
    print("Label names:", class_names)
    print("Label counts:", [len(image_files[i]) for i in range(num_class)])

    # Prepare training, validation and test data lists
    valid_frac, test_frac = 0.1, 0.1
    trainX, trainY = [], []
    valX, valY = [], []
    testX, testY = [], []

    for i in range(num_total):
        rann = np.random.random()
        if rann < valid_frac:
            valX.append(image_file_list[i])
            valY.append(image_label_list[i])
        elif rann < test_frac + valid_frac:
            testX.append(image_file_list[i])
            testY.append(image_label_list[i])
        else:
            trainX.append(image_file_list[i])
            trainY.append(image_label_list[i])

    print("Training count =",len(trainX),"Validation count =", len(valX), "Test count =",len(testX))

    # Split/Solution creation function
    def write_solution(which='training'):
        variable_key = {'training':(trainX,trainY),
                        'validation':(valX,valY),
                        'testing':(testX,testY)}
        files, labels = variable_key[which]
        with open(os.path.join(out,f'{which}_solution.csv'), 'w') as f:
            f.write('file,class\n')
        with open(os.path.join(out,f'{which}_solution.csv'), 'a') as f:
            for (file,label) in zip(files,labels):
                file_new = file[file.rfind('/')+1:]
                tag = '-data' # Couldn't add to f{} string directly
                f.write(f'{os.path.join(which+tag,file_new)},{label_key[label]}\n')

    # Train
    write_solution(which='training')
    # Validation
    write_solution(which='validation')
    # Test
    write_solution(which='testing')

    # Move data to correct location for participants
    # Training solution they can have so move to participant_data_directory "input_data"
    # Same for Validation
    copyfile(os.path.join(out,'training_solution.csv'), 
            os.path.join(participant_data_directory,'training_solution.csv'))

    copyfile(os.path.join(out,'validation_solution.csv'), 
            os.path.join(participant_data_directory,'validation_solution.csv'))

    copyfile(os.path.join(out,'testing_solution.csv'), 
            os.path.join(participant_data_directory,'testing_solution.csv'))

    # Actual Training\Validation\Test data move
    def move_data(which='training'):
        variable_key = {'training':trainX,
                        'validation':valX,
                        'testing':testX}
        files = variable_key[which]
        for i,file in enumerate(files):
            i += 1;
            file_name = file[file.rfind('/')+1:]
            copyfile(os.path.join(file), os.path.join(participant_data_directory,which+"-data",file_name)) # I think this is new correct naming convention

    move_data('training')
    move_data('validation')
    move_data('testing')

def make_dataset_smaller(which='training'):
    # delete all but 600 images from the data from the solution csv
    sol = pd.read_csv("input_data/"+which+"_solution.csv")
    sol = sol.sort_values("file")
    # pdb.set_trace()
    new_sol = pd.DataFrame()
    classes = list(sol['class'].unique())
    for c in classes:
        new_sol = new_sol.append(sol[sol['class'] == c].iloc[0:100,:])
    # delete all but 600 images from the data folder
    # pdb.set_trace()
    delete_t_set = list(set(sol['file']) - set(new_sol['file']))
    for i in delete_t_set:
        os.remove('input_data/'+i)
    os.remove("input_data/"+which+"_solution.csv")
    new_sol.to_csv("input_data/"+which+"_solution.csv", index=None)


# make_smaller = True
# if make_smaller == True:
#     make_dataset_smaller()

if __name__ == "__main__":
    main()