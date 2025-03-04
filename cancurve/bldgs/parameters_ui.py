'''
Created on Apr. 28, 2024

@author: cef
'''

import os

#os.path.dirname(os.path.dirname(__file__))

#options for populating the building details tab
building_details_options_d = {
    #general
    #'occupancyClassification': ['Residential', 'Commercial', 'Industrial', 'Other'],
    #'subClassification': ['Single Family', 'Construction', 'Duplex', 'Entertainment and Recreation', 'Food/Drugs/Chemicals', 'Heavy', 'High rise apartment', 'High technology', 'Hospital', 'Light', 'Low rise apartment', 'Medical office', 'Metals/Minerals Processing', 'Mobile home', 'Multifamily', 'Other', 'Personal and repair', 'Recreational', 'Retail trade', 'Theatre', 'Townhouse', 'Wholesale trade'],
    'storys': ['1', '2', 'Split', 'Multi-storey'],
    
    'heatingType': ['Baseboard-electric', 'Baseboard-hot Water', 'Forced Air - Electric', 'Forced Air - Gas', 'Forced Air - Unknown', 'Heatpump', 'Mixed', 'Solar', 'Oil', 'Woodstove', 'Other'],
    'coolingType': ['Central air', 'Heat pump'],
    'garageType': ['None', 'Attached', 'Detached', 'Underground single-level', 'Underground multi-level', 'Surface Parking', 'Other'],
    'garageSize': ['Single', 'Single Plus', 'Double', 'Triple', '>10'],
    'buildingLayout':['default'], #needed by DRF, but not sure about values other than 'default'
    
    
    #foundation/basement
    'foundationType':['Basement', 'Crawlspace', 'Slab', 'Other'],
    #'basementHeightUnits':['m', 'ft'],
    
    
    
    #size age materials
    'sizeOrAreaUnits':['m2', 
                       #'ft\u00B2'
                       'ft2'],
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
    'taxesIncluded': ['PST', 'PST & GST', 'GST', 'HST', 'HST & QST', 'None'],
    'currency':['$CAD', '$USD', 'Other'],
    'costBasis':['Replacement Cost', 'Depreciated Cost']
}


#hierarchical building occupancy classes
building_occupancy_class_d = {
    "Residential": [
        "Single Family",
        "Townhouse",
        "Mobile home",
        "Duplex",
        "Multiplex",
        "Low rise apartment",
        "High rise apartment",
        "Seniors Housing",
        "Other",
    ],
    "Commercial": [
        "Retail trade",
        "Wholesale Trade",
        "Personal and Repair",
        "Hospital",
        "Care Homes",
        "Medical office",
        "Entertainment and recreation",
        "Theatre",
        "Professional and Technical Services",
        "Financial Services",
        "Automobile Services",
        "Other"
    ],
    "Industrial": [
        "Heavy",
        "Light",
        "Food/Drugs/Chemicals",
        "Metals/Minerals Processing",
        "High technology",
        "Construction",
        'Wastewater Plants'
        "Other",
    ],
    "Agriculture": [
        "Agriculture facilities",
        "Other",

    ],
    "Government": [
        "Government Services",
        "Emergency Services",
        "School",
        "College or University",
        "Other",

    ],
    "Cultural": [
        "Religious",
        "Community Centres",
        "Arena",
        "Swimming Pool",
        "Museum",
        "Club Centres",
        "Aquarium",
        "Other",

    ],
    "Critical Infrastructure": [
        "Electrical substations",
        "Wastewater Plants",
        "water treatment plants",
        "pumpstations",
        "lighthouses",
        "Other",
    ],
    "Other":["Other"]
}


#update building_details_options_d with the occupancy classes

# Set occupancyClassification to the keys of building_occupancy_class_d
building_details_options_d['occupancyClassification'] = list(building_occupancy_class_d.keys())

# Flatten the lists from building_occupancy_class_d values and remove duplicates using a set
building_details_options_d['subClassification'] = list({option for options in building_occupancy_class_d.values() for option in options})

