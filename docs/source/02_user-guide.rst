.. _sec02-userGuide:

User Guide: Buildings Tool
==========================

.. _sec02-bldgs:



The CanCurve **Buildings Tool** is designed to create Depth Damage Functions (DDF) for an archetypal Canadian building from detailed restoration cost data.
Basically, the tool joins this cost data to a database of item vulnerability then groups the data by depth to create a simple function for *flood damage* against *flood depth* (with some additional features of course). 

Introduction
-------------
The devastation of the 2013 Southern Alberta and Toronto Floods triggered a transition in Canada from the traditional standards-based approach, where flood protection is designed for a single level-of-safety, towards a risk-based approach.
This new risk-based approach recognizes that robust planning must consider vulnerability and a range of floods that may harm a community, rather than focusing on a single design event.
The foundation of this new approach are *flood risk models*: a collection of procedures, algorithms, and mathematical functions used to simplify, study, and quantify the components of our world that relate to flood risk.
At the core of most flood risk models are a set of flood damage functions.

Depth Damage Functions (DDF)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Flood damage functions are a mathematical relationship between hazard and vulnerability variables against the estimated damages from flooding (e.g., building repair costs) for an individual asset.
The most basic functions directly relate flood depth to damage --- the so-called depth-damage curves or functions (DDF) widely attributed to Gilbert White [#1]_.
Damage functions are typically categorized based on the model's focus or objective, such as the sector (residential vs. non-residential), tangibility (tangible vs. intangible), damage mechanism (indirect vs. direct), and uncertainty treatment (deterministic vs. probabilistic) [#2]_.
Further classification considers the function structure such as continuity (discrete vs. continuous) and for tangible economic functions the asset total value relation (relative vs. absolute).
While depth-damage functions are still common, research in the past two decades has advanced the understanding of flood damage processes and, along with new data and techniques, has led to more sophisticated and accurate multi-variate models [#3]_.
CanCurve currently only supports discrete tangible depth-damage functions.


Flood Risk Modelling in Canada
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
NRCan develops and maintains flood risk software and data tools to support disaster resilience in Canada. 
In particular, NRCan maintains `CanFlood <https://github.com/NRCan/CanFlood>`_, a QGIS plugin for building flood risk models. 
A major input or component of CanFlood models are DDFs. 
Traditionally, CanFlood users struggled to obtain DDFs from past projects or public repositories, leading to inefficient and inaccurate risk modelling. 
To address this gap, in 2023 NRCan commissioned the Arcadis company to develop a system for constructing local DDFs in Canada. 
This resulted in a formal process for constructing DDFs called *Program for the Development of Flood Damage (Vulnerability) Curves for buildings in Canada* (a.k.a. the DDF Program or DDFP).
To operationalize DDFP, NRCan initiated the CanCurve project.

.. _sec02-dataRequirements:

Data Requirements
-----------------
The **Buildings Tool** requires three types of data about the archetypal building in order to generate a DDF.

Building Metadata
~~~~~~~~~~~~~~~~~
Building metadata includes any information that might be relevant to estimating the flood vulnerability of an archetype, like the year of construction, the date associated with the cost estimate, the person preparing the estimate, etc.
This information is used by the Buildings Tool to populate metadata fields on output DDFs and, in some cases, to assemble the DDF.
Metadata is specified on the **Metadata** tab and stored in the **c00_bldg_meta** table of the Project Database.
The user is expected to obtain this information from expert knowledge and documentation on the archetype. 

.. _sec02-costInformation:

Cost Information
~~~~~~~~~~~~~~~~

This restoration item and cost data is specifed as a CSV file on the Data Input tab. Click here for an example. [Click here for an example].

.. _sec02-DRF:

Depth-Replacement-Factor (DRF) Dataset
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This dataset relates flood depth to the percentage loss or damage of a restoration item and is specified on the Data Input tab. By default, the DRF dataset shipped with CanCurve will be used.

.. _sec02-fixedCosts:

Fixed Costs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This simple dataset has two simple values, the fixed costs for the restoration of the basement and the mainfloor.
This represents the sum of all depth-invariant cost items for each floor.
For example, mobilization costs or permit fees --- restoration costs that would be incurred no mater how severe the flood exposure.



Key Concepts
-----------------
The **Buildings Tool** is composed of the Graphical User Interface (GUI) front-end and a collection of python scripts for performing the data operations in the back-end, called the *core* which contains four *curve creation* steps.
A typical workflow starts by preparing the :ref:`Input Data <sec02-dataRequirements>`, populating the fields in the GUI, then executing the :ref:`Curve Creation Steps <_sec02-Core>`. 

.. _sec02-Core:

Core: Curve Creation Steps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
At the core of the Buildings Tool are four curve creation steps that are executed in sequence to generate a DDF.
These are controlled from the **Create Curve** tab and can be executed individually or all at once:

1. **Setup project**: 
   Construct the :ref:`project SQLite database <sec02-projectDatabase>` and load data into it from the GUI.

2. **Data join and multiply costs**: 
   Join DRF to the Cost-Item table, then multiply through to create fractional restoration costs.

3. **Data group and concat stories**: 
   Group restoration costs by story and concatenate them into a single table.

4. **Export result in CanFlood format**: 
   Export the DDF in the CanFlood format.

To pass information between these steps and to save the user's progress to a file, all of these steps read or write to a SQLite database, called the :ref:`Project Database <sec02-projectDatabase>`.


Project Database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The **Project Database** is a SQLite database that stores the data and metadata for the project.
While knowledge of the project database is not strictly necessary to use CanCurve, it can be useful for debugging and understanding the tool's operation.
The database is composed of several tables, each of which is used by one or more of the curve creation steps, as shown in the table below.

.. _tab02-ProjectDatabase:

 
.. table:: Project Database tables and corresponding Curve Creation Steps
   :widths: auto

   +------------------+--------------------------------------------+------+
   | Table Name       | Description                                | Step |
   +==================+============================================+======+
   | c00_bldg_meta    | Building metadata                          | 1    |
   +------------------+--------------------------------------------+------+
   | c00_cost_items   | Cost-Item table                            | 1    |
   +------------------+--------------------------------------------+------+
   | c00_drf          | DRF database                               | 1    |
   +------------------+--------------------------------------------+------+
   | c00_fixed_costs  | Fixed costs                                | 1    |
   +------------------+--------------------------------------------+------+
   | c01_depth_rcv    | Fractional item cost for each depth        | 2    |
   +------------------+--------------------------------------------+------+
   | c02_ddf          | DDF for each story                         | 3    |
   +------------------+--------------------------------------------+------+
   | project_meta     | Metadata tracking operations on the db     | all  |
   +------------------+--------------------------------------------+------+
   | project_settings | Project settings                           | 1    |
   +------------------+--------------------------------------------+------+

To view and manipulate the project database, the user can use a SQLite database viewer like `DB Browser for SQLite <https://sqlitebrowser.org/>`_.


.. _sec02-CanFloodFormat:

CanFlood Format DDF
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The `CanFlood <https://github.com/NRCan/CanFlood>`_ program expects DDFs to be in a certain format, namely an XLSX file with two columns divided into two sections.
The first section contains the metadata in key-value pairs while the second section contains the exposure-impact series.
CanFlood requires three keys in the metadata section:
- **tag**: used for linking the curve to the inventory. 
- **impact_units**: used for indicating what units the impact values are in (e.g., $CAD) on plots and reports.
- **exposure**: used to indicate the transition between the metadata and the exposure-impact sections.
It is good practice to include additional metadata (e.g., location); however, these are not strictly required by CanFlood.
Below is a minimum example CanFlood format DDF.
 
 
.. _fig02-CanCurve-format:

.. figure:: /assets/02-CanCurve-format.png
   :alt: CanCurve format
   :align: center
   :width: 900px

   Conceptual diagram of the CanCurve Buildings Tool.




.. [#1] White, G. F.: Human Adjustment to Floods. A Geographical Approach to the Flood Problem in the United States, The University of Chicago, Chicago, 1945.

.. [#2] Merz, B., Kreibich, H., Schwarze, R., and Thieken, A.: Review article “Assessment of economic flood damage,” Nat. Hazards Earth Syst. Sci., 10, 1697–1724, https://doi.org/10.5194/nhess-10-1697-2010, 2010.

.. [#3] Schröter, K., Kreibich, H., Vogel, K., Riggelsen, C., Scherbaum, F., and Merz, B.: How useful are complex flood damage models?, Water Resources Research, 50, 3378–3395, https://doi.org/10.1002/2013WR014396, 2014.

.. [#4] Only those DRF entries intersecting with the c00_cost_items table are included.

