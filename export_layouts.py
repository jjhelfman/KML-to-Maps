# This script is intended to be used in a script tool for an ArcGIS Pro project
# From the script tool properties,
# assign the appropriate parameters.

import arcpy

aprx = arcpy.mp.ArcGISProject("CURRENT")
all_layouts = aprx.listLayouts()

output_path = arcpy.GetParameterAsText(0)
output_ext = arcpy.GetParameterAsText(1)
output_res = int(arcpy.GetParameter(2))
PDF_quality = arcpy.GetParameterAsText(3)
JPEG_TIFF_quality = int(arcpy.GetParameterAsText(4))
PDF_compr = arcpy.GetParameterAsText(5)
TIFF_compr = arcpy.GetParameterAsText(6)
output_embed = arcpy.GetParameter(7)
clipped_elements = arcpy.GetParameter(8) # False, by default
world_files = arcpy.GetParameter(9) # False, by default
geoTIFF_tag = arcpy.GetParameter(10) # False, by default


if output_ext == "PDF":
    for lyt in all_layouts:
        lyt.exportToPDF(output_path + "/" + lyt.name, resolution=output_res, image_quality=PDF_quality, image_compression=PDF_compr, embed_fonts=output_embed)

if output_ext in ["JPEG", "JPG"]:
    for lyt in all_layouts:
        lyt.exportToJPEG(out_jpg=output_path + "/" + lyt.name, resolution=output_res, jpeg_quality=JPEG_TIFF_quality, clip_to_elements=clipped_elements)

if output_ext == "PNG":
    for lyt in all_layouts:
        lyt.exportToPNG(output_path + "/" + lyt.name, resolution=output_res, clip_to_elements=clipped_elements)

if output_ext == "TIFF":
    for lyt in all_layouts:
        lyt.exportToTIFF(output_path + "/" + lyt.name, resolution=output_res, color_mode='24-BIT_TRUE_COLOR', tiff_compression=TIFF_compr, jpeg_compression_quality=JPEG_TIFF_quality, transparent_background=False, embed_color_profile=True, clip_to_elements=clipped_elements, world_file=world_files, geoTIFF_tags=geoTIFF_tag)