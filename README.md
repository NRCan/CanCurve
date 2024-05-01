# CanCurve
CanCurve is an open-source tool which can develop depth-damage (stage-damage) functions for use in flood loss estimation and flood risk assessments.

<p align="center">
  <img src="./cancurve/img/icon.png" alt="CanCurve Icon"> 
</p>
 

## Installation
- Install [QGIS 3.34.5](https://download.qgis.org/downloads/) (with Qt 5.15.13)
- download the `cancurve.zip` file from the latest release to your local machine
- in QGIS, `Manage and Install Plugins...` > `Install from ZIP` > select the downloaded file
- it is recommended to also install the **First Aid** plugin for more detailed error messages. 
- it is recommended to set up the QGIS Debug Log file as shown [here](https://stackoverflow.com/a/61669864/9871683)



## USE
1) populate the **Building Details** and **Data Input** tabs to reflect your archetype and cost-item properties
2) on the **Create Curve** tab, either click `Run All` to execute the full DDF compilation workflow, or select `Individual Steps` and click through the steps individually. The resulting DDF will be exported in CanFlood format.

### DEVELOPMENT TESTING
The **Welcome** tab contains a temporary `Load Testing Values` button where you can select from the pre-populated test cases. This should make playing with the tool easier. 
