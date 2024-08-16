# Legacy software
Compatability and comparison to Program for the Development of Flood Damage (Vulnerability) Curves for buildings in Canada (DDFP).

#DDFP
see [DDFP](https://github.com/cefect/DDFP) repository and readme for description.

# Philosophical differences

- DDFP is an Xactimate + Excel based workflow
- CanCurve is python-based QGIS plugin

## Fixed costs and Response costs
Fixed costs are those restoration activities that are not a function of depth. e.g., mobilzation.

DDFP Uses a set of $/m2 values developed from spatiotemporal price lists (e.g., ABCA8X_SEP23; see the master rule book 'Response_Costs') for different categories (e.g., General, Kitchen/Bathroom) that are assigned to rooms then multiplied by the floor area of the room (see 'Groups-Layout').

CanCurve has a simpler approach whereby the user supplies fixed values for each storey.

## Structure-level split costs
depth-dependent costs that are not obviously assigned to a room (i.e., StructureLevelLineItems). This is a shortcoming of the Xactimate data used by DDFP. 

DDFP assigns these to 'split', which is typically then evenly divided between the basement and the main floor. 

CanCurve assigns all of these to the basement during the data extraction.
