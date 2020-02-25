
##need to change this output folder to where you want the gdb to be created
output_folder = r"C:\temp\ResourceArea"

##I was using a local copy of the resource areas but I put the network path back in:
resource_areas = r"\\Cgisfile\Public\BPS\EzoneMapCorrectionProject\Ezone_GIS_Mapping\Remapping_Resources_2019_1_9.gdb\Resource_Sites_Edit_2019_1_9"

egh_public = r"\\oberon\grp117\DAshney\Scripts\connections\egh_public on gisdb1.rose.portland.local.sde"

resource_area_characterization = r"resource_area_characterization"

resource_area_drop_fields = ['Name', 'Site_number', 'Site_OJ', 'Plan_', 'Plan_year',
                             'Site_label', 'Notes', 'TO_DELETE', 'GeographicPlanArea',
                             'Old_ID', 'NewName', 'NewPlanArea']

sewer_basin_areas = egh_public + r"\ARCMAP_ADMIN.sewer_basins_bes_pdx"

uic_areas = r"\\besfile1\asm_projects\9ESPP0000056_UIC\Automation\working.gdb\sump_delin_07_2017"

bmp_areas = r"\\besfile1\Modeling\GridMaster\BMP\PRF\ARC\Working\Drainage_Delineation\DelineationFinal_results.gdb\Delineation_04_2015"

modeled_impervious_areas = egh_public + r"\ARCMAP_ADMIN.emgaats_areas_bes_pdx"

