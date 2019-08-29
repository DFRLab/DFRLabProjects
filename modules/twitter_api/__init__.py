# -*- coding: utf-8 -*-

'''
'''

# import modules
import sys
import pandas as pd
from bs4 import BeautifulSoup as bs

# import local modules
from utils import create_folder, clean_text

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
        'created_at_timestamp',
        'created_at_year',
        'created_at_month',
        'created_at_day',
		'created_at_hour',
		'created_at_weekday',
		'created_at_time_hour',
        'text',
		'full_text',
		'is_retweet_status',
		'rt_user_screen_name',
		'rt_user_id_str',
		'rt_status_id_str',
		'is_quote_status',
		'quoted_status_id_str',
		'quoted_status_url',
		'quoted_user_screen_name',
		'quoted_was_deleted',
		'in_reply_to_status_id_str',
		'in_reply_to_screen_name',
		'in_reply_to_user_id_str',
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


def quote_attributes(data):
	'''
	'''
	qstatus = 'is_quote_status'
	istr = 'quoted_status_id_str'
	link = 'quoted_status_permalink'

	return {
		'quoted_status_id_str': [
			(
				obj[istr]
				if obj[qstatus] == True and istr in obj.keys()
				else None
			)
			for obj in data
		],
		'quoted_status_url': [
			(
				obj[link]['expanded']
				if obj[qstatus] == True and link in obj.keys()
				else None
			)
			for obj in data
		],
		'quoted_user_screen_name': [
			(
				obj[link]['expanded'].split('/')[3]
				if obj[qstatus] == True and link in obj.keys()
				else None
			)
			for obj in data
		],
		'quoted_was_deleted': [
			(
				1 if obj[qstatus] == True and not istr in obj.keys()
				else 0
			)
			for obj in data
		]
	}


def reply_attributes(data):
	'''
	'''
	return {
		'in_reply_to_status_id_str': [
			obj['in_reply_to_status_id_str'] for obj in data
		],
		'in_reply_to_screen_name': [
			(
				obj['in_reply_to_screen_name']
				if obj['in_reply_to_status_id_str'] != None
				else None
			)
			for obj in data
		],
		'in_reply_to_user_id_str': [
			(
				obj['in_reply_to_user_id_str']
				if obj['in_reply_to_status_id_str'] != None
				else None
			)
			for obj in data
		]
	}


def timestamp_attrs(data, col='created_at', tz='America/Mexico_City',
	passtz=True):
	'''
	'''
	if passtz:
		t = pd.to_datetime(
			data[col],
			utc=True,
			infer_datetime_format=True
		).apply(lambda x: x.tz_convert(tz))
	else:
		t = pd.to_datetime(
			data[col],
			infer_datetime_format=True
		)
	
	data[f'{col}_timestamp'] = t
	data[f'{col}'] = t.dt.strftime('%Y-%m-%d')
	data[f'{col}_year'] = t.dt.year
	data[f'{col}_month'] = t.dt.month
	data[f'{col}_day'] = t.dt.day
	data[f'{col}_hour'] = t.dt.hour
	data[f'{col}_weekday'] = t.dt.dayofweek
	data[f'{col}_time_hour'] = t.dt.strftime('%H:%M:%S')
	
	return data


def build_dataframe(statuses, tz):
	'''
	'''
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

	# quote attributes
	qt_attrs = quote_attributes(statuses)

	# reply attrs
	rp_attrs = reply_attributes(statuses)

	# create dataframe
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
		'quoted_status_id_str': qt_attrs['quoted_status_id_str'],
		'quoted_status_url': qt_attrs['quoted_status_url'],
		'quoted_user_screen_name': qt_attrs['quoted_user_screen_name'],
		'quoted_was_deleted': qt_attrs['quoted_was_deleted'],
		'in_reply_to_status_id_str': rp_attrs['in_reply_to_status_id_str'],
		'in_reply_to_screen_name': rp_attrs['in_reply_to_screen_name'],
		'in_reply_to_user_id_str': rp_attrs['in_reply_to_user_id_str'],
		'source': source
	})

	# clean text
	df['text'] = df['text'].apply(clean_text)
	df['full_text'] = df['full_text'].apply(clean_text)

	# timestamp attributes
	args = {
		'data': df
	}
	if tz != 'default':
		args['tz'] = tz
	
	df = timestamp_attrs(**args)

	# order columns
	order = twitter_timeline_columns()
	df = df[order].copy()

	return df


def user_timeline(cxn, **kwargs):
	'''
	'''
	# create time string folder
	screen_name = kwargs['screen_name']
	folder = create_folder(prompt=screen_name)

	# create csv files -> twitter data
	path = f'{folder}/data.csv'
	pd.DataFrame(columns=twitter_timeline_columns()) \
		.to_csv(path, index=False, encoding='utf-8')
	
	# arguments
	tz = 'default'
	if 'tz' in kwargs.keys():
		tz = kwargs['tz']
		del kwargs['tz']
	
	args = arguments(**kwargs)
	statuses = cxn.statuses.user_timeline(**args)


	# build dataframe
	df = build_dataframe(statuses, tz)

	# append data to csv file
	df.to_csv(path, index=False, encoding='utf-8', mode='a', \
		header=False)


	# get oldest
	oldest = min([i['id'] for i in statuses]) - 1

	# looper
	while len(statuses) > 0:
		statuses = cxn.statuses.user_timeline(max_id=oldest, **args)
		if statuses:
			df = build_dataframe(statuses, tz)

			# append data to csv file
			df.to_csv(path, index=False, encoding='utf-8', mode='a', \
				header=False)
			
			oldest = min([i['id'] for i in statuses]) - 1

	print (f'Data is available in {path}')
	return path


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
	if type(kwargs['screen_name']) == str:
		Error = 'screen_name should be a list, not string \
			-> consider to use `timeline_one_round` instead'
		Error = ' '.join(Error.split()).strip()
		raise ValueError(Error)
	
	# create time string folder
	folder = create_folder()
	
	# create csv files -> twitter data
	path = f'{folder}/data.csv'
	pd.DataFrame(columns=twitter_timeline_columns()) \
		.to_csv(path, index=False, encoding='utf-8')

	# arguments
	tz = 'default'
	if 'tz' in kwargs.keys():
		tz = kwargs['tz']
		del kwargs['tz']
	
	args = arguments(**kwargs)

	# iterate
	for user in args['screen_name']:
		tmp = {}
		for k, v in args.items():
			if k != 'screen_name':
				tmp[k] = v
		
		tmp['screen_name'] = user

		# extract statuses
		statuses = cxn.statuses.user_timeline(**tmp)

		# build dataframe
		df = build_dataframe(statuses, tz)

		# append data to csv file
		df.to_csv(path, index=False, encoding='utf-8', mode='a', \
			header=False)


	print (f'Data is available in {path}')
	return path
