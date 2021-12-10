# This script is intended to be used for a script tool in an open ArcGIS Pro project
import arcpy

aprx = arcpy.mp.ArcGISProject("CURRENT")
figFolder = arcpy.GetParameterAsText(0) # Set this parameter from the script tool properties as a Folder data type

for lyt in aprx.listLayouts():
    print(" {0} ({1} x {2} {3})".format(lyt.name, lyt.pageHeight, lyt.pageWidth, lyt.pageUnits))
    lyt.exportToPDF(figFolder + "\\" + lyt.name + ".pdf")
