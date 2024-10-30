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
CanCurve currently supports discrete, tangible, absolute, single-variable, depth-damage functions.


Flood Risk Modelling in Canada
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Natural Resources Canada (NRCan) develops and maintains flood risk software and data tools to support disaster resilience in Canada.
In particular, NRCan maintains `CanFlood <https://github.com/NRCan/CanFlood>`_, a QGIS plugin for building and running flood risk models.
A major input or component of CanFlood models are DDFs.
Traditionally, CanFlood users struggled to obtain DDFs from past projects or public repositories, leading to inefficient and inaccurate risk modelling.
To address this gap, in 2023 NRCan commissioned the Arcadis company to develop a system for constructing local DDFs in Canada.
This resulted in a formal process for constructing DDFs called *Program for the Development of Flood Damage (Vulnerability) Curves for buildings in Canada* (a.k.a. the DDF Program or DDFP).
To operationalize this, NRCan initiated the CanCurve project.

.. _sec02-dataRequirements:

Data Requirements
-----------------
The **Buildings Tool** requires three types of data about the archetypal building in order to generate a DDF, as summarized in the following sections.
See :ref:`Tutorials <sec03-tutorials>` for data examples.

Building Metadata
~~~~~~~~~~~~~~~~~
Building metadata is simple information relevant to estimating the flood vulnerability of an archetype, like the year of construction, the date associated with the cost estimate, the person preparing the estimate, etc.
This information is used by the Buildings Tool to populate metadata fields on output DDFs and, in some cases, to assemble the DDF.
Metadata is specified on the **Metadata** tab and stored in the **c00_bldg_meta** table of the :ref:`Project Database <sec02-projectdatabase>`
The user is expected to obtain this information from expert knowledge and documentation on the archetype.
To assemble the DDF, the following metadata is required:

 - **Building Layout** (``bldg_layout``): Corresponds to categories in the DRF dataset.
 - **Basement height value** (``basement_height_m``): The height of the basement in meters, used to concatenate the cost values between storys.
 - **Structure area value** (``scale_value``): The area of the structure in square meters used to scale the cost values for :ref:`Area-based <sec02-costbasis>` cost basis.

It is good practice to specify additional metadata fields, which the  Buildings Tool  propagates onto the output DDFs.

.. _sec02-costItem:

Cost-Item Table
~~~~~~~~~~~~~~~~

This restoration item and cost data is specified as a CSV file on the **Data Input** tab.
Typically this information is obtained from cost restoration experts using specialized software like Xactimate and a detailed model of the structure.


.. _sec02-DRF:

Depth Replacement-Factor (DRF) Database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This database relates flood depth to the percentage loss or damage of a restoration item and is specified on the **Data Input** tab.
The DRF database is a SQLite database with three tables:

 - **cost_item_meta**: lookup and description fields for each cost-item with key fields ``cat``, ``sel``, and ``bldg_layout``.
 - **drf**: the depth-replacement-factor for each cost-item with key fields ``cat``, ``sel``, and ``bldg_layout``.
 - **meta**: metadata for the database.

By default, the DRF database shipped with CanCurve will be used, which is installed into the `./db` directory of the CanCurve plugin.
This database was constructed by the DDFP project in consultation with cost-restoration specialists and reflects the vulnerability of a typical Canadian building to stillwater flooding.
:numref:`fig01-conceptual-diagram` provides a diagram of how the remote, local, and project datasets are related.

.. _fig01-conceptual-diagram:

.. figure:: /assets/01-conceptual-diagram.png
   :alt: Conceptual Diagram
   :align: center
   :width: 900px

   Conceptual diagram of the CanCurve Buildings Tool.

.. _sec02-fixedCosts:

Fixed Costs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This simple dataset has two values: the fixed costs for the restoration of the basement and the mainfloor.
This represents the sum of all depth-invariant cost items for each floor i.e., restoration costs that would be incurred regardless of flood depth.
For example, mobilization costs or permit fees.
This dataset is specified on the **Data Input** tab and stored in the **c00_fixed_costs** table of the Project Database.


Key Concepts
-----------------
The **Buildings Tool** is composed of the Graphical User Interface (GUI) front-end and a collection of python scripts for performing the data operations in the back-end, called the ``core`` which contains four :ref:`Curve Creation <sec02-Core>` steps.
A typical workflow starts by preparing the :ref:`Input Data <sec02-dataRequirements>`, populating the fields in the GUI, then executing the :ref:`Curve Creation Steps <sec02-Core>`.



.. _sec02-Core:

Core: Curve Creation Steps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
At the core of the Buildings Tool are four curve creation steps that are executed in sequence to generate a DDF.
These are controlled from the **Create Curve** tab and can be executed individually or all at once:

1. **Setup project**:
   Construct the :ref:`Project Database <sec02-projectDatabase>` and load data into it from the GUI.

2. **Data join and multiply costs**:
   Join :ref:`DRF Database <sec02-drf>` to the :ref:`Cost-Item table <sec02-costItem>`, then multiply through to create fractional restoration costs.

3. **Data group and concat stories**:
   Group restoration costs by story and concatenate them into a single table.

4. **Export result in CanFlood format**:
   Export the DDF in the :ref:`CanFlood format <sec02-CanFloodFormat>`.

To pass information between these steps and to save the user's progress to disk, all of these steps read or write to a :ref:`Project Database <sec02-projectDatabase>`.

.. _sec02-projectDatabase:

Project Database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The **Project Database** is a SQLite database that the Buildings Tool creates for each project, then uses to store the data and metadata for the project.
For most workflows, the Project Database is hidden in the background; however, knowledge of the project database can be useful for debugging and understanding the tool's operation.
The database is composed of several tables, each of which is used by one or more of the :ref:`curve creation steps <sec02-Core>`, as shown in the table below.

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
   | c00_drf          | DRF database [#4]_                         | 1    |
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
Currently, the buildings tool supports exporting DDFs in the CanFlood format.
The `CanFlood <https://github.com/NRCan/CanFlood>`_ program expects DDFs to be in a certain format, namely an XLSX file with two columns divided into two sections.
The first section contains the metadata in key-value pairs while the second section contains the exposure-impact series.
CanFlood requires three keys in the metadata section:

 - ``tag``: used for linking the curve to the inventory.
 - ``impact_units``: used for indicating what units the impact values are in (e.g., $CAD) on plots and reports.
 - ``exposure``: used to indicate the transition between the metadata and the exposure-impact sections.

It is good practice to include additional metadata (e.g., location); however, these are not strictly required by CanFlood.
Below is a minimum example CanFlood format DDF.

.. _fig02-CanCurve-format:

.. figure:: /assets/02-CanCurve-format.png
   :alt: CanCurve format
   :align: center
   :width: 900px

   CanFlood format DDF minimum example.

.. _sec02-costBasis:

Cost Basis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Buildings Tool supports two cost bases:

 - **Total** ($/structure): The resulting DDF will reflect the total restoration costs for the archetype as a function of depth. This can be useful for debugging and for risk models with very similar structures. For DDFs of this type, the calculated impacts should not be scaled.
 - **Area-based** ($/area): The resulting DDF will reflect the restoration costs per area of the structure as a function of depth. The units of the DDF impact values can be $/ft^2 or $/m^2 depending on what was specified in the **Structure area** field on the **Metadata** tab. This basis is useful for adapting the resulting archetypal DDF to other structures by scaling the impact values by the area of the structure. Most CanFlood models use this cost basis.


.. _sec02-units:

Units
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Buildings Tool is unit-agnostic, meaning any units you specify are supported.
Any units explicitly specified (e.g., through drop downs) or implicitly (e.g., through input data) are propagated into CanFlood's project tables and the final DDF outputs.
In otherwords, there are *no unit conversions* under-the-hood, by design.
Users should be aware of the three main units concerning DDFs:
 - **Currency**: This is related to the :ref:`Cost Basis <sec02-costBasis>`_, and is input implicitly from the :ref:`Cost Items <_sec02-costItem>`_ table. Users should ensure the **Currency** drop down on the **Metadata** tab is consistent with this table so that the resulting DDF metadata is accurate.
 - **Vertical Distances**: Both the *exposure depths* and the *basement heights* must be provided in the same units (no checks are performed on this). These units are specified on the *Data Input* tab under *exposure units* (feet or meters). These values are used to calculate the *exposure depths* on the resulting DDF.
 - **Structure Area**: To calculate *area-based curves*, the user must provide a *Structure area* value and unit on the *Metadata* tab (ft2 or m2). These units must be consistent with the intended application of the DDFs. For example, if you plan to use building area as a scaler in your flood risk model, the units of the area in the exposure data must match the units of your DDF. Often this is the same system as the **vertical distance** (e.g., metric), but this is not a requirement, i.e., a curve with a vertical distance of meters and an area of square feet is valid. 


 



.. [#1] White, G. F.: Human Adjustment to Floods. A Geographical Approach to the Flood Problem in the United States, The University of Chicago, Chicago, 1945.

.. [#2] Merz, B., Kreibich, H., Schwarze, R., and Thieken, A.: Review article “Assessment of economic flood damage,” Nat. Hazards Earth Syst. Sci., 10, 1697–1724, https://doi.org/10.5194/nhess-10-1697-2010, 2010.

.. [#3] Schröter, K., Kreibich, H., Vogel, K., Riggelsen, C., Scherbaum, F., and Merz, B.: How useful are complex flood damage models?, Water Resources Research, 50, 3378–3395, https://doi.org/10.1002/2013WR014396, 2014.

.. [#4] Only those DRF entries intersecting with the c00_cost_items table are included.

