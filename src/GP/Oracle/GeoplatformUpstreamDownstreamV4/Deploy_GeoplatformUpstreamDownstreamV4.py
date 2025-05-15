import arcpy,os,sys;
import builtins;

arcpy.env.overwriteOutput = True;
###############################################################################
g_ags = r"D:\Public\Data\WatersGeoPro\watersgeo\watersgp\ProO_GeoplatformUpstreamDownstreamV4\watersgeo1.ags";
#g_ags = r"D:\Public\Data\WatersGeoPro\watersgeo\watersgp\ProO_GeoplatformUpstreamDownstreamV4\cat1.ags";

###############################################################################
# Step 10
# Validate system
###############################################################################
project_root = os.path.dirname(os.path.realpath(__file__));

print();
py_version = str(sys.version_info[0]) + '.' + str(sys.version_info[1]);
print("Step 10: Using Python version " + str(py_version) + ".");
if float(py_version) < 3:
   raise Exception("Must be using Python 3!");
   
arcpy_install = arcpy.GetInstallInfo();
print("         Using arcpy version " + arcpy_install['Version'] + " with " + arcpy_install['LicenseLevel'] + " license.");

###############################################################################
# Step 20
# Set AGS connection
###############################################################################
if not os.path.isfile(g_ags):
   raise Exception("AGS file not found <" + g_ags + ">");
print("Step 20: Using AGS connection file named " + os.path.basename(g_ags));

###############################################################################
# Step 30
# Add project path to python path and import util forcing project to aprx file
###############################################################################
print("Step 30: Importing project root to path:\n   " + project_root);
sys.path.append(project_root);

###############################################################################
# Step 40
# Short circuit the toolbox and load the util toolbox directly in order to 
# access the parameters.  ArcPy remains a buggy mess and these contortions are
# the only way I can test the tools without just recreating steps from scratch
###############################################################################
toolbx = os.path.join(project_root,"GeoplatformUpstreamDownstreamV4.pyt");
print("Step 40: Sideloading toolbox from \n   " + toolbx);
tb = arcpy.ImportToolbox(toolbx);

###############################################################################
# Step 50
# Set project common variables
###############################################################################
__builtins__.dz_deployer = True;

print("Step 50: Dry run for Search...");
rez = tb.SearchUsingStartingPoint(
    StreamSelectionType      = "Upstream with Tributaries"
   ,AttributeHandling        = "Separated"
   ,ShowSelectedStreams      = False
   ,AdvancedConfiguration    = ""
);

###############################################################################
# Step 60
# Build sddraft file
###############################################################################
print("Step 60: Building sddraft file...");
sd = arcpy.CreateScratchName(
    "GeoplatformUpstreamDownstreamSearchV4"
   ,".sd"
   ,None
   ,arcpy.env.scratchFolder
);
sd = r"D:\Public\Data\WatersGeoPro\watersgeo\watersgp\ProO_GeoplatformUpstreamDownstreamV4\z.sd";
sddraft = arcpy.CreateScratchName(
    "GeoplatformUpstreamDownstreamSearchV4"
   ,".sddraft"
   ,None
   ,arcpy.env.scratchFolder
);
sddraft = r"D:\Public\Data\WatersGeoPro\watersgeo\watersgp\ProO_GeoplatformUpstreamDownstreamV4\z.sddraft";
arcpy.CreateGPSDDraft(
    result               = [rez]
   ,out_sddraft          = sddraft
   ,service_name         = "GeoplatformUpstreamDownstreamSearchV4"
   ,server_type          = "ARCGIS_SERVER"
   ,connection_file_path = g_ags
   ,copy_data_to_server  = False
   ,folder_name          = "watersgp"
   ,summary              = "The Upstream/Downstream Search V4 service is designed to provide standard traversal and linked data discovery functions upon the NHDPlus stream network."
   ,tags                 = "EPA"
   ,executionType        = "ASynchronous"
   ,resultMapServer      = False
   ,showMessages         = "INFO"
   ,maximumRecords       = 1000000
   ,minInstances         = 1
   ,maxInstances         = 2
   ,maxUsageTime         = 1200
   ,maxWaitTime          = 1200
   ,maxIdleTime          = 1800
);

###############################################################################
# Step 80
# Analyze and Upload SD
###############################################################################
print("Step 80: Uploading sd...");
arcpy.StageService_server(sddraft,sd);
   
upStatus = arcpy.UploadServiceDefinition_server(sd,g_ags);
print("-- Upload Deployment Complete --");



