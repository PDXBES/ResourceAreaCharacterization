import config
import arcpy
import time

# This script does intersections of multiple inputs to determine the areas of treated stormwater in a given resource area.
# Output is provided as a time stamped gdb.
# Currently all intermediate steps are saved out as feature classes
# ==> Program is meant to be run using the ArcPro version of Python <==


def characterize_resource():

    #create new time stamped gdb
    gdb_name = time.strftime("ResourceAreas_%m_%d_%Y_%H_%M")

    arcpy.CreateFileGDB_management(config.output_folder, gdb_name, "10.0")
    gdb_path = config.output_folder + r"/" + gdb_name + r".gdb/"

    working_resource_areas_path = gdb_path + config.resource_area_characterization
    imp_intersect_path = gdb_path + 'imp_intersect'
    imp_intersect_dissolved_path = gdb_path + 'imp_intersect_dissolved'

    mem = 'memory/'
    #feature_classes_in_memory = []

    #this copies the resource area and removes extra fields
    arcpy.Dissolve_management(config.resource_areas, gdb_path + config.resource_area_characterization, 'NewSiteNum')

    working_resource_areas_layer = arcpy.MakeFeatureLayer_management(gdb_path + config.resource_area_characterization, 'working_resource_areas_layer')
    #add all the new fields
    arcpy.AddField_management(working_resource_areas_layer,'Resource_Area_sqft', 'DOUBLE')
    arcpy.CalculateField_management(working_resource_areas_layer,'Resource_Area_sqft',0)

    arcpy.AddField_management(working_resource_areas_layer,'ImpA_sqft', 'DOUBLE')
    arcpy.CalculateField_management(working_resource_areas_layer,'ImpA_sqft',0)

    arcpy.AddField_management(gdb_path + config.resource_area_characterization,'Total_Treated_sqft', 'DOUBLE')
    arcpy.CalculateField_management(gdb_path + config.resource_area_characterization,'Total_Treated_sqft',0)

    arcpy.AddField_management(gdb_path + config.resource_area_characterization,'Total_Untreated_sqft', 'DOUBLE')
    arcpy.CalculateField_management(gdb_path + config.resource_area_characterization,'Total_Untreated_sqft',0)

    arcpy.AddField_management(gdb_path + config.resource_area_characterization,'ImpA_BMP_Treated_sqft', 'DOUBLE')
    arcpy.CalculateField_management(gdb_path + config.resource_area_characterization,'ImpA_BMP_Treated_sqft',0)

    arcpy.AddField_management(gdb_path + config.resource_area_characterization,'ImpA_UIC_Treated_sqft', 'DOUBLE')
    arcpy.CalculateField_management(gdb_path + config.resource_area_characterization,'ImpA_UIC_Treated_sqft',0)

    arcpy.AddField_management(working_resource_areas_layer,'Combined_ImpA_sqft', 'DOUBLE')
    arcpy.CalculateField_management(working_resource_areas_layer, 'Combined_ImpA_sqft', 0)

    arcpy.AddField_management(gdb_path + config.resource_area_characterization,'Sanitary_ImpA_sqft', 'DOUBLE')
    arcpy.CalculateField_management(gdb_path + config.resource_area_characterization,'Sanitary_ImpA_sqft', 0)

    ##Impervious Area


    #intersect impervious areas and resource areas in memory
    #imp_intersect = arcpy.Intersect_analysis([working_resource_areas_path, config.modeled_impervious_areas], imp_intersect_path)
    imp_intersect = arcpy.PairwiseIntersect_analysis([working_resource_areas_path, config.modeled_impervious_areas], imp_intersect_path)

    #dissolve on NewSiteNum
    imp_intersect_dissolved = arcpy.Dissolve_management(imp_intersect_path, imp_intersect_dissolved_path, 'NewSiteNum')

    #make a feature layer
    imp_intersect_dissolved_layer = arcpy.MakeFeatureLayer_management(imp_intersect_dissolved, 'imp_intersect_dissolved_layer')

    # join the impervious area to the resource area and transfer area to 'ImpA_sqft'
    joined = arcpy.AddJoin_management(working_resource_areas_layer, 'NewSiteNum', imp_intersect_dissolved_layer, 'NewSiteNum')
    arcpy.CalculateField_management(working_resource_areas_layer, "ImpA_sqft", "!imp_intersect_dissolved.Shape_Area!")
    arcpy.RemoveJoin_management(working_resource_areas_layer)

    ##BMP Areas
    #get intersection of bmp and resource areas, dissolve the result, make a feature layer so it can be joined
    bmp_intersect_resource = arcpy.Intersect_analysis([working_resource_areas_layer, config.bmp_areas], gdb_path + 'bmp_intersect_resource')
    bmp_intersect_resource_dissolved = arcpy.Dissolve_management(bmp_intersect_resource, gdb_path + 'bmp_intersect_resource_dissolved', 'NewSiteNum')
    bmp_intersect_resource_dissolved_layer = arcpy.MakeFeatureLayer_management(bmp_intersect_resource_dissolved, 'bmp_intersect_resource_dissolved_layer')

    ##BMPs intersected with impervious areas
    bmp_intersect_impervious = arcpy.Intersect_analysis([bmp_intersect_resource_dissolved, imp_intersect_dissolved_layer], gdb_path + 'bmp_intersect_impervious')
    bmp_intersect_impervious_dissolved = arcpy.Dissolve_management(bmp_intersect_impervious, gdb_path + 'bmp_intersect_impervious_dissolved', 'NewSiteNum')
    bmp_intersect_impervious_dissolved_layer = arcpy.MakeFeatureLayer_management(bmp_intersect_impervious_dissolved, 'bmp_intersect_impervious_dissolved_layer')

    ##UIC Areas
    #get intersection of uic and resource areas, dissolve the result, make a feature layer so it can be joined

    uic_intersect_resource = arcpy.Intersect_analysis([working_resource_areas_layer, config.uic_areas], gdb_path + 'uic_intersect_resource')
    uic_intersect_dissolved = arcpy.Dissolve_management(uic_intersect_resource, gdb_path + 'uic_intersect_dissolved', 'NewSiteNum')
    uic_intersect_dissolved_layer = arcpy.MakeFeatureLayer_management(uic_intersect_dissolved, 'uic_intersect_dissolved_layer')

    ##UICs intersected with impervious areas
    uic_intersect_impervious = arcpy.Intersect_analysis([uic_intersect_dissolved, imp_intersect_dissolved_layer], gdb_path + 'uic_intersect_impervious')
    uic_intersect_impervious_dissolved = arcpy.Dissolve_management(uic_intersect_impervious, gdb_path + 'uic_intersect_impervious_dissolved', 'NewSiteNum')
    uic_intersect_impervious_dissolved_layer = arcpy.MakeFeatureLayer_management(uic_intersect_impervious_dissolved, 'uic_intersect_impervious_dissolved_layer')


    arcpy.AddJoin_management(working_resource_areas_layer, 'NewSiteNum', bmp_intersect_impervious_dissolved_layer, 'NewSiteNum')
    arcpy.CalculateField_management(working_resource_areas_layer, "ImpA_BMP_Treated_sqft", "!bmp_intersect_impervious_dissolved.Shape_Area!")
    #copy out the join to see whats up
    arcpy.CopyFeatures_management(working_resource_areas_layer, gdb_path + 'watershed_resource_combined_intersect_dissolved_bmp_join')
    arcpy.RemoveJoin_management(working_resource_areas_layer)


    arcpy.AddJoin_management(working_resource_areas_layer, 'NewSiteNum', uic_intersect_impervious_dissolved_layer, 'NewSiteNum')
    arcpy.CalculateField_management(working_resource_areas_layer, "ImpA_UIC_Treated_sqft", "!uic_intersect_impervious_dissolved.Shape_Area!")
    #copy out the join to see whats up
    arcpy.CopyFeatures_management(working_resource_areas_layer, gdb_path + 'watershed_resource_combined_intersect_dissolved_uic_join')

    arcpy.RemoveJoin_management(working_resource_areas_layer)


    ##UICs intersected with impervious areas
    ##Combined Sewer
    #Make layer to filter by sewer area, dissolve, make layer on the dissolved result so it can be joined
    combined_sewer_area = arcpy.MakeFeatureLayer_management(config.sewer_basin_areas, 'combined_sewer_area', "TYPE =  'C'")
    combined_sewer_area_dissolved = arcpy.Dissolve_management(combined_sewer_area, "memory/combined_dissolved", "TYPE")
    combined_sewer_area_dissolved_layer = arcpy.MakeFeatureLayer_management(combined_sewer_area_dissolved, 'combined_sewer_area_dissolved_layer')


    #Sanitary Sewer
    #Make layer to filter by sewer area, dissolve, make layer on the dissolved result so it can be joined
    sanitary_sewer_area = arcpy.MakeFeatureLayer_management(config.sewer_basin_areas, 'sanitary_sewer_area', "TYPE =  'S'")
    sanitary_sewer_area_dissolved = arcpy.Dissolve_management(sanitary_sewer_area, "memory/sanitary_dissolved", "TYPE")
    sanitary_sewer_area_dissolved_layer = arcpy.MakeFeatureLayer_management(sanitary_sewer_area_dissolved, 'sanitary_sewer_area_dissolved_layer')


    #intersect watershed areas and combined sewer areas
    watershed_resource_combined_intersect = arcpy.Intersect_analysis([working_resource_areas_layer, combined_sewer_area_dissolved_layer], "memory/watershed_resource_combined_intersect")
    watershed_resource_combined_intersect_dissolved = arcpy.Dissolve_management(watershed_resource_combined_intersect, "memory/watershed_resource_combined_intersect_dissolved",'NewSiteNum' )
    arcpy.CopyFeatures_management(watershed_resource_combined_intersect_dissolved, gdb_path + 'watershed_resource_combined_intersect_dissolved')

    watershed_resource_combined_intersect_dissolved_layer = arcpy.MakeFeatureLayer_management(watershed_resource_combined_intersect_dissolved, 'watershed_resource_combined_intersect_dissolved_layer')
    ##
    #
    #intersect new combined areas with impervious areas and dissolve
    watershed_resource_combined_intersect_impervious = arcpy.Intersect_analysis([watershed_resource_combined_intersect_dissolved, imp_intersect_dissolved_layer], "memory/watershed_resource_combined_intersect_impervious")
    watershed_resource_combined_intersect_impervious_dissolved = arcpy.Dissolve_management(watershed_resource_combined_intersect_impervious, "memory/watershed_resource_combined_intersect_impervious_dissolved", 'NewSiteNum')
    arcpy.CopyFeatures_management(watershed_resource_combined_intersect_impervious_dissolved, gdb_path + 'watershed_resource_combined_intersect_impervious_dissolved')
    watershed_resource_combined_intersect_impervious_dissolved_layer = arcpy.MakeFeatureLayer_management(watershed_resource_combined_intersect_impervious_dissolved, 'watershed_resource_combined_intersect_impervious_dissolved_layer')

    #intersect watershed areas and sanitary sewer areas
    watershed_resource_sanitary_intersect = arcpy.Intersect_analysis([working_resource_areas_layer, sanitary_sewer_area_dissolved_layer], "memory/watershed_resource_sanitary_intersect")
    watershed_resource_sanitary_intersect_dissolved = arcpy.Dissolve_management(watershed_resource_sanitary_intersect, "memory/watershed_resource_sanitary_intersect_dissolved",'NewSiteNum' )

    arcpy.CopyFeatures_management(watershed_resource_sanitary_intersect_dissolved, gdb_path + 'watershed_resource_sanitary_intersect_dissolved')

    watershed_resource_sanitary_intersect_dissolved_layer = arcpy.MakeFeatureLayer_management(watershed_resource_sanitary_intersect_dissolved, 'watershed_resource_sanitary_intersect_dissolved_layer')
    #
    #
    #intersect new sanitary areas with impervious areas and dissolve
    watershed_resource_sanitary_intersect_impervious = arcpy.Intersect_analysis([watershed_resource_sanitary_intersect_dissolved, imp_intersect_dissolved_layer], "memory/watershed_resource_sanitary_intersect_impervious")
    watershed_resource_sanitary_intersect_impervious_dissolved = arcpy.Dissolve_management(watershed_resource_sanitary_intersect_impervious, "memory/watershed_resource_sanitary_intersect_impervious_dissolved", 'NewSiteNum')
    arcpy.CopyFeatures_management(watershed_resource_sanitary_intersect_impervious_dissolved, gdb_path + 'watershed_resource_sanitary_intersect_impervious_dissolved')
    watershed_resource_sanitary_intersect_impervious_dissolved_layer = arcpy.MakeFeatureLayer_management(watershed_resource_sanitary_intersect_impervious_dissolved, 'watershed_resource_sanitary_intersect_impervious_dissolved_layer')

    #join combined and sanitary impervious areas and transfer the areas

    arcpy.AddJoin_management(working_resource_areas_layer, 'NewSiteNum', gdb_path + 'watershed_resource_combined_intersect_impervious_dissolved', 'NewSiteNum')
    arcpy.CalculateField_management(working_resource_areas_layer, 'Combined_ImpA_sqft', '!watershed_resource_combined_intersect_impervious_dissolved.Shape_Area!')
    arcpy.RemoveJoin_management(working_resource_areas_layer)

    arcpy.AddJoin_management(working_resource_areas_layer, 'NewSiteNum', gdb_path + 'watershed_resource_sanitary_intersect_impervious_dissolved', 'NewSiteNum')
    arcpy.CalculateField_management(working_resource_areas_layer, 'Sanitary_ImpA_sqft', '!watershed_resource_sanitary_intersect_impervious_dissolved.Shape_Area!')
    arcpy.RemoveJoin_management(working_resource_areas_layer)



    #prior to calculating total treated, need to merge UIC and BMP areas and then dissolve to remove duplicates
    merged_uic_and_bmp = arcpy.Merge_management([bmp_intersect_impervious_dissolved_layer, uic_intersect_impervious_dissolved_layer], 'memory/merged_uic_and_bmp')
    merged_uic_and_bmp_dissolved = arcpy.Dissolve_management(merged_uic_and_bmp, 'memory/merged_uic_and_bmp_dissolved', 'NewSiteNum')
    merged_uic_and_bmp_dissolved_layer = arcpy.MakeFeatureLayer_management(merged_uic_and_bmp_dissolved, 'merged_uic_and_bmp_dissolved_layer')
    arcpy.CopyFeatures_management(merged_uic_and_bmp_dissolved_layer,  gdb_path + 'merged_uic_and_bmp_dissolved')

    new_join = arcpy.AddJoin_management(working_resource_areas_layer, 'NewSiteNum', gdb_path + 'merged_uic_and_bmp_dissolved', 'NewSiteNum')
    arcpy.CopyFeatures_management(new_join, gdb_path + 'new_join')

    arcpy.CalculateField_management(working_resource_areas_layer, 'Total_Treated_sqft', '!merged_uic_and_bmp_dissolved.Shape_Area!')
    arcpy.RemoveJoin_management(working_resource_areas_layer)

    arcpy.CalculateField_management(working_resource_areas_layer, 'Total_Untreated_sqft', "!ImpA_sqft!- !Total_Treated_sqft!", "PYTHON3")
    arcpy.CalculateField_management(working_resource_areas_layer, 'Resource_Area_sqft', "!Shape_Area!", "PYTHON3")

    #create copies of feature classes
    arcpy.CopyFeatures_management(combined_sewer_area_dissolved_layer, gdb_path + 'combined_sewer_area_dissolved_layer')
    arcpy.CopyFeatures_management(sanitary_sewer_area_dissolved_layer, gdb_path + 'sanitary_sewer_area_dissolved_layer')

if __name__ == "__main__":
    characterize_resource()