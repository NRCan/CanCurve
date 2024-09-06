# CanCurve
CanCurve is an open-source tool for developing flood depth-damage (stage-damage) functions for use flood assessments.

<p align="center">
  <img src="./cancurve/img/icon.png" alt="CanCurve Icon"> 
</p>
 
 
## Updates
- 2024-08-22: priority A and B fixes [v0.1.0](https://github.com/NRCan/CanCurve/releases/tag/v0.1.0)
- 2024-05-09: small fixes and updates based on initial comments
- 2024-05-01: initial working release (un tested) [v0.0.1](https://github.com/NRCan/CanCurve/releases/tag/v0.0.1)


## Documentation
 CanCurve is an open-source tool which can be used to create depth-damage (stage-damage) functions for use in flood loss estimation and flood risk assessments. 
## Background
In Canada, a limited number of developed damage functions are available to support flood risk assessments. The existing functions lack a standardized process, and the underlying algorithms and data to derive them are unclear, making them a bit of a ‘black box.’ Additionally, transferability from one region to another can be challenging. 
<p>
Previous work in 2023 explored the development of a framework for developing depth damage functions. This work resulted in a synthesis of the existing methods being used in Canada to develop depth damage functions. Additionally, it included some details on work done internationally. Several limitations to existing approaches were identified, and a novel and more transparent way to develop depth damage curves was proposed.
<p></p>
CanCurve uses room component replacement costs to generate Depth Damage Functions (DDF) from detailed restoration cost data. This approach allows for a clearer understanding of the contributing components to the overall losses experienced during a flood event. The tool joins cost data to a database of item vulnerability. Then, it groups the data by water depth to create a simple function for flood damage against flood depth. 
<p></p>
The tool also allows users to aggregate data using pivot tables to view items, rooms, and damage estimates at various levels of aggregation. This added flexibility and transparency will provide users with a better understanding of the DDF data used in the calculation, allowing for more informed decisions on the applicability of curves to use and allow for easier translation for use in other regions.  
<p></p>


## Installing for the first time
- Install [QGIS 3.34.5](https://download.qgis.org/downloads/) (with Qt 5.15.13)
- download the `cancurve.zip` file from the latest release to your local machine
- in QGIS, `Manage and Install Plugins...` > `Install from ZIP` > select the downloaded file
- it is recommended to also install the **First Aid** plugin for more detailed error messages. 
- it is recommended to set up the QGIS Debug Log file as shown [here](https://stackoverflow.com/a/61669864/9871683)
- CanCurve backend and project data is implemented in SQLite relational databases. For enhanced customization and debugging, it is recommended to install a SQLite viewer + editor like [DB Browser for SQLite](https://sqlitebrowser.org/) for working with these files.  

## Re-installation/updating
For best performance: follow similar steps to the above, but be sure to **Uninstall** the plugin and restart QGIS first. 


## USE
1) populate the **Building Details** and **Data Input** tabs to reflect your archetype and cost-item properties
2) on the **Create Curve** tab, either click `Run All` to execute the full DDF compilation workflow, or select `Individual Steps` and click through the steps individually. The resulting DDF will be exported in CanFlood format.

## Development
see [CONTRIBUTING.md](./CONTRIBUTING.md)

### Testing
The **Welcome** tab contains a temporary `Load Testing Values` button where you can select from the pre-populated test cases. This should make playing with the tool easier. 


