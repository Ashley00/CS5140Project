import numpy as np
import math
import json
import gzip
import os
import pickle
import random
import math
from tqdm import tqdm
from more_itertools import unique_everseen

# read in three data sets
def readReviewData(path):
   review = []
   with gzip.open(path, 'r') as f:
      for l in f:
         review.append(json.loads(l.strip()))
   return review

def readMetaData(path):
	meta = []
	with gzip.open(path, 'r') as f:
		for l in f:
			l = eval(l)
			meta.append(l)
	return meta
   

def readMaveData(path):
   item_kv_dict = {}
   # index as key and kv pair as value
   # store every pair of kv
   kv_list = []
   items = []
   with open(path, 'r') as f:
	   for l in f:
		   line = json.loads(l.strip())
		   item = line['id']
		   items.append(item)
		   attributes = line['attributes']
		   # get each kv pair from attributes
		   for row in attributes:
			   key = row['key']
			   value = row['evidences'][0]['value']
			   pair = (key, value)
			   kv_list.append(pair)

			   if item not in item_kv_dict.keys():
				   item_kv_dict[item] = [pair]
			   else:
				   item_kv_dict[item].append(pair)
		   
   kv_list = list(unique_everseen(kv_list))
   return item_kv_dict, kv_list, items

def get_item_kv(item_dict, all_kv_dict):
	item_kv_dict = {}
	for key in item_dict.keys():
		if key in all_kv_dict.keys():
			item_kv_dict[key] = all_kv_dict[key]

	return item_kv_dict




def get_user_item_dict(review):
	"""
	build user & item dictionary
	return: user dictionary {u1:[i, i, i...], u2:[i, i, i...]}, similarly, item dictionary
	"""
	user_dict = {}
	item_dict = {}
	for row in review:
		user = row['reviewerID']
		item = row['asin']
		if user not in user_dict:
			user_dict[user] = [item]
		else:
			user_dict[user].append(item)
		if item not in item_dict:
			item_dict[item] = [user]
		else:
			item_dict[item].append(user)
	return user_dict, item_dict
# non index
def name2dicts(name_list):
	name_dict = {}
	count = 0
    # get key in dict
	for i in name_list:
		if i not in name_dict.keys():
			name_dict[i] = count
			count += 1
	return name_dict

def name2dict(name_list, index):
	name_dict = {}
	count = index
    # get key in dict
	for i in name_list:
		if i not in name_dict.keys():
			name_dict[i] = count
			count += 1
	return name_dict

def match_rating_date(user_item_dict, item_user_dict, review_path):
	user_item_date_dict = {}
	user_item_rating_dict = {}
	for i, line in enumerate(gzip.open(review_path, 'r')):
		record = json.loads(line)
		user = record['reviewerID']
		item = record['asin']
		rating = record['overall']
		date = record['unixReviewTime']
		if user in user_item_dict and item in user_item_dict[user] and (user, item) not in user_item_date_dict:
			user_item_date_dict[(user, item)] = date
		if (user, item) not in user_item_rating_dict.keys():
			user_item_rating_dict[(user, item)] = rating
	return user_item_rating_dict, user_item_date_dict

def get_filter(user_item_dict, item_user_dict, test_length):
	input_user = user_item_dict
	output_user = {}
	while True:
		if len(output_user) == len(input_user):
			return output_user, item_user_dict
		else:
			input_user = user_item_dict
			user_item_dict, item_user_dict = get_filter_rec(user_item_dict, item_user_dict, test_length)
			output_user = user_item_dict

# recursively filter out user item pair
def get_filter_rec(user_item_dict, item_user_dict, test_length):
	user_filter = {}
	item_filter = {}
	for user in user_item_dict.keys():
		items = user_item_dict[user]
		if len(items) >= test_length:
			user_filter[user] = user_item_dict[user]
		else:
			for i in items:
				if user in item_user_dict[i]:
					item_user_dict[i].remove(user)
	
	for item in item_user_dict.keys():
		users = item_user_dict[item]
		if len(users) >= 0:
			item_filter[item] = item_user_dict[item]
		else:
			for u in users:
				if item in user_filter[u]:
					user_filter[u].remove(item)
	return user_filter, item_filter
			

def get_train_test(user_item, item_dict):
	for i in range(500):
		flag = False
		# split train and test data
		train_dict = {}
		test_dict = {}
		train_item_set = ()
		random.seed(i)
		for key, value in user_item.items():
			user = key
			random.shuffle(value)
			thred = math.ceil(len(value)*0.7)
			train_items = value[:thred]
			test_items = value[thred:]
			train_dict[user] = train_items
			test_dict[user] = test_items
			train_item_set.add(train_items)
		
		if len(train_item_set) == len(item_dict):
			return train_dict, test_dict
			
		



		
		# train_items = train_dict.values()
		# for key, value in test_dict.items():
		# 	if flag == True:
		# 		break
		# 	for item in value:
		# 		if item not in train_items:
		# 			flag = True
		# 			break

		# if flag == False:
		# 	return train_dict, test_dict

	print('Error find train')
	# not find accurate train set
		
def get_train_test2(user_item, item_dict):
	train_dict = {}
	test_dict = {}
	
	for key, value in user_item.items():
		user = key
		random.shuffle(value)
		
		train_items = value
		test_items = value[0:1]
		train_dict[user] = train_items
		test_dict[user] = test_items
		
	return train_dict, test_dict
		
		
def get_brand_category(meta_storage):
	category_list = []
	brand_list = []

	for i, line in enumerate(meta_storage):
		#print(line.keys())
		if 'brand' in line.keys():
			brand_list.append(line['brand'])
		if 'category' in line.keys():
			categories = line['category']
			for category in categories:
				category_list.append(category)
		

	brand_list = list(unique_everseen(brand_list))
	category_list = list(unique_everseen(category_list))

	brand_dict = {brand:i for i, brand in enumerate(brand_list)}
	category_dict = {category:i for i, category in enumerate(category_list)}

	return brand_dict, category_dict

# for new meta set
def get_item_related2(user_list, item_list, meta_storage, item_dict):
	bought_together_dict = {k: set() for k,v in item_dict.items()}
	also_bought_dict = {k: set() for k,v in item_dict.items()}
	also_viewed_dict = {k: set() for k,v in item_dict.items()}
	item_brand_dict = {k: set() for k,v in item_dict.items()}
	item_category_dict = {k: set() for k,v in item_dict.items()}

	pbar = tqdm(total=len(meta_storage))
	for i, line in enumerate(meta_storage):
		current_item = line['asin']
		if current_item in item_list:
			if 'brand' in line.keys():
				#if current_item in item_brand_dict.keys():
				item_brand_dict[current_item].add(line['brand'])
			if 'category' in line.keys():
				categories = line['category']
				#if current_item in item_category_dict.keys():
				for category in categories:
					item_category_dict[current_item].add(category)

			if 'also_buy' in line.keys():
				also_bought = line['also_buy']
				for item in also_bought:
					if item in item_list:
						also_bought_dict[current_item].add(item)
			if 'also_view' in line.keys():
				also_view = line['also_view']
				for item in also_view:
					if item in item_list:
						also_viewed_dict[current_item].add(item)
		pbar.update(1)
	pbar.close()
	return item_brand_dict, item_category_dict, also_bought_dict, bought_together_dict, also_viewed_dict


def get_item_related(user_list, item_list, meta_storage, item_dict):
	bought_together_dict = {k: set() for k,v in item_dict.items()}
	also_bought_dict = {k: set() for k,v in item_dict.items()}
	also_viewed_dict = {k: set() for k,v in item_dict.items()}
	item_brand_dict = {k: set() for k,v in item_dict.items()}
	item_category_dict = {k: set() for k,v in item_dict.items()}

	#pbar = tqdm(total=len(meta_storage))
	for i, line in enumerate(meta_storage):
		current_item = line['asin']
		if current_item in item_brand_dict.keys():
			if 'brand' in line.keys():
				#if current_item in item_brand_dict.keys():
				item_brand_dict[current_item].add(line['brand'])
			if 'categories' in line.keys():
				categories = line['categories'][0]
				#if current_item in item_category_dict.keys():
				for category in categories:
					item_category_dict[current_item].add(category)

			# if 'also_buy' in related.keys():
			# 	also_bought = line['also_buy']
			# 	for item in also_bought:
			# 		if item in item_list:
			# 			also_bought_dict[current_item].add(item)
			# if 'also_view' in related.keys():
			# 	also_view = line['also_view']
			# 	for item in also_view:
			# 		if item in item_list:
			# 			also_viewed_dict[current_item].add(item)

			if 'related' in line.keys():
				related = line['related']
				if 'also_bought' in related.keys():
					also_bought = related['also_bought']
					for item in also_bought:
						if item in item_list:
							#if current_item in also_bought_dict.keys():
							also_bought_dict[current_item].add(item)
				if 'bought_together' in related.keys():
					bought_together = related['bought_together']
					for item in bought_together:
						if item in item_list:
							#if current_item in bought_together_dict.keys():
							bought_together_dict[current_item].add(item)
				if 'buy_after_viewing' in related.keys():
					also_viewed = related['buy_after_viewing']
					for item in also_viewed:
						if item in item_list:
							#if current_item in also_viewed_dict.keys():
							also_viewed_dict[current_item].add(item)
		#pbar.update(1)
	#pbar.close()
	return item_brand_dict, item_category_dict, also_bought_dict, bought_together_dict, also_viewed_dict

def write_out_file(path, name, dic):
    with open(os.path.join(path, name), 'wb') as fout:
        pickle.dump(dic, fout, protocol=pickle.HIGHEST_PROTOCOL)

def write_out_train_test(path, name, user_dict, train_dict, item_dict):
	num_dict = {}
	with open(os.path.join(path, name), 'wb') as fout:
		for k,v in train_dict.items():
			num_user = user_dict[k]
			num_items = []
			for item in v:
				num_items.append(item_dict[item])
			

			num_dict[num_user] = num_items
		
		#print(list(num_dict.items())[0:1])
		pickle.dump(num_dict, fout, protocol=pickle.HIGHEST_PROTOCOL)


def write_out_related(path, name, rev_item_dict, item_related_dict, related_dict):
	num_dict = {}
	with open(os.path.join(path, name), 'wb') as fout:
		for i,v in rev_item_dict.items():
			product = rev_item_dict[i]
			categories = list(item_related_dict[product])
			for item in categories:
				if i not in num_dict.keys():
					num_dict[i] = [related_dict[item]]
				else:
					num_dict[i].append(related_dict[item])
		pickle.dump(num_dict, fout, protocol=pickle.HIGHEST_PROTOCOL)

	rev_num_dict = {}
	for k,v in num_dict.items():
		for item in v:
			if item not in rev_num_dict.keys():
				rev_num_dict[item] = [k]
			else:
				rev_num_dict[item].append(k)

	rev_name = name[:-7] + '_rev' + '.pickle'	
	with open(os.path.join(path, rev_name), 'wb') as f:
		pickle.dump(rev_num_dict, f, protocol=pickle.HIGHEST_PROTOCOL)

	


def write_out_related_kv(path, name, rev_item_dict, item_related_dict, related_dict):
	num_dict = {}
	with open(os.path.join(path, name), 'wb') as fout:
		for i,v in rev_item_dict.items():
			product = rev_item_dict[i]
			if product in item_related_dict.keys():
				
				categories = list(item_related_dict[product])
			
				for item in categories:
					if i not in num_dict.keys():
						num_dict[i] = [related_dict[item]]
					else:
						num_dict[i].append(related_dict[item])

			
		pickle.dump(num_dict, fout, protocol=pickle.HIGHEST_PROTOCOL)

	# get reverse of relation
	rev_num_dict = {}
	for k,v in num_dict.items():
		for item in v:
			if item not in rev_num_dict.keys():
				rev_num_dict[item] = [k]
			else:
				rev_num_dict[item].append(k)

	rev_name = name[:-7] + '_rev' + '.pickle'
	with open(os.path.join(path, rev_name), 'wb') as f:
		pickle.dump(rev_num_dict, f, protocol=pickle.HIGHEST_PROTOCOL)