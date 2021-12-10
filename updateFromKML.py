# -*- coding: utf-8 -*-
# Make sure to run this without other conflicting processes. Remember to QC and clean up data after run!
# 1. The kmlToFC() and appendTo() methods can be called from outside of the ArcGIS Pro application
# 2. The appendToFL() method is set up to be called from an open ArcGIS Pro project with a map named "1. HMPs" and a hosted feature layer named "Wildlife Pts" (toss this entire script into the python window; for script tool, the params would need to be set up here!)
# 3. Here, the master_FC (variable pointing to feature class, "C:/HMPs Project/HMPs_Master.gdb/Wildlife_Points") matches what's in the "Wildlife Points" feature layer in AGOL
# Notes: 
    #   Use correct Python interpreter (mine is "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe")
    #   This where history is saved: C:\Users\User\AppData\Roaming\Esri\ArcGISPro\ArcToolbox\History
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
staging_kmzfc = staging_kmzFGDB_path + "Placemarks/Points"
projected_FGDB = staging_folder + config.updateFromKML["projected_FGDB"]
projected_fc = projected_FGDB + fc_name_final
spatial_ref = arcpy.SpatialReference(config.updateFromKML["spatial_ref"])
transform_method = config.updateFromKML["transform_method"]

delete_list = [staging_kmzFGDB_path, projected_fc]

master_FGDB = config.appendTo["master_FGDB"]
master_FC = master_FGDB + config.appendTo["master_FC"] 

projected_fc_fields = ['BeginTime', 'Name', 'PopupInfo']
master_FC_fields = ['SurveyDate','CommonName','FieldNotes']

map_name = config.appendToFL["map_name"]




def removeExisting():
    # Remove stale data
    for i in delete_list:
        # Remove FC if exists
        if arcpy.Exists(projected_fc):
            arcpy.management.Delete(projected_fc)
            msg_Delete = f"Completed removing existing {i}" + arcpy.GetMessages()
            arcpy.AddMessage(msg_Delete)
            print(arcpy.GetMessages()) # for running in IDE


# Convert KMZ file to Points FC (and layer)
def kmlToFC():
    try:
        # Convert KML/KMZ file
        arcpy.conversion.KMLToLayer(kmz_file_path, staging_folder) # https://pro.arcgis.com/en/pro-app/latest/tool-reference/conversion/kml-to-layer.htm
        # arcpy.AddMessage(arcpy.GetMessages())
        msg_KML = f"Completed KML to Layer from {kmz_file_path} to {staging_folder}"
        arcpy.AddMessage(msg_KML)
        print(arcpy.GetMessages())
        # When indexing the result object or using its getOutput() method, the return value is a string.
        # print(kml_layer[0])
        # print(staging_fc)
        arcpy.management.Project(staging_kmzfc, projected_fc, spatial_ref, transform_method)
        msg_Prj = f"Completed Projecting {staging_kmzfc} to {projected_fc}, using {spatial_ref.name} and {transform_method}"
        arcpy.AddMessage(msg_Prj)
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
        msg_Ins = f"Created Insert Cursor for {master_FC}"
        arcpy.AddMessage(msg_Ins)
        print(arcpy.GetMessages())
        
        count1 = arcpy.management.GetCount(master_FC)
        msg_Start = f"{master_FC} is starting with a feature count of {count1}"
        arcpy.AddMessage(msg_Start)
        print(arcpy.GetMessages())
        
        new_rows = 0
        with arcpy.da.SearchCursor(projected_fc, projected_fc_fields+['SHAPE@']) as cursor:
            for row in cursor:
                insert_cursor.insertRow(row)
                new_rows += 1
        del insert_cursor
        
        count2 = arcpy.management.GetCount(master_FC)
        msg_End1 = f"Completed adding {new_rows} total features to {master_FC}"
        msg_End2 = f"{master_FC} now has a feature count of {count2}"
        arcpy.AddMessage(msg_End1 + "\n" + msg_End2)
        print(arcpy.GetMessages())  
    # Return geoprocessing specific errors
    except arcpy.ExecuteError:    
        print(arcpy.GetMessages()) 
    # Return any other type of error
    except:
        # By default any other errors will be caught here
        e = sys.exc_info()[1]
        print(e.args[1]) 
        
def appendToFL():
    try:
        
        # 5.) Loop through Feature Services and Append to Wildlife Points layer 
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        msg_aprx = f"Accessed the ArcGIS Pro project, {aprx}"
        arcpy.AddMessage(msg_aprx)
        print(arcpy.GetMessages())  
        
        m = aprx.listMaps(map_name)[0] # index b/cx method returns a list
        msg_map = f"Accessed {map_name}map. Now looking through its layers!"
        arcpy.AddMessage(msg_map)
        print(arcpy.GetMessages())
        for lyr in m.listLayers():
            msg_lyr = f"The {map_name} map has a layer named {lyr.name}"
            arcpy.AddMessage(msg_lyr)
            print(arcpy.GetMessages())  
            if lyr.name == "Wildlife Points":  
                insert_cursor = arcpy.da.InsertCursor(lyr, master_FC_fields+['SHAPE@'])
                msg_Inslyr = f"Created Insert Cursor for {lyr.name}"
                arcpy.AddMessage(msg_Inslyr)
                print(arcpy.GetMessages())
                
                count1 = arcpy.management.GetCount(lyr)
                msg_count1 = f"{lyr} is starting with a feature count of {count1}"
                arcpy.AddMessage(msg_count1)
                print(arcpy.GetMessages())
                
                new_rows = 0
                with arcpy.da.SearchCursor(projected_fc, projected_fc_fields+['SHAPE@']) as cursor:
                    for row in cursor:
                        insert_cursor.insertRow(row)
                        new_rows += 1
                del insert_cursor
                
                count2 = arcpy.management.GetCount(lyr)
                msg_End1 = f"Completed adding {new_rows} total features to {lyr}"
                msg_End2 = f"{lyr} now has a feature count of {count2}"
                arcpy.AddMessage(msg_End1 + "\n" + msg_End2)
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
    appendToFL()
    
    