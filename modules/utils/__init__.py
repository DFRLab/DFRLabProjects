# -*- coding: utf-8 -*-

'''
'''

# import modules
import time
import os


# create functions
def create_folder(prompt=None):
    '''
    '''
    if prompt != None:
        prompt = prompt.capitalize()
    t = str(int(time.time()))
    folder = f'../_data/DATA{t}{prompt}'
    if not os.path.exists(folder):
        os.mkdir(folder)
    
    return folder


def clean_text(text):
    '''
    '''
    text = text.replace('\x00', '')
    return ' '.join(text.split()).strip()


def twitter_data_converters():
    return {
        'id_str': str,
        'user_id_str': str,
        'created_at_year': str,
        'created_at_hour': str,
        'rt_user_id_str': str,
        'rt_status_id_str': str,
        'quoted_status_id_str': str,
        'in_reply_to_status_id_str': str,
        'in_reply_to_user_id_str': str
    }

