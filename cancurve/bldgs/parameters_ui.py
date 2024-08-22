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
    'subClassification': ['Single Family', 'Construction', 'Duplex', 'Entertainment and Recreation', 'Food/Drugs/Chemicals', 'Heavy', 'High rise apartment', 'High technology', 'Hospital', 'Light', 'Low rise apartment', 'Medical office', 'Metals/Minerals Processing', 'Mobile home', 'Multifamily', 'Other', 'Personal and repair', 'Recreational', 'Retail trade', 'Theatre', 'Townhouse', 'Wholesale trade'],
    'storeys': ['1', '2', 'Split', 'Multi-story'],
    
    'heatingType': ['Baseboard-electric', 'Baseboard-hot Water', 'Forced Air - Electric', 'Forced Air - Gas', 'Forced Air - Unknown', 'Heatpump', 'Mixed', 'Solar', 'Oil', 'Woodstove', 'Other'],
    'coolingType': ['Central air', 'Heat pump'],
    'garageType': ['Yes, Attached', 'Yes, Detached', 'None'],
    'garageSize': ['Single', 'Single Plus', 'Double', 'Triple'],
    'buildingLayout':['default'], #needed by DRF, but not sure about values other than 'default'
    
    
    #foundation/basement
    'foundationType':['Basement', 'Crawlspace', 'Slab', 'Other'],
    'basementHeightUnits':['m', 'ft'],
    
    
    
    #size age materials
    'sizeOrAreaUnits':['m2', 'ft\u00B2'],
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
    'currency':['$CAD', '$USD', 'Other'],
    'costBasis':['Replacement Cost', 'Depreciated Costs']
}


 