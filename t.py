import numpy as np
import json
import argparse
import os
import gzip
import sys
import pickle
import time
from more_itertools import unique_everseen

train = pickle.load(open('/raid/brutusxu/ashleylan/item_category.pickle', 'rb'))
#test = pickle.load(open('/raid/brutusxu/ashleylan/test.pickle', 'rb'))
print(train.items())
sys.exit()

data = []

# with open(args.meta_path, 'r') as f:
# 	for line in f:
# 		eval_line = eval(line)
# 		if eval(line)['asin'] in item_dict.keys():
# 			meta_storage.append(eval_line)
with gzip.open("/raid/brutusxu/ashleylan/meta_Electronics.json.gz") as f:
    count = 0
    for l in f:
        l = eval(l)
        #data.append(json.dumps(l.strip()))
        data.append(l)
        count += 1
        if count == 5:
            break
           
           

#print(len(data))
print(data)

sys.exit()
test = pickle.load(open('/raid/brutusxu/ashleylan/ranklist.pickle', 'rb'))
print(list(test.items())[0:2])

