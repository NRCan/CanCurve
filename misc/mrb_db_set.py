'''
Created on Oct. 7, 2024

@author: cef

take the raw MRB database and add keys and checks

doesn't look like this can be done after-the fact
pretty nasty to do w/o SQLalchemy... doesn't seem worth it
'''


sql_fp = r'l:\10_IO\CanCurve\misc\port_linerules\mrb_20241007.db'


#add primary keys to cost_items (cat, sel, bldg_layout)



#add primary keys to drf table  (cat, sel, bldg_layout)
#add foreign key from cost_items  (cat, sel, bldg_layout)
#add foreign key from depths ('depths_idx')

