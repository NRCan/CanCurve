.. _sec01-gettingStarted:

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
CanCurve is a collection of tools for generating Depth Damage Functions (DDF)for use in flood risk modelling platforms like `CanFlood <https://github.com/NRCan/CanFlood>`.

The CanCurve Buildings Tool generates DDFs from detailed restoration cost data for archetypal buildings.:ref:`Buildings Tool <sec02-bldgs>`
The tool joins together multiple datasets to  
#. Cost-Item Table: a table of restoration activities and their costs (e.g., repair dry-wall for $1000), :ref:`Cost-Item Table <sec02-costItem>`.
#. Depth-Replacement-Factor (DRF) Database: This database provides information on the flood vulnerability of varios items, :ref:`Depth-Replacement-Factor (DRF) Database <sec02-DRF>`.

A DDF, is generated with the following steps: 
#. **Item 1. Populating Building Metadata:** input building metadata using the Buildings Tool.
#. **Item 2. Prepare the Cost-Item Table:** Use local pricing data and expert knowledge to compile a list of restoration activities and costs for the target building or archetype. :ref:`Cost-Item Table <sec02-costItem>`
#. **Item 3. Select DRF Database:** Either use the default DRF Database included with CanCurve, or add your own file. :ref:`DRF Database <sec02-DRF>` 
 #. **Item 4. Create the DDF Curve:** Create and export a DDF for use in CanFlood :ref:`Curve Creation <sec02-Core>`  


.. _sec01-quick:

Quick-Start
-----------------------
After installing the plugin, the |CanCurve_icon| icon should appear on your plugins toolbar.
If you don't see the icon, first ensure the plugin is checked on the **Installed** tab of the **Manage and Install Plugins..** dialog; then ensure the **plugins toolbar** is enabled by right-clicking the QGIS toolbar.

.. |CanCurve_icon| image:: /assets/icon_solid.png
   :align: middle
   :width: 14

To start using CanCurve, click the |CanCurve_icon| and open the :ref:`Buildings Tool <sec02-bldgs>` dialog.

#. **Step 1. Populate the Metadata tab:** Enter availabel information into the Metadata tab. Only fields marked with an asterisk (*) are mandatory, but the more information you provide, the more complete your DDF will be. For example data, see the (:ref:`Tutorials <sec03-tutorials>`. 
#. **Step 2. Data input tab:** Specify settings for datasets including the **Cost-Item Table**, the **Depth-Replacement Factor (DRF)** and **Fixed Costs**. (:ref:`Cost-Item Table <sec02-costItem>`, :ref:`Depth-Replacement Factor (DRF) Database <sec02-DRF>`, and :ref:`Fixed Costs <sec02-fixedCosts>`. 
#. **Step 3. Create and Export the DDF:** Go to the **Create Curve** tag and execute the four curve creation steps. This will generate and export your DDF in the :ref:`CanFlood format <sec02-CanFloodFormat>`.


For additional guidance, see the :ref:`User Guide <sec02-userGuide>` and the :ref:`Tutorials <sec03-tutorials>`.


.. _sec01-faq:

Frequently Asked Questions
--------------------------

**Where can I find Cost-Item data for my archetype?**
    Typically this information is obtained from cost restoration experts using specialized software like Xactimate and a detailed model of the structure.

**How can I add entries to my Depth-Replacement-Factor (DRF) Database**
    You'll need to use software that allows editing of SQLite databases. We recommend `DB Browser for SQLite <https://sqlitebrowser.org/>`_.

**Where can I go to get help?**
    The best place to get help is the `CanCurve GitHub Issues <https://github.com/NRCan/CanCurve/issues>`_ page where you can read through questions posted by others or ask your own.

**Do I really need to install an old version of QGIS to use CanCurve**
      No, but we recommend it for best performance. If you have a newer version of QGIS installed, you can try CanCurve, but you may experience issues.

      




