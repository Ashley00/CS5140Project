import numpy as np
import json
import argparse
import os
import gzip
import sys
import time
from more_itertools import unique_everseen
from tqdm import tqdm

from util import *

# using parser
parser = argparse.ArgumentParser()
parser.add_argument('--review_path', type=str, default='/raid/brutusxu/ashleylan/Office_Products_5.json.gz')
parser.add_argument('--meta_path', type=str, default='/raid/brutusxu/ashleylan/meta_Office_Products.json.gz')
parser.add_argument('--mave_path', type=str, default='/raid/brutusxu/MAVE/reproduce/mave_positives.jsonl')
parser.add_argument('--output_dir', type=str, default='/raid/brutusxu/ashleylan')
args = parser.parse_args()

# set threshold
user_thresh = 5
item_thresh = 5
feature_thresh = 3
# interaction less then 5, delete
test_length = 5

#read in data sets
review = readReviewData(args.review_path)
meta = readMetaData(args.meta_path)
# example: ('B005DVV6RW', [('Maximum Players', 'For 2 players'), ('Recommended Age', 'Ages 6- Adult'), ('Age Group', 'Adult')])
all_kv_dict, kv_list, items = readMaveData(args.mave_path) 

print(len(all_kv_dict))

kv_dict = name2dicts(kv_list)
# [(0, ('Maximum Players', 'For 2 players')), (1, ('Recommended Age', 'Ages 6- Adult')), (2, ('Age Group', 'Adult'))]
rev_kv_dict = {v:k for k,v in kv_dict.items()}
print(len(rev_kv_dict))
print(list(all_kv_dict.items())[0:3])
print(kv_list[0])
print(len(kv_dict))
#review = readReviewData(args.review_path)
#preprocess data
user_item_dict, item_user_dict = get_user_item_dict(review)
user_dict = name2dict(user_item_dict,0)
item_dict = name2dict(item_user_dict,len(user_dict))
print(len(user_dict))
print(len(item_dict))
print(list(item_dict.items())[0])
#dict have index for each user
rev_user_dict = {v:k for k,v in user_dict.items()}
#dict have index for each item
rev_item_dict = {v:k for k,v in item_dict.items()}



item_kv_dict = get_item_kv(item_dict, all_kv_dict)
print(len(item_kv_dict))

small_kv = []
for k, v in item_kv_dict.items():
    for kv in v:
        small_kv.append(kv)
small_kv = list(unique_everseen(small_kv))

smallkv_dict = name2dict(small_kv, len(user_dict)+len(item_dict))
rev_smallkv_dict = {v:k for k,v in smallkv_dict.items()}



user_item_rating_dict, user_item_date_dict = match_rating_date(user_item_dict, item_user_dict, args.review_path)
#train_dict, test_dict = get_train_test(user_item_date_dict, test_length)

brand_dict, category_dict = get_brand_category(meta)
brand_dict = name2dict(brand_dict.keys(), len(user_dict)+len(item_dict)+len(smallkv_dict))
category_dict = name2dict(category_dict.keys(), len(user_dict)+len(item_dict)+len(smallkv_dict)+len(brand_dict))
rev_brand_dict = {v:k for k,v in brand_dict.items()}
rev_category_dict = {v:k for k,v in category_dict.items()}
print(list(user_dict.items())[0:2])
print(list(item_dict.items())[0:2])
print(list(category_dict.items())[0:2])
print(list(brand_dict.items())[0:2])
print(list(smallkv_dict.items())[0:2])

user_list, item_list = list(user_dict.keys()), list(item_dict.keys())
item_brand_dict, item_category_dict, also_bought_dict, bought_together_dict, also_viewed_dict = get_item_related2(user_list, item_list, meta, item_dict)


print(list(user_item_dict.items())[0:2])
print(list(item_category_dict.items())[0:2])
print(list(item_brand_dict.items())[0:2])
print(list(also_bought_dict.items())[0:2])
print(list(also_viewed_dict.items())[0:2])
print(list(item_kv_dict.items())[0:2])
# # write user, product, related product, brand, category, k-v, 
# # item-category, item-brand, item-also bought, item-also view, bought-together, item-kv

print(len(user_item_dict))
print(len(item_category_dict))
print(len(item_brand_dict))
print(len(also_bought_dict))
print(len(item_kv_dict))
# write output files
write_out_file(args.output_dir, 'users.pickle', rev_user_dict)
write_out_file(args.output_dir, 'product.pickle', rev_item_dict)
write_out_file(args.output_dir, 'related_product.pickle', rev_item_dict)
write_out_file(args.output_dir, 'brand.pickle', rev_brand_dict)
write_out_file(args.output_dir, 'category.pickle', rev_category_dict)
write_out_file(args.output_dir, 'kv.pickle', rev_smallkv_dict)


write_out_related(args.output_dir, 'user_item.pickle', rev_user_dict, user_item_dict, item_dict)
print('write user_item finished')
write_out_related(args.output_dir, 'item_category.pickle', rev_item_dict, item_category_dict, category_dict)
print('write item_category finished')
write_out_related(args.output_dir, 'item_brand.pickle', rev_item_dict, item_brand_dict, brand_dict)
print('write item_brand finished')
write_out_related(args.output_dir, 'also_bought.pickle', rev_item_dict, also_bought_dict, item_dict)
print('write also_bought finished')
write_out_related_kv(args.output_dir, 'item_kv.pickle', rev_item_dict, item_kv_dict, kv_dict)
print('write item_kv finished')
write_out_related(args.output_dir, 'also_viewed.pickle', rev_item_dict, also_viewed_dict, item_dict)
print('write also_viewed_p_p finished')
# write_out_related(args.output_dir, 'bought_together.pickle', rev_item_dict, bought_together_dict, item_dict)
# print('write bought_together_p_p finished')

#sys.exit()

print(len(user_item_dict))
print(len(item_user_dict))
#no need for filter
user_item_filter, item_user_filter = get_filter(user_item_dict, item_user_dict, test_length)
print(len(user_item_filter))
print(len(item_user_filter))
#sys.exit()
print(list(user_item_filter.items())[0:2])
train_set, test_set = get_train_test2(user_item_dict, item_dict)
print(list(train_set.items())[0:2])
print(len(train_set))
print(len(test_set))
print(list(test_set.items())[0:2])

# convert to num index representation
write_out_train_test(args.output_dir, 'train.pickle', user_dict, train_set, item_dict)
write_out_train_test(args.output_dir, 'test.pickle', user_dict, test_set, item_dict)





# example of first object in All_Beauty review:
#{'overall': 1.0, 
# 'verified': True, 
# 'reviewTime': '02 19, 2015', 
# 'reviewerID': 'A1V6B6TNIC10QE', 
# 'asin': '0143026860', 
# 'reviewerName': 'theodore j bigham', 
# 'reviewText': 'great', 
# 'summary': 'One Star', 
# 'unixReviewTime': 1424304000}

# example of first object in meta_All_Beauty meta:
#{'category': [], 
# 'tech1': '', 
# 'description': ["Loud 'N Clear Personal Sound Amplifier allows you to turn up the volume on what people around you are saying, listen at the level you want without disturbing others, hear a pin drop from across the room."], 
# 'fit': '', 
# 'title': "Loud 'N Clear&trade; Personal Sound Amplifier", 
# 'also_buy': [], 
# 'tech2': '', 
# 'brand': 'idea village', 
# 'feature': [], 
# 'rank': '2,938,573 in Beauty & Personal Care (', 
# 'also_view': [], 
# 'details': {'ASIN: ': '6546546450'}, 
# 'main_cat': 'All Beauty', 
# 'similar_item': '', 
# 'date': '', 
# 'price': '', 
# 'asin': '6546546450', 
# 'imageURL': [], 
# 'imageURLHighRes': []}

# example of first object in MAVE positive:
# The product id is exactly the ASIN number in review data
#{'category': 'Games', 
# 'attributes': [{'evidences': [{'pid': 1, 'end': 285, 'value': 'For 2 players', 'begin': 272}, 
#                               {'pid': 2, 'end': 228, 'value': 'For 2 players', 'begin': 215}, 
#                               {'pid': 3, 'end': 228, 'value': 'For 2 players', 'begin': 215}], 
#                 'key': 'Maximum Players'}, 
#                {'evidences': [{'pid': 1, 'end': 300, 'value': 'Ages 6- Adult', 'begin': 287}], 
#                 'key': 'Recommended Age'}, 
#                {'evidences': [{'pid': 1, 'end': 300, 'value': 'Adult', 'begin': 295}], 
#                 'key': 'Age Group'}], 
# 'id': 'B005DVV6RW', 
# 'paragraphs': [{'source': 'title', 'text': 'PRESSMAN TOY Mancala'}, 
#                {'source': 'description', 'text': 'PLEASE NOTE: THIS ITEM CANNOT SHIP VIA 3-DAY DELIVERY. THE CENTURIES OLD GAME OF COLLECTING "GEMSTONES". The one with the most stones wins! Comes complete with solid wood hinged playing board, 48 multi-colored stones, and illustrated instructions. Folds for easy storage. For 2 players. Ages 6- Adult.'}, 
#                {'source': 'feature', 'text': 'THE CENTURIES OLD GAME OF COLLECTING "GEMSTONES"The one with the most stones wins! Comes complete with solid wood hinged playing board, 48 multi,colored stones, and illustrated instructions. Folds for easy storage. For 2 players. Ages 6 ,'}, 
#                {'source': 'feature', 'text': 'THE CENTURIES OLD GAME OF COLLECTING "GEMSTONES"The one with the most stones wins! Comes complete with solid wood hinged playing board, 48 multi,colored stones, and illustrated instructions. Folds for easy storage. For 2 players. Ages 6 ,'}, 
#                {'source': 'price', 'text': '$18.08'}, 
#                {'source': 'brand', 'text': 'Pressman'}]}





# data = []
# with open('/raid/brutusxu/MAVE/reproduce/mave_positives.jsonl') as f:
# #with gzip.open(args.meta_path, 'r') as f:
# #with gzip.open(args.review_path, 'r') as f:
#    count = 0
#    for l in f:
#         data.append(json.loads(l.strip()))
#         count += 1

#         if count == 1:
#            break

# #print(len(data))
# print(data[0]['attributes'][0])
