import os

file = os.getcwd()
files = os.listdir(file)
for index,i in enumerate(files):
    if '.py' in i:
        continue
    os.rename(i,str(index) + '.txt')