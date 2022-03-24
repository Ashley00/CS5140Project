import pickle
import math
from tqdm import tqdm
import matplotlib.pyplot as plt
import sys
import numpy as np
import argparse
import os
import random
import copy
import time

parser = argparse.ArgumentParser()
parser.add_argument('--input_dir', type=str, default='/raid/brutusxu/ashleylan/')
parser.add_argument('--train_test_ratio', type=float, default=0.8)
parser.add_argument('--build_kge_pretrain', type=int, default=0)
args = parser.parse_args()

# read in file
train = pickle.load(open(os.path.join(args.input_dir,'train.pickle'), 'rb'))
print(len(train))

train_item_user = {}
for k,v in train.items():
	for item in v:
		if item not in train_item_user.keys():
			train_item_user[item] = [k]
		else:
			train_item_user[item].append(k)

print(len(train_item_user))
print(list(train_item_user.items())[0:2])
#sys.exit()

user_item = pickle.load(open(os.path.join(args.input_dir,'user_item.pickle'), 'rb'))
print(len(user_item))
item_user = pickle.load(open(os.path.join(args.input_dir,'user_item_rev.pickle'), 'rb'))
item_kv = pickle.load(open(os.path.join(args.input_dir,'item_kv.pickle'), 'rb'))
kv_item = pickle.load(open(os.path.join(args.input_dir,'item_kv_rev.pickle'), 'rb'))
item_brand = pickle.load(open(os.path.join(args.input_dir,'item_brand.pickle'), 'rb'))
brand_item = pickle.load(open(os.path.join(args.input_dir,'item_brand_rev.pickle'), 'rb'))
item_category = pickle.load(open(os.path.join(args.input_dir,'item_category.pickle'), 'rb'))
category_item = pickle.load(open(os.path.join(args.input_dir,'item_category_rev.pickle'), 'rb'))
also_bought = pickle.load(open(os.path.join(args.input_dir,'also_bought.pickle'), 'rb'))
also_bought_r = pickle.load(open(os.path.join(args.input_dir,'also_bought_rev.pickle'), 'rb'))
also_viewed = pickle.load(open(os.path.join(args.input_dir,'also_viewed.pickle'), 'rb'))
also_viewed_r = pickle.load(open(os.path.join(args.input_dir,'also_viewed_rev.pickle'), 'rb'))
#bought_together = pickle.load(open(os.path.join(args.input_dir,'bought_together.pickle'), 'rb'))
#bought_together_r = pickle.load(open(os.path.join(args.input_dir,'bought_together_rev.pickle'), 'rb'))


user_id = pickle.load(open(os.path.join(args.input_dir,'users.pickle'), 'rb'))
item_id = pickle.load(open(os.path.join(args.input_dir,'product.pickle'), 'rb'))
relateditem_id = pickle.load(open(os.path.join(args.input_dir,'related_product.pickle'), 'rb'))
brand_id = pickle.load(open(os.path.join(args.input_dir,'brand.pickle'), 'rb'))
category_id = pickle.load(open(os.path.join(args.input_dir,'category.pickle'), 'rb'))
kv_id = pickle.load(open(os.path.join(args.input_dir,'kv.pickle'), 'rb'))


with open(os.path.join(args.input_dir, 'entity2id.txt'), 'w') as f:
	length5 = len(user_id) + len(item_id) + len(kv_id) + len(brand_id) + len(category_id)
	f.write(str(length5)+'\n')
	for k,v in user_id.items():
		f.write('user'+str(k)+' '+str(k)+'\n')
	for k,v in item_id.items():
		f.write('item'+str(k)+' '+str(k)+'\n')
	for k,v in kv_id.items():
		f.write('kv'+str(k)+' '+str(k)+'\n')
	for k,v in brand_id.items():
		f.write('brand'+str(k)+' '+str(k)+'\n')
	for k,v in category_id.items():
		f.write('category'+str(k)+' '+str(k)+'\n')
		

with open(os.path.join(args.input_dir, 'relation2id.txt'), 'w') as f:
	f.write(str(10)+'\n')
	f.write('user_item'+' '+str(0)+'\n')
	f.write('item_user'+' '+str(1)+'\n')
	f.write('item_category'+' '+str(2)+'\n')
	f.write('category_item'+' '+str(3)+'\n')
	f.write('item_brand'+' '+str(4)+'\n')
	f.write('brand_item'+' '+str(5)+'\n')
	f.write('item_kv'+' '+str(6)+'\n')
	f.write('kv_item'+' '+str(7)+'\n')
	f.write('also_bought'+' '+str(8)+'\n')
	f.write('also_view'+' '+str(9)+'\n')
	#f.write('buy_together'+' '+str(10)+'\n')


	# edges = []
	# for i, row in enumerate(train):
	# 	#row = row[0]
	# 	for j, edge in enumerate(row):
	# 		# print(edge)

	# 		if edge[0] != edge[1] and list(edge) not in edges:
	# 			edges.append(list(edge))



with open(os.path.join(args.input_dir, 'train2id.txt'), 'w') as f:
	f.write(str(2686025)+'\n')
	train_item_user = {}
	for k,v in train.items():
		for item in v:
			f.write(str(k)+' '+str(item)+' '+str(0)+'\n')
			f.write(str(item)+' '+str(k)+' '+str(1)+'\n')
	
	# for k,v in train_item_user.items():
	# 	for item in v:
	# 		f.write(str(k)+' '+str(item)+' '+str(1)+'\n')

	for k,v in item_category.items():
		for item in v:
			f.write(str(k)+' '+str(item)+' '+str(2)+'\n')

	for k,v in category_item.items():
		for item in v:
			f.write(str(k)+' '+str(item)+' '+str(3)+'\n')

	for k,v in item_brand.items():
		for item in v:
			f.write(str(k)+' '+str(item)+' '+str(4)+'\n')
	
	for k,v in brand_item.items():
		for item in v:
			f.write(str(k)+' '+str(item)+' '+str(5)+'\n')

	
	for k,v in item_kv.items():
		for item in v:
			f.write(str(k)+' '+str(item)+' '+str(6)+'\n')
	
	for k,v in kv_item.items():
		for item in v:
			f.write(str(k)+' '+str(item)+' '+str(7)+'\n')
	
	for k,v in also_bought.items():
		for item in v:
			f.write(str(k)+' '+str(item)+' '+str(8)+'\n')
	
	for k,v in also_bought_r.items():
		for item in v:
			f.write(str(k)+' '+str(item)+' '+str(8)+'\n')

	for k,v in also_viewed.items():
		for item in v:
			f.write(str(k)+' '+str(item)+' '+str(9)+'\n')
	
	for k,v in also_viewed_r.items():
		for item in v:
			f.write(str(k)+' '+str(item)+' '+str(9)+'\n')

	# for k,v in bought_together.items():
	# 	for item in v:
	# 		f.write(str(k)+' '+str(item)+' '+str(10)+'\n')
	
	# for k,v in bought_together_r.items():
	# 	for item in v:
	# 		f.write(str(k)+' '+str(item)+' '+str(10)+'\n')
	# for i in edges:
	# 	f.write(str(i[0])+' '+str(i[1])+' '+str(0)+'\n')

