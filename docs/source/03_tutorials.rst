.. _sec03-tutorials:

Tutorials
==========================

This section contains a collection of tutorials with example data and results.
Be sure to read and follow the :ref:`Getting Started Section <sec01-gettingStarted>` before attempting these tutorials.

.. _sec03-tut01:

Tutorial 1: Single-Story Residential
-------------------------------------

This tutorial will demonstrate how to create a :ref:`CanFlood format DDF <sec02-CanFloodFormat>` from a :ref:`Cost-Item Table <sec02-costItem>` and some default values for a single-story residential building using the :ref:`Buildings Tool <sec02-bldgs>`.

Step 1: Download the example Cost-Item Table
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From the project repository, download the `example Cost-Item Table <https://github.com/NRCan/CanCurve/blob/main/tutorial/01/R_1-L-BD-CU_ABCA.csv>`_ somewhere easy to find.

Step 2: Enter Metadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Open the :ref:`Buildings Tool <sec02-bldgs>`, navigate to the **Metadata** tab, and populate the fields as shown below:


.. figure:: /assets/03_01_meta01.PNG
   :alt: Metadata Tab
   :align: center
   :width: 900px

.. figure:: /assets/03_01_meta02.PNG
   :alt: Metadata Tab
   :align: center
   :width: 900px

   Metadata for Tutorial 1

Step 3: Data Input
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Navigate to the **Data Input** tab and, using the below image for reference, populate the following fields:

 - **Working Directory**: choose your own path or use the default
 - **Project Name**: choose your own name or use the name shown
 - **Cost-Item Table**: browse to the downloaded example Cost-Item Table .csv file from Step 1.
 - **Fixed Costs**: enter the two values shown below.
 - **Cost Basis**: For this tutorial we will use :ref:`Area Based <sec02-costBasis>`.
 - **DRF Database**: By default, the field should be populated with the filepath to the DRF Database that ships with CanCurve.

.. figure:: /assets/03_01_dataInput.PNG
   :alt: Data Input Tab
   :align: center
   :width: 900px

   Data Input page for Tutorial 1

Step 4: Create Curve
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Navigate to the **Create Curve** tab.
In the **Run Control** box, select **All**, then click **Run**.
You should see the progress of each of the four :ref:`Curve Creation Steps <sec02-Core>` along with a message in the bottom window informing you that the DDF has been output to the **Working Directory** you specified in Step 3, similar to what is shown below.

.. figure:: /assets/03_01_cc.PNG
   :alt: Curve Creation Tab
   :align: center
   :width: 900px

   Curve Creation page for Tutorial 1

For additional log messages, you can return to the main QGIS window, open the log panel (View>Panels>Log Messages), and select the **CanCurve** tab.
Scrolling up, you should see diagnostic messages for each of the four steps you just ran.
This is the end of a typical workflow; however, the **Buildings Tool** provides for some additional functionality and output control that you may wish to explore.
For example, selecting the **Individual Steps** radio button will allow you to specify your own project database and generate some diagnostic plots for each step.
Similarly, expanding the **Output Control** box shows some additional options for controlling the output of the tool.




