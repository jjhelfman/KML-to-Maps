# This script is intended to be used in a script tool for an ArcGIS Pro project
# From the script tool properties, assign the figFolder string parameter as a Folder data type.
import arcpy

aprx = arcpy.mp.ArcGISProject("CURRENT")
figFolder = arcpy.GetParameterAsText(0) 

for lyt in aprx.listLayouts():
    print(" {0} ({1} x {2} {3})".format(lyt.name, lyt.pageHeight, lyt.pageWidth, lyt.pageUnits))
    lyt.exportToPDF(figFolder + "\\" + lyt.name + ".pdf")
