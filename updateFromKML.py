# -*- coding: utf-8 -*-
# Make sure to run this without other conflicting processes. Remember to QC and clean up data after run!
# Notes: 
    #   Use correct Python interpreter (mine is "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe")
    #   Append projected_fc to feature service manually, b/c as of 11/19/2021, the feature_layer.append() method kept throwing this error:
        # Object reference not set to an instance of an object.
        # (Error Code: 400)

import arcpy
import sys, os, re

import config

kmz_path = config.updateFromKML["kmz_path"]
kmz_file = config.updateFromKML["kmz_file"]
kmz_file_path = kmz_path + kmz_file
kmz_filename = os.path.splitext(kmz_file)[0]
starting_numbers = re.findall(r'^\d+', kmz_filename) # returns list
fc_name_wo_spaces = kmz_filename.replace(" ", "_")
fc_name_replaced_numbers = re.sub(r'^\d+[_]', '', fc_name_wo_spaces)
fc_name_final = fc_name_replaced_numbers + "_" + starting_numbers[0]

staging_folder = config.updateFromKML["staging_folder"]
staging_kmzFGDB_path = staging_folder + kmz_filename + ".gdb/"
projected_FGDB = staging_folder + config.updateFromKML["projected_FGDB"]
projected_fc = projected_FGDB + fc_name_final
spatial_ref = arcpy.SpatialReference(config.updateFromKML["spatial_ref"])
transform_method = config.updateFromKML["transform_method"]

delete_list = [staging_kmzFGDB_path, projected_fc]

master_FGDB = config.appendTo["master_FGDB"]
master_FC = master_FGDB + config.appendTo["master_FC"] 

projected_fc_fields = ['BeginTime', 'Name', 'PopupInfo']
master_FC_fields = ['SurveyDate','CommonName','FieldNotes']


def removeExisting():
    # Remove stale data
    for i in delete_list:
        # Remove FC if exists
        if arcpy.Exists(projected_fc):
            arcpy.management.Delete(projected_fc)
            print(arcpy.GetMessages())
            print(f"Completed removing existing {i}")


# Convert KMZ file to Points FC (and layer)
def kmlToFC():
    try:
        # Remove stale data
        removeExisting()
        # Convert KML/KMZ file
        arcpy.conversion.KMLToLayer(kmz_file_path, staging_folder) # https://pro.arcgis.com/en/pro-app/latest/tool-reference/conversion/kml-to-layer.htm
        # arcpy.AddMessage(arcpy.GetMessages())
        print(f"Completed KML to Layer from {kmz_file_path} to {staging_folder}")
        print(arcpy.GetMessages())
        # When indexing the result object or using its getOutput() method, the return value is a string.
        # print(kml_layer[0])
        staging_kmzfc = staging_kmzFGDB_path + "Placemarks/Points"
        # print(staging_fc)
        arcpy.management.Project(staging_kmzfc, projected_fc, spatial_ref, transform_method)
        print(f"Completed Projecting {staging_kmzfc} to {projected_fc}, using {spatial_ref.name} and {transform_method}")
        print(arcpy.GetMessages())
          
    # Return geoprocessing specific errors
    except arcpy.ExecuteError:    
        print(arcpy.GetMessages()) 
    # Return any other type of error
    except:
        # By default any other errors will be caught here
        e = sys.exc_info()[1]
        print(e.args[1])  


# Append Projected FC to Master FC and Feature Service!
def appendTo():
    try:
        insert_cursor = arcpy.da.InsertCursor(master_FC, master_FC_fields+['SHAPE@'])
        
        count1 = arcpy.management.GetCount(master_FC)
        print(f"{master_FC} is starting with a feature count of {count1}")
        
        new_rows = 0
        with arcpy.da.SearchCursor(projected_fc, projected_fc_fields+['SHAPE@']) as cursor:
            for row in cursor:
                insert_cursor.insertRow(row)
                new_rows += 1

        del insert_cursor
        
        print(f"Completed adding {new_rows} total features to {master_FC}")
        count2 = arcpy.management.GetCount(master_FC)
        print(f"{master_FC} now has a feature count of {count2}")
        print(arcpy.GetMessages())  
    # Return geoprocessing specific errors
    except arcpy.ExecuteError:    
        print(arcpy.GetMessages()) 
    # Return any other type of error
    except:
        # By default any other errors will be caught here
        e = sys.exc_info()[1]
        print(e.args[1]) 
        

if __name__ == "__main__":
    removeExisting()
    kmlToFC()
    appendTo()
    
    