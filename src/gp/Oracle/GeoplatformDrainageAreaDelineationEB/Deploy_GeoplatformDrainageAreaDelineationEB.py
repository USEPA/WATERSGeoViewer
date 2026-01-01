import arcpy;
import os,sys;
import xml.dom.minidom as DOM;

#------------------------------------------------------------------------------
# Step 10
# Collect AGS catalog connection
#------------------------------------------------------------------------------
#ags = 'watersgeostage.ags';
ags = 'watersgeo.ags';

#sde = 'ora_rad_ags_stg.sde';
sde = 'ora_rad_ags.sde';

arcpy.AddMessage("Verifying connections...");

projpath = os.path.dirname(os.path.realpath(__file__));
sde_conn = os.path.join(projpath,sde);
ags_conn = os.path.join(projpath,ags);

if not arcpy.Exists(sde_conn):
   arcpy.AddMessage(". SDE Connection " + str(sde_conn) + " not found.");
   exit(-1);

arcpy.AddMessage(". Service will utilize geodatabase connection at: ");
arcpy.AddMessage(".  " + str(sde_conn));

desc = arcpy.Describe(sde_conn);
cp = desc.connectionProperties;
arcpy.AddMessage(". User    : " + cp.user);
arcpy.AddMessage(". Instance: " + cp.instance);

if not os.path.exists(ags_conn):
   print(". AGS connection " + str(ags_conn) + " not found.");
   exit(-1);
   
arcpy.AddMessage(". Service will be deployed to: ");
arcpy.AddMessage(".  " + str(ags_conn));

###############################################################################
#  Set the service parameters                                                 #
#  This section is generally editable                                         #
###############################################################################

draft_service_name        = "GeoplatformDrainageAreaDelineationEB";
draft_folder_name         = "watersgp";
draft_summary             = "The EPA Office of Water Watershed Delineation Service provides an areal representation of the navigation process by linking navigated flowlines to associated areal geographies. The service has been optimized to aggregate and return NHDPlus catchments."
draft_tags                = "EPA";
draft_execution_type      = "ASynchronous";
draft_max_records         = 1000000;
draft_maxUsageTime        = 1200;
draft_maxWaitTime         = 1200;
draft_maxIdleTime         = 1800;
draft_minInstances        = 2;
draft_maxInstances        = 4;

# Hash of any additional general properties to be applied to the sddraft file
ags_properties = {};

# Hash of services to enable or disable
ags_services = {
    'WPSServer': False
};

# Array of Hash of properties to be applied to individual services
ags_service_props = {
    'WPSServer': {'abstract': 'EPA Office of Waters WPS Services'}
};

###############################################################################                                                                            #
# No further changes should be necessary                                      #
###############################################################################

#------------------------------------------------------------------------------
# Step 20
# Import the toolbox
#------------------------------------------------------------------------------
arcpy.AddMessage("Importing the toolbox...");

tb = arcpy.ImportToolbox(
   os.path.join(projpath,'GeoplatformDrainageAreaDelineationEB.pyt')
);

#------------------------------------------------------------------------------
#- Step 30
#- Craft starting point for dry run
#------------------------------------------------------------------------------
sp = os.path.join(arcpy.env.scratchGDB,'Point');
if arcpy.Exists(sp):
   arcpy.Delete_management(sp);
   
arcpy.management.CreateFeatureclass(
    out_path          = os.path.dirname(sp)
   ,out_name          = os.path.basename(sp)
   ,geometry_type     = "POINT"
   ,has_m             = "DISABLED"
   ,has_z             = "DISABLED"
   ,spatial_reference = arcpy.SpatialReference(4269)
   ,out_alias         = "Result Delineated Area"
   ,oid_type          = "32_BIT"
);

with arcpy.da.InsertCursor(
    in_table     = sp
   ,field_names  = [
       'SHAPE@'
    ]
) as icursor:
   
   pt = arcpy.Point(-77.0461,38.9458);
   shape = arcpy.PointGeometry(pt,arcpy.SpatialReference(4269));
   icursor.insertRow((shape));

#------------------------------------------------------------------------------
#- Step 40
#- Dry run service to generate results file
#------------------------------------------------------------------------------
arcpy.AddMessage("Dry run for DelineateUsingStartingPoint...");

resultFC = tb.DelineateUsingStartingPoint(
    StreamSelectionType    = "Upstream with Tributaries"
   ,StartingPoint          = sp
   ,MaxDistanceKm          = "15"
   ,ShowSelectedStreams    = "True"
   ,ShowSelectedCatchments = "True"
   ,AdvancedConfiguration  = ""
);
arcpy.AddMessage(" Success.");

#------------------------------------------------------------------------------
#- Step 50
#- Create the sddraft file
#------------------------------------------------------------------------------
arcpy.AddMessage("Generating sddraft file...");

sddraft = arcpy.CreateScratchName(
    "GeoplatformDrainageAreaDelineationEB"
   ,".sddraft"
   ,None
   ,arcpy.env.scratchFolder
);
arcpy.AddMessage("sddraft: " + str(sddraft));

sd = arcpy.CreateScratchName(
    "GeoplatformDrainageAreaDelineationEB"
   ,".sd"
   ,None
   ,arcpy.env.scratchFolder
);
arcpy.AddMessage("sd: " + str(sd));

gpd = arcpy.sharing.GeoprocessingSharingDraft(
    copyDataToServer         = False
   ,description              = """
The Drainage Area Delineation service is a service that builds upon NHDPlus stream navigation to provide an areal representation of the drainge area by linking navigated flowlines to associated NHDPlus catchments.

Requests for complete upstream watersheds will attempt when possible to return a preaggregated cached watershed polygon. For large delineations such as the Mississippi this is by far the most performant usage of the service. However requesting certain data results such as individual catchments, individual flowlines or flowline lists will require a full navigation which may take a very long time or may not return results for large networks.
    """
   ,draftValue               = [resultFC]
   ,executionType            = draft_execution_type
   ,maxInstances             = draft_maxInstances
   ,maxUsageTime             = draft_maxUsageTime
   ,maxWaitTime              = draft_maxWaitTime
   ,maximumRecords           = draft_max_records
   ,messageLevel             = "Info"
   ,minInstances             = draft_minInstances
   ,offline                  = False
   ,offlineTarget            = 330
   ,overwriteExistingService = True
   ,removeDefaultValues      = [
       'StartingPoint'
      ,'MaxDistanceKm'
      ,'MaxFlowtimeDay'
    ]
   ,resultMapService         = False
   ,serverFolder             = draft_folder_name
   ,serverType               = "ARCGIS_SERVER"
   ,serviceName              = draft_service_name
   ,serviceType              = "GP_SERVICE"
   ,summary                  = draft_summary
   ,tags                     = draft_tags
   ,targetServer             = ags_conn     
);
   
gpd.exportToSDDraft(
   out_sddraft          = sddraft
);

#------------------------------------------------------------------------------
#- Step 60
#- Analyze the SD
#------------------------------------------------------------------------------
arcpy.AddMessage("Analyzing service definition...");
analysis = gpd.analyzeSDDraft();

if analysis["errors"] != []:
   print("---- ERRORS ----");
   vars = analysis["errors"]
   for item in vars:
      print("    ", item[1], ' (CODE %i)' % item[0]);
      if len(item) > 2:
         print("       applies to:");
         for layer in item[2]:
            print(layer.name);
         print(" ");

if analysis["warnings"] != []:
   print("---- WARNINGS ----");
   vars = analysis["warnings"]
   for item in vars:
      print("    ", item[1], ' (CODE %i)' % item[0]);
      if len(item) > 2:
         print("       applies to:");
         for layer in item[2]:
            print(layer.name);
         print(" ");
         
if analysis["messages"] != []:
   print("---- MESSAGES ----");
   vars = analysis["messages"]
   for item in vars:
      print("    ", item[1], ' (CODE %i)' % item[0]);
      if len(item) > 2:
         print("       applies to:");
         for layer in item[2]:
            print(layer.name);
         print(" ");
         
if analysis['errors'] == []:
   arcpy.AddMessage(". No errors found.");
else:
   print(" ");
   print(" Service Errors must be corrected. Exiting.");
   exit(-1);

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
for k, v in ags_properties.items():
   doc = srv_property(doc,k,v);
for k, v in ags_services.items():
   doc = soe_enable(doc,k,v);
for k, v in ags_service_props.items():
   for k2, v2 in v.items():
      doc = soe_property(doc,k,k2,v2);
f = open(sddraft, 'w');
doc.writexml(f);
f.close();

#------------------------------------------------------------------------------
#- Step 80
#- Generate sd file and deploy the service
#------------------------------------------------------------------------------ 
arcpy.AddMessage("Generating sd file..."); 
arcpy.server.StageService(sddraft,sd);
    
arcpy.AddMessage("Deploying to ArcGIS Server..."); 
arcpy.server.UploadServiceDefinition(sd,ags_conn);
arcpy.AddMessage("Deployment Complete.");
arcpy.AddMessage(" ");
