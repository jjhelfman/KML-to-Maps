# -*- coding: utf-8 -*-
# Make sure to run this without other conflicting processes. Remember to QC and clean up data after run!
# Notes: 
    #   Use correct Python interpreter (mine is "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe")
    #   Append projected_fc to feature service manually, b/c as of 11/19/2021, the feature_layer.append() method keeps throwing this error:
    #   (even after trying different AGOL item types and passing different args (w/o field mappings too))
        #   Object reference not set to an instance of an object.
        #   (Error Code: 400)

import arcpy
import sys, os, shutil, re
import zipfile
import datetime
import config
from arcgis.gis import GIS
from arcgis.features import FeatureLayer

now = datetime.datetime.now() # current date and time
this_year = now.strftime("%Y")

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
# staging_fgdb = fc_name_final + ".gdb"
# staging_fgdb_path = staging_folder + fc_name_final + ".gdb" # ....2021
# staging_fgdb_zipped = staging_folder + fc_name_final + ".zip"
fgdb_AGOL = fc_name_final + "_AGOL.gdb"
fgdb_AGOL_path = staging_folder + fgdb_AGOL
fgdb_AGOL_zipped = staging_folder + fc_name_final + "_AGOL.zip"
fgdbs_list = [staging_kmzFGDB_path, fgdb_AGOL_path]

master_FGDB = config.appendTo["master_FGDB"]
master_FC = master_FGDB + config.appendTo["master_FC"] 

projected_fc_fields = ['BeginTime', 'Name', 'PopupInfo']
master_FC_fields = ['SurveyDate','CommonName','FieldNotes']

username = config.appendToFS["AGOL_username"]
password = config.appendToFS["AGOL_pass"]
AGOL_url = config.appendToFS["AGOL_url"]
AGOL_FS_title = config.appendToFS["AGOL_FS_title"]
item_url = config.appendToFS["item_url"]

def removeExisting():
    # Remove stale data
    for i in fgdbs_list:
        if os.path.exists(i):
            # shutil.rmtree(i)
            arcpy.management.Delete(i) 
            print(f"Completed removing existing {i}")
    # Remove FC if exists
    if arcpy.Exists(projected_fc):
        arcpy.management.Delete(projected_fc)
        print(f"Completed removing existing {projected_fc}")
        print(arcpy.GetMessages())

# Convert KMZ file to Points FC (and layer)
def kmlToFC():
    try:
        # Remove FGDB if exists
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
        e = sys.exc_info()
        print(e) 
        
def fdgb_AGOL(gis_AGOL):
    try:
        # Create and add AGOL staging FDGB item
        # This section is for appendToFS()  
        # Create separate compressed FGDB
        arcpy.management.CreateFileGDB(staging_folder, fgdb_AGOL)
        print(f"Successfully created {fgdb_AGOL}")
        print(arcpy.GetMessages())
        arcpy.conversion.FeatureClassToGeodatabase(projected_fc, fgdb_AGOL_path)
        print(f"Successfully added {projected_fc} to {fgdb_AGOL}")
        print(arcpy.GetMessages())
        
        
        # Remove zipped staging GDB if exists
        if os.path.exists(fgdb_AGOL_zipped):
            shutil.rmtree(fgdb_AGOL_zipped)
            print(f"Completed removing existing {fgdb_AGOL_zipped}")
        
        # shutil.make_archive(staging_fgdb_zipped, 'zip', staging_fgdb_path)
        with zipfile.ZipFile(fgdb_AGOL_zipped, 'w', compression=zipfile.ZIP_DEFLATED) as myzip:
            for file in os.listdir(fgdb_AGOL_path):
                if file[-5:] != '.lock':
                    # print(staging_fgdb_path + "/" + file)
                    myzip.write(fgdb_AGOL_path + "/" + file)
        print(f"Completed creating and compressing {fgdb_AGOL} into {fgdb_AGOL_zipped}")
    
        # Search for existing zipped FGDB items to delete
        fgdbs_to_delete = gis_AGOL.content.search(query="title: {}".format(fc_name_final + ".gdb"), item_type="File Geodatabase")
        print(f"Found existing fgdbs in AGOL: {fgdbs_to_delete}")
        for fgdb_item in fgdbs_to_delete:
            fgdb_item.delete()
            print(f"Deleted {fgdb_item} from AGOL") 

    # # Return geoprocessing specific errors
    except arcpy.ExecuteError:    
        print(arcpy.GetMessages()) 
    # Return any other type of error
    except:
        # By default any other errors will be caught here
        e = sys.exc_info()
        print(e)
     
        
def appendToFS():
    try:
        # Log into AGOL
        gis_AGOL = GIS(AGOL_url, username, password)
        print(f"Successfully connected to {AGOL_url}")
        # Create and add AGOL staging FDGB item
        fdgb_AGOL(gis_AGOL)
        # Return the feature layer item's object(s) in a list (i.e. title, type and owner props for a Service Definition, then for a Feature Layer Collection)
        item = gis_AGOL.content.search(query="title: {}".format(AGOL_FS_title), item_type="Feature Layer") 
        print(f"Found item list: {item}")
        
        # Add zipped FGDB to AGOL, to be the source of the Append
        item_fgdb_properties = {"title": fc_name_final + ".gdb",
                                "type": "File Geodatabase"}
        item_fgdb = gis_AGOL.content.add(item_properties=item_fgdb_properties, data=fgdb_AGOL_zipped)
        item_fgdb_id = item_fgdb[0].id
        print(f"Successfully added {fc_name_final}" + f".zip to {AGOL_url}")
        item_fgdb 
        
        feature_layer = FeatureLayer(item_url)
        
        count1 = feature_layer.query(return_count_only=True)
        print(f"{item[0].title} is starting with a feature count of {count1}")
        
        item_id = str(item[0].id)
        print(item_id)
        
        # Example usage (from https://developers.arcgis.com/python/api-reference/arcgis.features.toc.html#arcgis.features.FeatureLayer.append):
        field_mappings = [{"BeginTime" : "SurveyDate",
                           "Name" : "CommonName",
                           "PopupInfo": "FieldNotes"},]
        # this method needs to be more robust to accept mismatching field types in the field_mappings object {}
        feature_layer.append(item_id=item_fgdb_id, upload_format='filegdb', source_table_name=fc_name_final, upsert=False)
        
        count_projected_fc = arcpy.management.GetCount(projected_fc)
        print(f"Completed adding {count_projected_fc} total features to {item[0].title}")
        count2 = feature_layer.query(return_count_only=True)
        print(f"{item} now has a feature count of {count2}")
        print(arcpy.GetMessages())  
    # # Return geoprocessing specific errors
    except arcpy.ExecuteError:    
        print(arcpy.GetMessages()) 
    # Return any other type of error
    except:
        # By default any other errors will be caught here
        e = sys.exc_info()
        print(e)  

if __name__ == "__main__":
    removeExisting()
    kmlToFC()
    appendTo()
    appendToFS()
    
    