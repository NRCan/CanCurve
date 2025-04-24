[![Documentation Status](https://readthedocs.org/projects/cancurve/badge/?version=latest)](https://cancurve.readthedocs.io/en/latest/?badge=latest)

# CanCurve
CanCurve is an open source tool for developing flood depth-damage (stage-damage) functions for flood assessments.
<p> <em>CanCurve is in active development undergoing evaluation and validation. </em></p>

<p align="center">
  <img src="./cancurve/img/icon.png" alt="CanCurve Icon"> 
</p>
 
 
## Updates
- [v1.2.0](https://github.com/NRCan/CanCurve/releases/tag/v1.2.0) public release
    - update to QGIS 3.40.6
- [v1.1.0](https://github.com/NRCan/CanCurve/releases/tag/v1.1.0) post-release improvements
    - new interface and tools for missing DRF entries
    - rename sel to itemcode add cat lookup label table
- [v1.0.3](https://github.com/NRCan/CanCurve/releases/tag/v1.0.3) pre-release



## Documentation
Project documentation is [here](https://cancurve.readthedocs.io/en/latest/)


## Installing for the first time
- Install [QGIS 3.40.6](https://download.qgis.org/downloads/) (with Qt 5)
- download the `cancurve.zip` file from the [latest release](https://github.com/NRCan/CanCurve/releases) to your local machine
- in QGIS, `Manage and Install Plugins...` > `Install from ZIP` > select the downloaded file
- we recommended to also install the **First Aid** plugin for more detailed error messages 
- we recommended to set up the QGIS Debug Log file as shown [here](https://stackoverflow.com/a/61669864/9871683)
- CanCurve backend and project data is implemented in SQLite relational databases. For enhanced customization and debugging, it is recommended to install a SQLite viewer + editor like [DB Browser for SQLite](https://sqlitebrowser.org/) for working with these files  

## Re-installation/updating
For best performance: follow similar steps to the above, but be sure to **Uninstall** the plugin and restart QGIS first 


## Use
1) populate the **Building Details** and **Data Input** tabs to reflect your archetype and cost-item properties
2) on the **Create Curve** tab, either click `Run All` to execute the full DDF compilation workflow, or select `Individual Steps` and click through the steps individually. The resulting DDF will be exported in CanFlood format.

See the [documentation](https://cancurve.readthedocs.io/en/latest/) for more details.

## Development
see [CONTRIBUTING.md](./CONTRIBUTING.md)

### Testing
The **Welcome** tab contains a temporary `Load Testing Values` button where you can select from the pre-populated test cases. This should make playing with the tool easier. 


