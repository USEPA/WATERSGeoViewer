from __future__ import print_function;

import arcpy
import os
import __builtin__
import xml.dom.minidom as DOM;

#------------------------------------------------------------------------------
#
str_script   = "Waters Services GP Services Deployment Script";
num_version  = 3.0;
str_author   = "Paul Dziemiela, Eastern Research Group";
str_last_mod = "August 11, 2017";
#
#------------------------------------------------------------------------------
arcpy.AddMessage(" ");
arcpy.AddMessage(str_script);
arcpy.AddMessage("Version: " + str(num_version));
arcpy.AddMessage("By " + str_author);
arcpy.AddMessage("Last Modified: " + str_last_mod);
arcpy.AddMessage(" ");

#------------------------------------------------------------------------------
# Step 10
# Collect AGS catalog connection
#------------------------------------------------------------------------------
catalog = None;
keyword = None;

arcpy.AddMessage("Verifying connections...");

if len(sys.argv) > 1:
   catalog = sys.argv[1];

if len(sys.argv) > 2:
   keyword = sys.argv[2];

if catalog is None:
   print(" Please provide your ArcCatalog AGS connection as parameter one.");
   print(" ");
   exit(-1);

if catalog[-4:] != ".ags":
   catalog = catalog + ".ags"
   
ags_con = "GIS Servers\\" + catalog;

if not arcpy.Exists(ags_con):
   print(" Connection named GIS Servers\\" + catalog + " not found.");
   print(" ");
   exit(-1);
   
arcpy.AddMessage(" Service will be deployed to " + ags_con);
   
###############################################################################
#                                                                             #
#  Set the service parameters                                                 #
#  This section is generally editable                                         #
#                                                                             #
#

draft_service_name   = "GeoplatformDrainageAreaDelineation";
draft_folder_name    = "WATERS_SERVICES";
draft_summary        = "The EPA Office of Water Watershed Delineation Service provides an areal representation of the navigation process by linking navigated flowlines to associated areal geographies. The service has been optimized to aggregate and return NHDPlus catchments."
draft_tags           = "EPA";
draft_execution_type = "ASynchronous";
draft_max_records    = 1000000;
draft_maxUsageTime   = 1200;
draft_maxWaitTime    = 1200;
draft_maxIdleTime    = 1800;

if keyword == "dummy":
   draft_minInstances   = 0;
   draft_maxInstances   = 1;
   
else:
   draft_minInstances   = 2;
   draft_maxInstances   = 4;
   
draft_copy_data_to_server = False;
draft_result_map_server   = False;

# Hash of any additional general properties to be applied to the sddraft file
ags_properties = {}

# Hash of services to enable or disable
ags_services = {
    'WPSServer': True
}

# Array of Hash of properties to be applied to individual services
ags_service_props = {
    'WPSServer': {'abstract': 'EPA Office of Waters WPS Services'}
}

#                                                                             #
# No further changes should be necessary                                      #
###############################################################################

#------------------------------------------------------------------------------
# Step 20
# Verify SDE connection file exists and report on connection for QA purposes
#------------------------------------------------------------------------------
sde_con = sys.path[0] + "\\rad_ags.sde";
if not arcpy.Exists(sde_con):
   arcpy.AddMessage(" Connection named " + sde_con + " not found.");
   arcpy.AddMessage(" ");
   exit(-1);

arcpy.AddMessage(" Service will utilize geodatabase connection at: ");
arcpy.AddMessage("   " + sde_con);

try:
   desc = arcpy.Describe(sde_con);
   cp = desc.connectionProperties;

except arcpy.ExecuteError:
   print(arcpy.GetMessages(2));
       
arcpy.AddMessage(" User    : " + cp.user);
arcpy.AddMessage(" Instance: " + cp.instance);
arcpy.AddMessage(" ");

#------------------------------------------------------------------------------
# Step 30
# Import the toolbox
#------------------------------------------------------------------------------
arcpy.AddMessage("Importing the toolbox...");
try:
   tb = arcpy.ImportToolbox(
      sys.path[0] + "\\M_GeoplatformDrainageAreaDelineation.tbx"
   );

except Exception as err:
   arcpy.AddError(err)
   exit -1;

#------------------------------------------------------------------------------
#- Step 40
#- Dry Run Individual Services to generate results file
#------------------------------------------------------------------------------
__builtin__.dz_deployer = True;

arcpy.AddMessage(" Dry run for DelineateUsingStartingPoint...");
resultFC = tb.DelineateUsingStartingPoint(
    StreamSelectionType    = "Upstream with Tributaries"
   ,StartingPoint          = sys.path[0] + "\\rad_ags.gdb\\Point"
   ,MaxDistanceKm          = ""
   ,ShowSelectedStreams    = "False"
   ,ShowSelectedCatchments = "False"
   ,AdvancedConfiguration  = ""
);
arcpy.AddMessage(" Success.");

arcpy.AddMessage("Done.");
arcpy.AddMessage(" ");

#------------------------------------------------------------------------------
#- Step 50
#- Create the sddraft file
#------------------------------------------------------------------------------
arcpy.AddMessage("Generating sddraft file...");
try:
   sd = arcpy.CreateScratchName(
       "GeoplatformDrainageAreaDelineation"
      ,".sd"
      ,None
      ,arcpy.env.scratchFolder
   );
   
   sddraft = arcpy.CreateScratchName(
       "GeoplatformDrainageAreaDelineation"
      ,".sddraft"
      ,None
      ,arcpy.env.scratchFolder
   );
   
   arcpy.CreateGPSDDraft(
       result               = [resultFC]
      ,out_sddraft          = sddraft
      ,service_name         = draft_service_name
      ,server_type          = "ARCGIS_SERVER"
      ,connection_file_path = ags_con
      ,copy_data_to_server  = draft_copy_data_to_server
      ,folder_name          = draft_folder_name
      ,summary              = draft_summary
      ,tags                 = draft_tags
      ,executionType        = draft_execution_type
      ,resultMapServer      = draft_result_map_server
      ,showMessages         = "INFO"
      ,maximumRecords       = draft_max_records
      ,minInstances         = draft_minInstances
      ,maxInstances         = draft_maxInstances
      ,maxUsageTime         = draft_maxUsageTime
      ,maxWaitTime          = draft_maxWaitTime
      ,maxIdleTime          = draft_maxIdleTime
   );
   
except arcpy.ExecuteError:
   print(arcpy.GetMessages(2));
   
arcpy.AddMessage("Done.");
arcpy.AddMessage(" ");

#------------------------------------------------------------------------------
#- Step 60
#- Analyze the SD
#------------------------------------------------------------------------------
arcpy.AddMessage("Analyzing service definition...");
analysis = arcpy.mapping.AnalyzeForSD(sddraft);

if analysis["errors"] != {}:
   print("---- ERRORS ----");
   vars = analysis["errors"]
   for ((message, code), layerlist) in vars.iteritems():
      print("    ", message, ' (CODE %i)' % code);
      if len(layerlist) > 0:
         print("       applies to:");
         for layer in layerlist:
            print(layer.name);
         print(" ");

if analysis["warnings"] != {}:
   print("---- WARNINGS ----");
   vars = analysis["warnings"]
   for ((message, code), layerlist) in vars.iteritems():
      print("    ", message, ' (CODE %i)' % code);
      if len(layerlist) > 0:
         print("       applies to:");
         for layer in layerlist:
            print(layer.name);
         print(" ");
         
if analysis["messages"] != {}:
   print("---- MESSAGES ----");
   vars = analysis["messages"]
   for ((message, code), layerlist) in vars.iteritems():
      print("    ", message, ' (CODE %i)' % code);
      if len(layerlist) > 0:
         print("       applies to:");
         for layer in layerlist:
            print(layer.name);
         print(" ");
         
if analysis['errors'] == {}:
   arcpy.AddMessage(" No errors found.");
else:
   print(" ");
   print(" Service Errors must be corrected. Exiting.");
   exit(-1);

arcpy.AddMessage("Done.");
arcpy.AddMessage(" ");

#------------------------------------------------------------------------------
#- Step 70
#- Alter the sddraft file 
#------------------------------------------------------------------------------
def soe_enable(doc,soe,value):
   typeNames = doc.getElementsByTagName('TypeName');
   
   for typeName in typeNames:
      if typeName.firstChild.data == soe:
         extension = typeName.parentNode
         for extElement in extension.childNodes:
            if extElement.tagName == 'Enabled':
               if value is True:
                  extElement.firstChild.data = 'true';
               else:
                  extElement.firstChild.data = 'false';
                  
   return doc;
   
def srv_property(doc,property,value):
   keys = doc.getElementsByTagName('Key')
   for key in keys:
      if key.hasChildNodes():
         if key.firstChild.data == property:
            if value is True:
               key.nextSibling.firstChild.data = 'true';
            elif value is False:
               key.nextSibling.firstChild.data = 'false';
            else:
               key.nextSibling.firstChild.data = value
   return doc;

def soe_property(doc,soe,soeProperty,soePropertyValue):
   typeNames = doc.getElementsByTagName('TypeName');
   
   for typeName in typeNames:
       if typeName.firstChild.data == soe:
           extension = typeName.parentNode
           for extElement in extension.childNodes:
               if extElement.tagName in ['Props','Info']:
                   for propArray in extElement.childNodes:
                       for propSet in propArray.childNodes:
                           for prop in propSet.childNodes:
                               if prop.tagName == "Key":
                                   if prop.firstChild.data == soeProperty:
                                       if prop.nextSibling.hasChildNodes():
                                           prop.nextSibling.firstChild.data = soePropertyValue
                                       else:
                                           txt = doc.createTextNode(soePropertyValue)
                                           prop.nextSibling.appendChild(txt)
   return doc;
   

arcpy.AddMessage("Altering sddraft as needed...");       
doc = DOM.parse(sddraft)
for k, v in ags_properties.iteritems():
   doc = srv_property(doc,k,v);
for k, v in ags_services.iteritems():
   doc = soe_enable(doc,k,v);
for k, v in ags_service_props.iteritems():
   doc = soe_property(doc,k,v.keys()[0],v.values()[0]);
f = open(sddraft, 'w');
doc.writexml(f);
f.close();

arcpy.AddMessage("Done.");
arcpy.AddMessage(" ");

#------------------------------------------------------------------------------
#- Step 80
#- Generate sd file and deploy the service
#------------------------------------------------------------------------------ 
arcpy.AddMessage("Generating sd file..."); 
arcpy.StageService_server(sddraft,sd);
arcpy.AddMessage("Done.");
arcpy.AddMessage(" ");
    
arcpy.AddMessage("Deploying to ArcGIS Server..."); 
arcpy.UploadServiceDefinition_server(sd,ags_con);
arcpy.AddMessage("Deployment Complete.");
arcpy.AddMessage(" ");
