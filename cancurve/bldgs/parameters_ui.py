'''
Created on Apr. 28, 2024

@author: cef
'''

import os

#os.path.dirname(os.path.dirname(__file__))

#options for populating the building details tab
building_details_options_d = {
    #general
    'occupancyClassification': ['Residential', 'Commercial', 'Industrial', 'Other'],
    'subClassification': ['Single Family', 'Construction', 'Duplex', 'entertainment and recreation'],
    'storeys': [1, 2, 3, 'Split'],
    
    'heatingType': ['baseboard-electric', 'baseboard-hot water', 'Forced air - electric', 'forced air-gas'],
    'coolingType': ['Central air', 'Heat pump'],
    'garageType': ['Yes, Attached', 'Yes, Detached', 'None'],
    'garageSize': ['Single', 'Single Plus', 'Double', 'Triple'],
    'buildingLayout':['default'], #needed by DRF, but not sure about values other than 'default'
    
    
    #foundation/basement
    'foundationType':['basement', 'crawlspace', 'slab', 'other'],
    'basementHeightUnits':['m', 'ft'],
    
    
    
    #size age materials
    'sizeOrAreaUnits':['m\u00B2', 'ft\u00B2'],
    'qualityOfBuildingMaterials': ['Below Average', 'Average', 'Above Average', 'Custom'],
    
    
    #location costs
    'provinceTerritory':[
                            "AB",  # Alberta
                            "BC",  # British Columbia
                            "MB",  # Manitoba
                            "NB",  # New Brunswick
                            "NL",  # Newfoundland and Labrador
                            "NS",  # Nova Scotia
                            "ON",  # Ontario
                            "PE",  # Prince Edward Island
                            "QC",  # Quebec
                            "SK",  # Saskatchewan
                            "NT",  # Northwest Territories
                            "NU",  # Nunavut
                            "YT"   # Yukon
                        ],
    'taxesIncluded': ['PST', 'PST & GST', 'GST', 'None'],
    'currency':['$CAD', '$USD'],
    'costBasis':['replacement cost', 'depreciated costs']
}


building_details_translation_d = {
    'basement_height_m':'basementHeight_DoubleSpinBox',
    'scale_value':'sizeOrAreaValue_DoubleSpinBox',
    'bldg_layout':'buildingLayout_ComboBox',
    }