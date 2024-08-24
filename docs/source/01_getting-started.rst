Getting Started
==================
The following sections will help you get started using CanCurve.
We suggest reading these sections first.


.. _sec01-install:

Installation
------------

To install CanCurve, you first need to install QGIS, then you can install CanCurve from the Plugin Repository.

For detailed instructions, refer to the `project README <https://github.com/NRCan/CanCurve/tree/main?tab=readme-ov-file#installation>`_.
For best performance, ensure you have the specified version of QGIS installed.


.. _sec01-overview:

Overview
-----------------------
CanCurve is a collection of tools for generating Depth Damage Functions (DDF) used by platforms like `CanFlood <https://github.com/NRCan/CanFlood>`_ to create flood risk models.
CanCurve's :ref:`Buildings Tool <sec02-bldgs>` for example facilitates the creation of DDFs from detailed restoration cost data for archetypal buildings.

This tool joins a table of restoration activities (e.g., repair dry-wall for $1000), called the :ref:`Cost-Item Table <sec02-costInformation>`, to a database of information on the flood vulnerability of those items, called the :ref:`Depth-Replacement-Factor (DRF) Database <sec02-DRF>`.
After identifying the target building or archetype for which a user would like to construct a DDF, typically a Cost-Item table is prepared using local pricing tables and expert knowledge on the restoration of the building.
For the DRF Database, either the version shipped with CanCurve can be used (default), or an alternate file can be specified.
Once these inputs and the building metadata are prepared and entered into the Buildings Tool, the four *Curve Creation* steps can be run to create and export a DDF in :ref:`CanFlood format <sec02-CanFloodFormat>`.


:numref:`fig01-conceptual-diagram` provides a diagram of how the remote, local, and project datasets are related.
See the  :ref:`Quick Start Guide <sec01-quick>` to learn more.

.. _fig01-conceptual-diagram:

.. figure:: /assets/01-conceptual-diagram.png
   :alt: Conceptual Diagram
   :align: center
   :width: 900px

   Conceptual diagram of the CanCurve Buildings Tool.


.. _sec01-quick:

Quick-Start
-----------------------
After installation of the plugin, the |CanCurve_icon| icon should appear on your plugins toolbar.
If you don't see the icon, first ensure the plugin is checked on the **Installed** tab of the **Manage and Install Plugins..** dialog; then ensure the **plugins toolbar** is enabled by right-clicking the QGIS toolbar.

.. |CanCurve_icon| image:: /assets/icon_solid.png
   :align: middle
   :width: 14

To start working with CanCurve, click the |CanCurve_icon| to open the :ref:`Buildings Tool <sec02-bldgs>` dialog.


.. _fig01-dialog-welcome:

.. figure:: /assets/01-dialog-welcome.png
   :alt: Welcome Tab
   :align: center
   :width: 900px

   Welcome tab of the Buildings Tool.

To use the tool to create a DDF from data for your archetypal building, first populate the **Metadata** tab with whatever information is available (see the :ref:`Tutorials <sec03-tutorials>` section for example data).
Note that not all fields are required, but the more information you provide, the more complete your DDF will be.
To specify settings, the :ref:`Cost-Item Table <sec02-costInformation>`, the :ref:`Depth-Replacement-Factor (DRF) Database <sec02-DRF>`, and the :ref:`Fixed Costs <sec02-fixedCosts>` data, complete the **Data Input** tab.
Finally, the four curve creation steps can be executed from the **Create Curve** tab, ending in an export of your DDF in :ref:`CanFlood format <sec02-CanFloodFormat>`.


See the :ref:`User Guide <sec02-userGuide>` and the :ref:`Tutorials <sec03-tutorials>` section to learn more.


.. _sec01-faq:

Frequently Asked Questions
--------------------------

**Where can I find Cost-Item data for my archetype?**
    Typically this information is obtained from cost restoration experts using specialized software like Xactimate and a detailed model of the structure.

**How can I add entries to my Depth-Replacement-Factor (DRF) Database**
    You'll need to use some software that allows editing of SQLite databases. We recommend `DB Browser for SQLite <https://sqlitebrowser.org/>`_.




