# -*- coding: utf-8 -*-

'''
'''

# import modules
import time
import os


# create functions
def time_string_folder():
    '''
    '''
    t = str(int(time.time()))
    folder = f'../_data/DATA{t}'
    if not os.path.exists(folder):
        os.mkdir(folder)
    
    return folder


def clean_text(text):
    '''
    '''
    text = text.replace('\x00', '')
    return ' '.join(text.split()).strip()
