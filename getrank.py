from tqdm import tqdm
import pickle
import numpy as np
import argparse
import os
import sys
import random
from evaluate import *

parser = argparse.ArgumentParser()
parser.add_argument('--input_dir', type=str, default='/raid/brutusxu/ashleylan/')
parser.add_argument('--cutoff', type=int, default=20)
args = parser.parse_args()

# nd array(317881,100)

with open('/raid/brutusxu/ashleylan/test.pickle', 'rb') as f:
    qrel_map = pickle.load(f)

embedding = pickle.load(open(os.path.join(args.input_dir,'features.pickle'), 'rb'))
train_dict = pickle.load(open(os.path.join(args.input_dir,'train.pickle'), 'rb'))
all_user_item_dict = pickle.load(open(os.path.join(args.input_dir,'user_item.pickle'), 'rb'))
# item index starts with 192403
all_items = pickle.load(open(os.path.join(args.input_dir,'product.pickle'), 'rb'))

# for k,v in train_dict.items():
#     print(qrel_map[k] in train_dict[k])
#     time.sleep(0.1)
print(len(train_dict), len(qrel_map))

# get item that not in train_dict
# predict_dict = {}
# for user in train_dict.keys():
#     all_items = all_user_item_dict[user]
#     train_items = train_dict[user]
#     predict_items = list(set(all_items-set(train_items)))
#     predict_dict[user] = predict_items


rank_dict = {}
pbar = tqdm(total=2000)
count = 0
items = all_items.keys()
user_num = len(train_dict)
user_index = [i for i in range(user_num)]
random.shuffle(user_index)

for i in user_index:
    embed_user = embedding[i]
    # get corresponding items based on user id
    #items = all_user_item_dict[i]
    scores = []
    for item in items:
        embed_item = embedding[item]
        score = np.dot(embed_user, embed_item)
        scores.append(score)
    # index = np.argsort(np.array(scores))[::-1][:100].tolist()
    index = np.argsort(np.array(scores))[::-1][:args.cutoff].tolist()
    true_index = [x+user_num for x in index]


    # item_in_train = train_dict[i]
    # for ind in item_in_train:
    #     if ind in true_index:
    #         true_index.remove(ind)
        
    rank_dict[i] = true_index

    #print(index)
    count +=1
    if count == 2000:
        break
    

    pbar.update(1)

pbar.close()

with open('/raid/brutusxu/ashleylan/test.pickle', 'rb') as f:
    qrel_map = pickle.load(f)

print_metrics_with_rank_cutoff(rank_dict, qrel_map, 1000)


# with open(os.path.join(args.input_dir, 'ranklist.pickle'), 'wb') as f:
	# pickle.dump(rank_dict, f, protocol=pickle.HIGHEST_PROTOCOL)