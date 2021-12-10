# Habitat Management Plans (HMPs)

## This script is for appending new KML point data to point feature classes and layers

1. updateFromKML.py applies the following methods to an open ArcGIS Pro project:
    -   removeExisting() - Removes intermediate data from input
    -   kmlToFC() - Converts KML file to appropriately projected feature class (FC)
    -   appendTo() - Appends the new FC to a master FC  
    -   appendToFL() - Appends the new FC to the correct Feature Layer/Service

2. exportToPDF.py is a script tool that exports all of the layouts from your ArcGIS Pro project. 

## Instructions

**updateFromKML.py**

1. Create a config.py file in the same working directory as this project. Create a dictionary for the string variables defined in the script. A single dictionary should exist per method. Confirm that the data paths specified as variables are correct. The shallower the data paths, the better this script will run. 
2. Open an ArcGIS Pro project with the appropriately named map with the correct point Feature Layer to append to. 
3. Run the script from a Python window inside the open ArcGIS Pro project.

**exportToPDF.py**

1. Create a script tool, assigning the script path to and adding the figFolder str parameter. Documentation is here: https://pro.arcgis.com/en/pro-app/latest/help/analysis/geoprocessing/basics/create-a-python-script-tool.htm. 
2. Run the script tool to export all of your open Project's Layouts. 
