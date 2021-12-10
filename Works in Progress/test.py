
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


gis_AGOL = GIS(AGOL_url, username, password)
print(f"Successfully connected to {AGOL_url}")
# Create and add AGOL staging FDGB item
# fdgb_AGOL(gis_AGOL)
# Return the feature layer item's object(s) in a list (i.e. title, type and owner props for a Service Definition, then for a Feature Layer Collection)
item = gis_AGOL.content.search(query="title: {}".format(AGOL_FS_title), item_type="Feature Layer") 
print(f"Found item list: {item}")

# Add zipped FGDB to AGOL, to be the source of the Append
# item_fgdb_properties = {"title": fc_name_final + ".gdb",
                    # "type": "File Geodatabase"}
# item_fgdb = gis_AGOL.content.add(item_properties=item_fgdb_properties, data=fgdb_AGOL_zipped)
item_fgdb_id = 'd17646a0340f45dfa9e4066a1064665e'
# print(f"Successfully added {fc_name_final}" + f".zip to {AGOL_url}")
# item_fgdb 

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
feature_layer.append(item_id=item_fgdb_id, upload_format='featureCollection', source_table_name=fc_name_final, upsert=False)
