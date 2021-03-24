import os, sys, pdb, random, time

# If in practice environment and will use relative path
#IN = "./mnt/in"
#OUT = "./mnt/out"

# For real environment. This is where your algorithm will read and write data
IN = "/mnt/in"
OUT = "/mnt/out"

input_file_name = os.listdir(IN)[0]
output_file_name = "output_data.csv"

classes = ['a','b']
if __name__ == "__main__":
    # Read from IN
    with open(os.path.join(IN,input_file_name), 'r') as input:
        lines = input.read()
        key = lines.split('\n')[1:]

    # Simulate an algorithm running
    for i in range(10):
        print(f"epoch: {i+1}")
        time.sleep(0)
    
    # Write to OUT
    with open(os.path.join(OUT,output_file_name), 'w') as output:
       output.write("key,class\n")
       for id in key:
           if int(id) == len(key):
               output.write(f"{id},{random.sample(classes,1)[0]}")
           else:
               output.write(f"{id},{random.sample(classes,1)[0]}\n")
    
    

