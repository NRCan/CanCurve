'''
Created on Apr. 16, 2024

@author: cef
'''

colns_index = ['cat', 'sel', 'bldg_layout']

colns_dtypes = {'cat': 'object', 'sel': 'object', 'rcv': 'float64', 'desc': 'object', 'bldg_layout':'object',
                'group_code':'object', 'group_description':'object'}

floor_story_d = {'main':0, 'basement':-1}