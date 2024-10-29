# backend data

## Master rule-book file
### mrb_20241007.db
updated on 2024-10-29 to include an additional 'depths' table for the drf column index.
port of Master Rule Book (cost item) data from l:\09_REPOS\04_TOOLS\DDFP\DDF_RuleBook_r0.xlsm
using l:\09_REPOS\04_TOOLS\CanCurve\misc\port_linerules.py
saved as a sqlite w/ 3 tables
- cost_item_meta: metadata for each cost item
- drf: depth-replacement-factor data for each cost item
- meta: metadata on how the dataset was created