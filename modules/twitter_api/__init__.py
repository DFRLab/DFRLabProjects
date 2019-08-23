# -*- coding: utf-8 -*-

'''
'''

# import local modules


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


def timeline_one_round(cxn, **kwargs):
	'''
	'''
	args = arguments(**kwargs)
	if type(args['screen_name']) == list:
		Error = 'screen_name should be string, not list \
			-> consider to use `batch_timeline_one_round` instead'
		Error = ' '.join(Error.split()).strip()
		raise ValueError(Error)
		
	statuses = cxn.statuses.user_timeline(**args)
	return statuses


def batch_timeline_one_round(cxn, **kwargs):
	'''
	'''
	pass
