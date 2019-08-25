# -*- coding: utf-8 -*-

'''
'''

# import modules
import pandas as pd
from bs4 import BeautifulSoup as bs

# import local modules
from utils import time_string_folder, clean_text

# create functions
def arguments(screen_name, exclude_replies, \
    include_rts):
    '''
    '''
    object = {
		'screen_name': screen_name,
		'count': 200,
		'exclude_replies': exclude_replies,
		'include_rts': include_rts,
		'tweet_mode': 'extended'
    }

    return object


def twitter_timeline_columns():
    '''
    '''
    return [
        'id_str',
        'tweet_url',
        'user',
        'user_id_str',
		'user_url',
        'created_at',
        'text',
		'full_text',
		'is_retweet_status',
		'rt_user_screen_name',
		'rt_user_id_str',
		'rt_status_id_str',
		'is_quote_status',
		'source'
    ]


def extract_full_text(data):
	'''
	'''
	rstatus = 'retweeted_status'
	txt = 'full_text'
	return [
		(obj[rstatus][txt] if rstatus in obj.keys() else obj[txt])
		for obj in data
	]


def is_retweet_status(data):
	'''
	'''
	rstatus = 'retweeted_status'
	return [
		(1 if rstatus in obj.keys() else 0)
		for obj in data
	]


def is_quote_status(data):
	'''
	'''
	qstatus = 'is_quote_status'
	return [
		int(obj[qstatus]) for obj in data
	]


def get_anchor_text(html):
	'''
	'''
	try:
		src = bs(html, 'lxml')
	except:
		src = bs(html, 'html5lib')
	
	return src.text


def retweet_attributes(data):
	'''
	'''
	rstatus = 'retweeted_status'
	return {
		'rt_user_screen_name': [
			(obj[rstatus]['user']['screen_name']
			if rstatus in obj.keys() else None)
			for obj in data
		],
		'rt_user_id_str': [
			(obj[rstatus]['user']['id_str']
			if rstatus in obj.keys() else None)
			for obj in data
		],
		'rt_status_id_str': [
			(obj[rstatus]['id_str']
			if rstatus in obj.keys() else None)
			for obj in data
		]
	}


def timeline_one_round(cxn, **kwargs):
	'''
	'''
	args = arguments(**kwargs)
	if type(args['screen_name']) == list:
		Error = 'screen_name should be a string, not list \
			-> consider to use `batch_timeline_one_round` instead'
		Error = ' '.join(Error.split()).strip()
		raise ValueError(Error)
		
	statuses = cxn.statuses.user_timeline(**args)
	return statuses


def batch_timeline_one_round(cxn, **kwargs):
	'''
	'''
	args = arguments(**kwargs)
	if type(args['screen_name']) == str:
		Error = 'screen_name should be a list, not string \
			-> consider to use `timeline_one_round` instead'
		Error = ' '.join(Error.split()).strip()
		raise ValueError(Error)
	
	# create time string folder
	folder = time_string_folder()
	
	# create csv files -> twitter data
	path = f'{folder}/data.csv'
	pd.DataFrame(columns=twitter_timeline_columns()) \
		.to_csv(path, index=False, encoding='utf-8')

	# iterate
	for user in args['screen_name']:
		tmp = {}
		for k, v in args.items():
			if k != 'screen_name':
				tmp[k] = v
		
		tmp['screen_name'] = user

		# extract statuses
		statuses = cxn.statuses.user_timeline(**tmp)





		# temp
		_id = [i['id_str'] for i in statuses]
		tweet_url = [
			f'https://twitter.com/i/web/status/{i}'
			for i in _id
		]
		user = [i['user']['screen_name'] for i in statuses]
		user_id_str = [i['user']['id_str'] for i in statuses]
		user_url = [
			f'https://twitter.com/{i}' for i in user
		]
		created_at = [i['created_at'] for i in statuses]
		text = [i['full_text'] for i in statuses]
		full_text = extract_full_text(statuses)
		isrt = is_retweet_status(statuses)
		isq = is_quote_status(statuses)
		source = [get_anchor_text(i['source']) for i in statuses]

		# retweet attributes
		rt_attrs = retweet_attributes(statuses)

		df = pd.DataFrame({
			'id_str': _id,
			'tweet_url': tweet_url,
			'user': user,
			'user_id_str': user_id_str,
			'user_url': user_url,
			'created_at': created_at,
			'text': text,
			'full_text': full_text,
			'is_retweet_status': isrt,
			'rt_user_screen_name': rt_attrs['rt_user_screen_name'],
			'rt_user_id_str': rt_attrs['rt_user_id_str'],
			'rt_status_id_str': rt_attrs['rt_status_id_str'],
			'is_quote_status': isq,
			'source': source
		})

		# clean text
		df['text'] = df['text'].apply(clean_text)
		df['full_text'] = df['full_text'].apply(clean_text)






		# append data to csv file
		df.to_csv(path, index=False, encoding='utf-8', mode='a', \
			header=False)

	return folder
