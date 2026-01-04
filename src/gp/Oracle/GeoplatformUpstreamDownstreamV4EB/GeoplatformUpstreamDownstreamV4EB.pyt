import arcpy;
import sys,os,uuid,json;

g_workspace = arcpy.env.scratchGDB;

class Toolbox(object):

   def __init__(self):
   
      self.label = "Geoplatform Upstream Downstream Search V4";
      self.alias = "";

      self.tools = [
          SearchUsingStartingPoint
      ];

class SearchUsingStartingPoint(object):

   def __init__(self):
      
      self.label = "Search Using Starting Point";
      self.name  = "SearchUsingStartingPoint";
      self.description = "The Upstream/Downstream Search V4 service is designed to provide standard traversal and linked data discovery functions upon the NHDPlus stream network.  " + \
         "For more information see " +  \
         "<a href='https://watersgeo.epa.gov/openapi/waters/?sfilter=Discovery' target='_blank'>" + \
         "EPA service documentation</a>.";
      self.canRunInBackground = False;

   def getParameterInfo(self):
      
      flowl_lyrx     = r"D:\Public\Data\pdziemie\github\WATERSGeoViewer\src\gp\Oracle\GeoplatformUpstreamDownstreamV4EB\ResultStreamsSelected.lyrx";
      linkp_lyrx     = r"D:\Public\Data\pdziemie\github\WATERSGeoViewer\src\gp\Oracle\GeoplatformUpstreamDownstreamV4EB\ResultLinkPath.lyrx";
      source_p       = r"D:\Public\Data\pdziemie\github\WATERSGeoViewer\src\gp\Oracle\GeoplatformUpstreamDownstreamV4EB\ResultSourcePointLinkedData.lyrx";
      source_l       = r"D:\Public\Data\pdziemie\github\WATERSGeoViewer\src\gp\Oracle\GeoplatformUpstreamDownstreamV4EB\ResultSourceLinearLinkedData.lyrx";
      source_a       = r"D:\Public\Data\pdziemie\github\WATERSGeoViewer\src\gp\Oracle\GeoplatformUpstreamDownstreamV4EB\ResultSourceAreaLinkedData.lyrx";
      reach_p        = r"D:\Public\Data\pdziemie\github\WATERSGeoViewer\src\gp\Oracle\GeoplatformUpstreamDownstreamV4EB\ResultReachedPointLinkedData.lyrx";
      reach_l        = r"D:\Public\Data\pdziemie\github\WATERSGeoViewer\src\gp\Oracle\GeoplatformUpstreamDownstreamV4EB\ResultReachedLinearLinkedData.lyrx";
      reach_a        = r"D:\Public\Data\pdziemie\github\WATERSGeoViewer\src\gp\Oracle\GeoplatformUpstreamDownstreamV4EB\ResultReachedAreaLinkedData.lyrx";
      
      projpath = os.path.dirname(os.path.realpath(__file__));
      if not arcpy.Exists(flowl_lyrx):
         flowl_lyrx = os.path.join(projpath,'ResultStreamsSelected.lyrx');      
      if not arcpy.Exists(linkp_lyrx):
         linkp_lyrx = os.path.join(projpath,'ResultLinkPath.lyrx');
      if not arcpy.Exists(source_p):
         source_p = os.path.join(projpath,'ResultSourcePointLinkedData.lyrx');
      if not arcpy.Exists(source_l):
         source_l = os.path.join(projpath,'ResultSourceLinearLinkedData.lyrx');
      if not arcpy.Exists(source_a):
         source_a = os.path.join(projpath,'ResultSourceAreaLinkedData.lyrx');
      if not arcpy.Exists(reach_p):
         reach_p = os.path.join(projpath,'ResultReachedPointLinkedData.lyrx');
      if not arcpy.Exists(reach_l):
         reach_l = os.path.join(projpath,'ResultReachedLinearLinkedData.lyrx');
      if not arcpy.Exists(reach_a):
         reach_a = os.path.join(projpath,'ResultReachedAreaLinkedData.lyrx');
      
      param0 = arcpy.Parameter(
          displayName   = "Stream Selection Type"
         ,name          = "StreamSelectionType"
         ,datatype      = "String"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );
      param0.value = "Upstream with Tributaries";
      param0.filter.type = "ValueList";
      param0.filter.list = [
          "Upstream with Tributaries"
         ,"Upstream Main Path Only"
         ,"Downstream with Divergences"
         ,"Downstream Main Path Only"
         ,"Point to Point"
      ];

      param1 = arcpy.Parameter(
          displayName   = "Starting Point"
         ,name          = "StartingPoint"
         ,datatype      = "GPFeatureRecordSetLayer"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );
      param1.filter.list = ['Point'];

      param2 = arcpy.Parameter(
          displayName   = "Max Distance (Km)"
         ,name          = "MaxDistanceKm"
         ,datatype      = "String"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = True
      );
      
      param3 = arcpy.Parameter(
          displayName   = "Max Flowtime (Day)"
         ,name          = "MaxFlowtimeDay"
         ,datatype      = "String"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = True
      );

      param4 = arcpy.Parameter(
          displayName   = "Search For These Linked Data"
         ,name          = "SearchForTheseLinkedData"
         ,datatype      = "String"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,multiValue    = True
         ,enabled       = True
      );
      param4.value       = "Water Quality Portal Monitoring Data";
      param4.filter.type = "ValueList";
      # ATTAINS removed as HR NHDPlus not implemented in Oracle environment
      # "Assessment, Total Maximum Daily Load Tracking and Implementation System (ATTAINS)"
      param4.filter.list = [
          "Clean Watersheds Needs Survey"
         ,"Fish Consumption Advisories"
         ,"Fish Tissue Data"
         ,"Facilities that Discharge to Water"
         ,"Facility Registry Service"
         ,"Water Quality Portal Monitoring Data"
      ];
      
      param5 = arcpy.Parameter(
          displayName   = "Show Selected Streams"
         ,name          = "ShowSelectedStreams"
         ,datatype      = "GPBoolean"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );
      param5.value = True;
      
      param6 = arcpy.Parameter(
          displayName   = "Show Source Data"
         ,name          = "ShowSourceData"
         ,datatype      = "GPBoolean"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );
      param6.value = False;
      
      param7 = arcpy.Parameter(
          displayName   = "Attribute Handling"
         ,name          = "AttributeHandling"
         ,datatype      = "GPString"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );
      param7.value       = "No Attributes";
      param7.filter.type = "ValueList";
      param7.filter.list = [
          "No Attributes"
         ,"Tabular Attributes"
       ];
      
      param8 = arcpy.Parameter(
          displayName   = "NHDPlus Version"
         ,name          = "NHDPlusVersion"
         ,datatype      = "GPString"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );
      param8.value       = "NHDPlus v2.1 Medium Resolution";
      param8.filter.type = "ValueList";
      param8.filter.list = [
          "NHDPlus v2.1 Medium Resolution"
       ];
       
      param9 = arcpy.Parameter(
          displayName   = "Advanced Configuration"
         ,name          = "AdvancedConfiguration"
         ,datatype      = "String"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = True
      );

      param10 = arcpy.Parameter(
          displayName   = "Result Source Point Linked Data"
         ,name          = "ResultSourcePointLinkedData"
         ,datatype      = ["DEFeatureClass","GPString"]
         ,parameterType = "Derived"
         ,direction     = "Output"
      );
      param10.symbology = source_p;
      
      param11 = arcpy.Parameter(
          displayName   = "Result Source Linear Linked Data"
         ,name          = "ResultSourceLinearLinkedData"
         ,datatype      = ["DEFeatureClass","GPString"]
         ,parameterType = "Derived"
         ,direction     = "Output"
      );
      param11.symbology = source_l;

      param12 = arcpy.Parameter(
          displayName   = "Result Source Area Linked Data"
         ,name          = "ResultSourceAreaLinkedData"
         ,datatype      = ["DEFeatureClass","GPString"]
         ,parameterType = "Derived"
         ,direction     = "Output"
      );
      param12.symbology = source_a;
      
      param13 = arcpy.Parameter(
          displayName   = "Result Reached Point Linked Data"
         ,name          = "ResultReachedPointLinkedData"
         ,datatype      = ["DEFeatureClass","GPString"]
         ,parameterType = "Derived"
         ,direction     = "Output"
      );
      param13.symbology = reach_p;
      
      param14 = arcpy.Parameter(
          displayName   = "Result Reached Linear Linked Data"
         ,name          = "ResultReachedLinearLinkedData"
         ,datatype      = ["DEFeatureClass","GPString"]
         ,parameterType = "Derived"
         ,direction     = "Output"
      );
      param14.symbology = reach_l;

      param15 = arcpy.Parameter(
          displayName   = "Result Reached Area Linked Data"
         ,name          = "ResultReachedAreaLinkedData"
         ,datatype      = ["DEFeatureClass","GPString"]
         ,parameterType = "Derived"
         ,direction     = "Output"
      );
      param15.symbology = reach_a;

      param16 = arcpy.Parameter(
          displayName   = "Result Streams Selected"
         ,name          = "ResultStreamsSelected"
         ,datatype      = ["DEFeatureClass","GPString"]
         ,parameterType = "Derived"
         ,direction     = "Output"
      );
      param16.symbology = flowl_lyrx;
      
      param17 = arcpy.Parameter(
          displayName   = "Result FRSPUB Attributes"
         ,name          = "ResultFRSPUBAttributes"
         ,datatype      = ["DETable","GPString"]
         ,parameterType = "Derived"
         ,direction     = "Output"
      );
      
      param18 = arcpy.Parameter(
          displayName   = "Result NPDES Attributes"
         ,name          = "ResultNPDESAttributes"
         ,datatype      = ["DETable","GPString"]
         ,parameterType = "Derived"
         ,direction     = "Output"
      );
      
      param19 = arcpy.Parameter(
          displayName   = "Result WQP Attributes"
         ,name          = "ResultWQPAttributes"
         ,datatype      = ["DETable","GPString"]
         ,parameterType = "Derived"
         ,direction     = "Output"
      );
      
      param20 = arcpy.Parameter(
          displayName   = "Result Link Path"
         ,name          = "ResultLinkPath"
         ,datatype      = ["DEFeatureClass","GPString"]
         ,parameterType = "Derived"
         ,direction     = "Output"
      );
      param20.symbology = linkp_lyrx;
      
      param21 = arcpy.Parameter(
          displayName   = "Status Message"
         ,name          = "StatusMessage"
         ,datatype      = "GPString"
         ,parameterType = "Derived"
         ,direction     = "Output"
      );

      params = [
          param0
         ,param1
         ,param2
         ,param3
         ,param4
         ,param5
         ,param6
         ,param7
         ,param8
         ,param9
         ,param10
         ,param11
         ,param12
         ,param13
         ,param14
         ,param15
         ,param16
         ,param17
         ,param18
         ,param19
         ,param20
         ,param21
      ];

      return params

   def isLicensed(self):
      
      return True;

   def updateParameters(self, parameters):
      
      return True;

   def updateMessages(self, parameters):
      
      return True;

   def execute(self, parameters, messages):
      
      # The Esri geoprocessing publishing process is mysterious and convoluted whereby the receiving server sniffs the code for data sources 
	   # registered to the server data store.  If a match is made the server copies its own .sde file into the unpacked project directory 
	   # updating pointers as it sees fit.  It is VERY easy to confuse the logic.  If you wish to publish this tool to ArcGIS server, 
	   # I’ve found the best approach is to hard-code your .sde file location here.  Providing it unambiguously upfront seems the best way to 
	   # make the publishing process happy.  If just using the tool locally in ArcGIS Pro desktop, one can ignore this pointer.  The code does  
	   # check for the .sde file here first but will fall back the script location if not found.
      
      sde_connection = r"D:\Public\Data\pdziemie\github\WATERSGeoViewer\src\gp\Oracle\GeoplatformUpstreamDownstreamV4EB\ora_rad_ags.sde";
      
      #------------------------------------------------------------------------
      def strip_empty(val):

         if val in [""," "]:
            return None;
         return val;
      
      #------------------------------------------------------------------------
      def get_boo(val):

         if str(val) in ["true","TRUE","Y"]:
            return True;
         else:
            return False;
               
      #------------------------------------------------------------------------
      def search_type(val):

         if val == "Upstream with Tributaries":
            return "UT";
         elif val == "Upstream Main Path Only":
            return "UM";
         elif val == "Downstream with Divergences":
            return "DD";
         elif val == "Downstream Main Path Only":
            return "DM";
         elif val == "Point to Point":
            return "PPALL";
         elif val == "Point to Point All Streams Between":
            return "PPALL";
         elif val == "Upstream with Tributaries No Minor Divergences":
            return "UTNMD";
         elif val == "":
            return None;
         return val;
         
      #------------------------------------------------------------------------
      def to_eventtype(val):

         tmp = val;
         ary_tmp = [];
         
         if tmp == "":
            return ("NULL",ary_tmp);

         elif tmp is not None:
            tmp = tmp.replace('\'','');
            ary_tmp_str = tmp.split(';');

            for item in ary_tmp_str:
               ary_tmp.append(
                  name2eventtype(item)
               );

            tmp = "MDSYS.SDO_STRING2_ARRAY(";
            for item in ary_tmp:
               tmp += "'" + str(item) + "',"

            tmp = tmp[:-1] + ")";

         if tmp is None or tmp == "MDSYS.SDO_STRING2_ARRAY()":
            tmp = "NULL";

         return (tmp,ary_tmp);
         
      #------------------------------------------------------------------------
      def name2eventtype(input):

         if input == "Assessment, Total Maximum Daily Load Tracking and Implementation System (ATTAINS)":
            return 10033;
            
         elif input == "Clean Watersheds Needs Survey":
            return 10006;
            
         elif input == "Fish Consumption Advisories":
            return 10009;
            
         elif input == "Fish Tissue Data":
            return 10010;
            
         elif input == "Facilities that Discharge to Water":
            return 10015;
            
         elif input == "Facility Registry Service":
            return 10028;
            
         elif input == "Water Quality Portal Monitoring Data":
            return 10032;
            
         return input;
   
      #------------------------------------------------------------------------
      #-- Step 10
      #-- Load variables from form parameters
      #------------------------------------------------------------------------
      num_return_code      = 0;
      str_status_message   = "";

      str_search_type        = search_type(parameters[0].valueAsText);
      str_start_point_fc     = strip_empty(parameters[1].valueAsText);
      str_max_distancekm     = strip_empty(parameters[2].value);
      str_max_flowtimeday    = strip_empty(parameters[3].value);
      (str_eventtypelist,ary_eventtypelist) = to_eventtype(parameters[4].valueAsText);
      boo_nav_results        = get_boo(parameters[5].valueAsText);
      boo_show_source        = get_boo(parameters[6].valueAsText);
      str_attribute_handling = strip_empty(parameters[7].valueAsText);
      str_nhdplus_version    = strip_empty(parameters[8].valueAsText);
      str_advanced_config    = strip_empty(parameters[9].valueAsText);
      #arcpy.AddMessage(str(ary_eventtypelist));
      
      #------------------------------------------------------------------------
      #-- Step 20
      #-- Handle the options for max constraints
      #------------------------------------------------------------------------
      if str_max_distancekm is not None and str_max_distancekm.upper() in ["COMPLETE","\"COMPLETE\""]:
         str_max_distancekm  = None;
         str_max_flowtimeday = None;
            
      elif str_max_flowtimeday is not None and str_max_flowtimeday.upper() in ["COMPLETE","\"COMPLETE\""]:
         str_max_distancekm  = None;
         str_max_flowtimeday = None;

      #------------------------------------------------------------------------
      #-- Step 30
      #-- Do error checking
      #------------------------------------------------------------------------
      if str_search_type is None or str_search_type not in ["UT","UM","DD","DM","PP"]:
         num_return_code = -20;
         str_status_message += "Invalid search type. ";

      if str_start_point_fc is None:
         num_return_code = -20;
         str_status_message += "Starting point is required for all search. "

      if str_max_distancekm is not None:
         boo_bad = False;
         try:
            num_val = float(str_max_distancekm);
         except ValueError:
            boo_bad = True;

         if boo_bad or num_val <= 0:
            num_return_code = -10;
            str_status_message += "Maximum distance must be a positive numeric value. ";
      
         str_max_flowtimeday = None;
      
      else:
         if str_max_flowtimeday is not None:
            boo_bad = False;
            
            try:
               num_val = float(str_max_flowtimeday);
            except ValueError:
               boo_bad = True;
               
            if boo_bad or num_val < 0:
               num_return_code = -10;
               str_status_message += "Maximum flow time must be a numeric value of zero or greater. ";
 
      if str_attribute_handling == 'No Attributes':
         boo_attributes = False;
      elif str_attribute_handling == 'Tabular Attributes':
         boo_attributes = True;
      else:
         num_return_code = -11;
         str_status_message += "Unknown attribute handling keyword: "+ str(str_attribute_handling);
               
      #------------------------------------------------------------------------
      #-- Step 40
      #-- Unpack feature class
      #------------------------------------------------------------------------
      str_badgeo_message = """No valid geometry found in Starting Point feature class.""";
      
      try:
         desc           = arcpy.Describe(str_start_point_fc);
         sr             = desc.spatialReference;
         num_start_srid = sr.factoryCode;
         
      except:
         num_return_code = -30;
         str_status_message += str_badgeo_message;
      
      if num_return_code == 0:
         rows = [row for row in arcpy.da.SearchCursor(str_start_point_fc,["SHAPE@"])];
         
         if rows is None or len(rows) == 0:
            num_return_code = -30;
            str_status_message += str_badgeo_message;

         else:
            if rows[-1] is None or len(rows[-1]) == 0:
               num_return_code = -30;
               str_status_message += str_badgeo_message;
               
            else:
               geom = rows[-1][0];
               
               if geom is None:
                  num_return_code = -30;
                  str_status_message += str_badgeo_message;
                  
               else:            
                  if geom.type != "point":
                     geom = arcpy.PointGeometry(geom.trueCentroid);
                     
                  if num_start_srid != 4269:
                     geom = geom.projectAs(arcpy.SpatialReference(4269));

                  obj_esrijson = json.loads(geom.JSON);
                  num_long = obj_esrijson["x"];
                  num_lat  = obj_esrijson["y"];
                  
                  arcpy.AddMessage(". using start location " + str(num_long) + ", " + str(num_lat) + ".");
      
      #------------------------------------------------------------------------
      #-- Step 50
      #-- Determine reasonable navigation engine choice
      #------------------------------------------------------------------------
      if str_search_type in ('UM','DM','PP'):
         str_navigation_engine = 'V2';
      elif str_search_type == 'DD':
         str_navigation_engine = 'V1';
      elif str_search_type == 'UT'        \
      and str_max_distancekm is not None  \
      and float(str_max_distancekm) < 200:
         str_navigation_engine = 'V2';
      elif str_search_type == 'UT'        \
      and str_max_flowtimeday is not None \
      and float(str_max_flowtimeday) < 50:
         str_navigation_engine = 'V2';
      else:
         str_navigation_engine = 'V1';
       
      #------------------------------------------------------------------------
      #-- Step 60
      #-- Create the service scratch space
      #------------------------------------------------------------------------
      if num_return_code == 0:
         
         #------------------------------------------------------------------------
         if boo_show_source:
            if 10006 in ary_eventtypelist \
            or 10009 in ary_eventtypelist \
            or 10010 in ary_eventtypelist :        
            
               scratch_full_source_a = arcpy.CreateUniqueName(
                   base_name  = "ResultSourceAreaLinkedData"
                  ,workspace  = g_workspace
               );
               arcpy.management.CreateFeatureclass(
                   out_path          = os.path.dirname(scratch_full_source_a)
                  ,out_name          = os.path.basename(scratch_full_source_a)
                  ,geometry_type     = "POLYGON"
                  ,has_m             = "DISABLED"
                  ,has_z             = "DISABLED"
                  ,spatial_reference = arcpy.SpatialReference(3857)
                  ,out_alias         = "Result Source Area Linked Data"
                  ,oid_type          = "32_BIT"
               );
               arcpy.management.AddFields(
                   in_table          = scratch_full_source_a
                  ,field_description = [
                      ['eventtype'                  ,'LONG'  ,'Event Type Program Code'       ,None,None,None]
                     ,['program_name'               ,'TEXT'  ,'Program Name'                  ,255 ,None,None]
                     ,['permid_joinkey'             ,'TEXT'  ,'Permanent Identifier JoinKey'  ,40  ,None,None]
                     ,['source_originator'          ,'TEXT'  ,'Source Originator'             ,130 ,None,None]
                     ,['source_featureid'           ,'TEXT'  ,'Source Feature ID'             ,100 ,None,None]
                     ,['source_featureid2'          ,'TEXT'  ,'Source Feature ID 2'           ,100 ,None,None]
                     ,['source_series'              ,'TEXT'  ,'Source Series'                 ,100 ,None,None]
                     ,['source_subdivision'         ,'TEXT'  ,'Source Subdivision'            ,100 ,None,None]
                     ,['source_joinkey'             ,'TEXT'  ,'Source JoinKey'                ,40  ,None,None]
                     ,['start_date'                 ,'DATE'  ,'Start Date'                    ,None,None,None]
                     ,['end_date'                   ,'DATE'  ,'End Date'                      ,None,None,None]
                     ,['featuredetailurl'           ,'TEXT'  ,'Feature Detail URL'            ,255 ,None,None]
                     ,['areasqkm'                   ,'DOUBLE','Area (SqKm)'                   ,None,None,None]
                     ,['nearest_network_distancekm' ,'DOUBLE','Nearest Network Distance (Km)' ,None,None,None]
                     ,['nearest_network_flowtimeday','DOUBLE','Nearest Network Flowtime (Day)',None,None,None]
                   ]
               );

         #------------------------------------------------------------------------
         if boo_show_source:
            if 10006 in ary_eventtypelist \
            or 10009 in ary_eventtypelist \
            or 10010 in ary_eventtypelist : 
               
               scratch_full_source_l = arcpy.CreateUniqueName(
                   base_name  = "ResultSourceLinearLinkedData"
                  ,workspace  = g_workspace
               );
               arcpy.management.CreateFeatureclass(
                   out_path          = os.path.dirname(scratch_full_source_l)
                  ,out_name          = os.path.basename(scratch_full_source_l)
                  ,geometry_type     = "POLYLINE"
                  ,has_m             = "DISABLED"
                  ,has_z             = "DISABLED"
                  ,spatial_reference = arcpy.SpatialReference(3857)
                  ,out_alias         = "Result Source Linear Linked Data"
                  ,oid_type          = "32_BIT"
               );
               arcpy.management.AddFields(
                   in_table          = scratch_full_source_l
                  ,field_description = [
                      ['eventtype'                  ,'LONG'  ,'Event Type Program Code'       ,None,None,None]
                     ,['program_name'               ,'TEXT'  ,'Program Name'                  ,255 ,None,None]
                     ,['permid_joinkey'             ,'TEXT'  ,'Permanent Identifier JoinKey'  ,40  ,None,None]
                     ,['source_originator'          ,'TEXT'  ,'Source Originator'             ,130 ,None,None]
                     ,['source_featureid'           ,'TEXT'  ,'Source Feature ID'             ,100 ,None,None]
                     ,['source_featureid2'          ,'TEXT'  ,'Source Feature ID 2'           ,100 ,None,None]
                     ,['source_series'              ,'TEXT'  ,'Source Series'                 ,100 ,None,None]
                     ,['source_subdivision'         ,'TEXT'  ,'Source Subdivision'            ,100 ,None,None]
                     ,['source_joinkey'             ,'TEXT'  ,'Source JoinKey'                ,40  ,None,None]
                     ,['start_date'                 ,'DATE'  ,'Start Date'                    ,None,None,None]
                     ,['end_date'                   ,'DATE'  ,'End Date'                      ,None,None,None]
                     ,['featuredetailurl'           ,'TEXT'  ,'Feature Detail URL'            ,255 ,None,None]
                     ,['lengthkm'                   ,'DOUBLE','Length (Km)'                   ,None,None,None]
                     ,['nearest_network_distancekm' ,'DOUBLE','Nearest Network Distance (Km)' ,None,None,None]
                     ,['nearest_network_flowtimeday','DOUBLE','Nearest Network Flowtime (Day)',None,None,None]
                   ]
               );

         #------------------------------------------------------------------------
         if boo_show_source:
            scratch_full_source_p = arcpy.CreateUniqueName(
                base_name  = "ResultSourcePointLinkedData"
               ,workspace  = g_workspace
            );
            arcpy.management.CreateFeatureclass(
                out_path          = os.path.dirname(scratch_full_source_p)
               ,out_name          = os.path.basename(scratch_full_source_p)
               ,geometry_type     = "POINT"
               ,has_m             = "DISABLED"
               ,has_z             = "DISABLED"
               ,spatial_reference = arcpy.SpatialReference(3857)
               ,out_alias         = "Result Source Point Linked Data"
               ,oid_type          = "32_BIT"
            );
            arcpy.management.AddFields(
                in_table          = scratch_full_source_p
               ,field_description = [
                   ['eventtype'                  ,'LONG'  ,'Event Type Program Code'       ,None,None,None]
                  ,['program_name'               ,'TEXT'  ,'Program Name'                  ,255 ,None,None]
                  ,['permid_joinkey'             ,'TEXT'  ,'Permanent Identifier JoinKey'  ,40  ,None,None]
                  ,['source_originator'          ,'TEXT'  ,'Source Originator'             ,130 ,None,None]
                  ,['source_featureid'           ,'TEXT'  ,'Source Feature ID'             ,100 ,None,None]
                  ,['source_featureid2'          ,'TEXT'  ,'Source Feature ID 2'           ,100 ,None,None]
                  ,['source_series'              ,'TEXT'  ,'Source Series'                 ,100 ,None,None]
                  ,['source_subdivision'         ,'TEXT'  ,'Source Subdivision'            ,100 ,None,None]
                  ,['source_joinkey'             ,'TEXT'  ,'Source JoinKey'                ,40  ,None,None]
                  ,['start_date'                 ,'DATE'  ,'Start Date'                    ,None,None,None]
                  ,['end_date'                   ,'DATE'  ,'End Date'                      ,None,None,None]
                  ,['featuredetailurl'           ,'TEXT'  ,'Feature Detail URL'            ,255 ,None,None]
                  ,['nearest_network_distancekm' ,'DOUBLE','Nearest Network Distance (Km)' ,None,None,None]
                  ,['nearest_network_flowtimeday','DOUBLE','Nearest Network Flowtime (Day)',None,None,None]
                ]
            );
         
         #------------------------------------------------------------------------
         if 10006 in ary_eventtypelist \
         or 10009 in ary_eventtypelist \
         or 10010 in ary_eventtypelist : 
         
            scratch_full_reached_a = arcpy.CreateUniqueName(
                base_name  = "ResultReachedAreaLinkedData"
               ,workspace  = g_workspace
            );
            arcpy.management.CreateFeatureclass(
                out_path          = os.path.dirname(scratch_full_reached_a)
               ,out_name          = os.path.basename(scratch_full_reached_a)
               ,geometry_type     = "POLYGON"
               ,has_m             = "DISABLED"
               ,has_z             = "DISABLED"
               ,spatial_reference = arcpy.SpatialReference(3857)
               ,out_alias         = "Result Reached Area Linked Data"
               ,oid_type          = "32_BIT"
            );
            arcpy.management.AddFields(
                in_table          = scratch_full_reached_a
               ,field_description = [
                   ['eventtype'                   ,'LONG'  ,'Event Type Program Code'       ,None,None,None]
                  ,['program_name'                ,'TEXT'  ,'Program Name'                  ,255 ,None,None]
                  ,['permanent_identifier'        ,'TEXT'  ,'Permanent Identifier'          ,40  ,None,None]
                  ,['permid_joinkey'              ,'TEXT'  ,'Permanent Identifier JoinKey'  ,40  ,None,None]
                  ,['eventdate'                   ,'DATE'  ,'Event Date'                    ,None,None,None]
                  ,['reachcode'                   ,'TEXT'  ,'Reach Code'                    ,14  ,None,None]
                  ,['reachsmdate'                 ,'DATE'  ,'Reach SMDate'                  ,None,None,None]
                  ,['reachresolution'             ,'LONG'  ,'Reach Resolution'              ,None,None,None]
                  ,['feature_permanent_identifier','TEXT'  ,'Feature Permanent Identifier'  ,40  ,None,None]
                  ,['featureclassref'             ,'LONG'  ,'Feature Class Reference'       ,None,None,None]
                  ,['source_originator'           ,'TEXT'  ,'Source Originator'             ,130 ,None,None]
                  ,['source_featureid'            ,'TEXT'  ,'Source Feature ID'             ,100 ,None,None]
                  ,['source_featureid2'           ,'TEXT'  ,'Source Feature ID 2'           ,100 ,None,None]
                  ,['source_datadesc'             ,'TEXT'  ,'Source Data Description'       ,100 ,None,None]
                  ,['source_series'               ,'TEXT'  ,'Source Series'                 ,100 ,None,None]
                  ,['source_subdivision'          ,'TEXT'  ,'Source Subdivision'            ,100 ,None,None]
                  ,['source_joinkey'              ,'TEXT'  ,'Source JoinKey'                ,40  ,None,None]
                  ,['start_date'                  ,'DATE'  ,'Start Date'                    ,None,None,None]
                  ,['end_date'                    ,'DATE'  ,'End Date'                      ,None,None,None]
                  ,['featuredetailurl'            ,'TEXT'  ,'Feature Detail URL'            ,255 ,None,None]
                  ,['event_areasqkm'              ,'DOUBLE','Event Area (SqKm)'             ,None,None,None]
                  ,['geogstate'                   ,'TEXT'  ,'Event Geographic State'        ,2   ,None,None]
                  ,['network_distancekm'          ,'DOUBLE','Network Distance (Km)'         ,None,None,None]
                  ,['network_flowtimeday'         ,'DOUBLE','Network Flowtime (Day)'        ,None,None,None]
                ]
            );

         #------------------------------------------------------------------------
         if 10006 in ary_eventtypelist \
         or 10009 in ary_eventtypelist \
         or 10010 in ary_eventtypelist : 
            
            scratch_full_reached_l = arcpy.CreateUniqueName(
                base_name  = "ResultReachedLinearLinkedData"
               ,workspace  = g_workspace
            );
            arcpy.management.CreateFeatureclass(
                out_path          = os.path.dirname(scratch_full_reached_l)
               ,out_name          = os.path.basename(scratch_full_reached_l)
               ,geometry_type     = "POLYLINE"
               ,has_m             = "DISABLED"
               ,has_z             = "DISABLED"
               ,spatial_reference = arcpy.SpatialReference(3857)
               ,out_alias         = "Result Reached Linear Linked Data"
               ,oid_type          = "32_BIT"
            );
            arcpy.management.AddFields(
                in_table          = scratch_full_reached_l
               ,field_description = [
                   ['eventtype'                   ,'LONG'  ,'Event Type Program Code'       ,None,None,None]
                  ,['program_name'                ,'TEXT'  ,'Program Name'                  ,255 ,None,None]
                  ,['permanent_identifier'        ,'TEXT'  ,'Permanent Identifier'          ,40  ,None,None]
                  ,['permid_joinkey'              ,'TEXT'  ,'Permanent Identifier JoinKey'  ,40  ,None,None]
                  ,['eventdate'                   ,'DATE'  ,'Event Date'                    ,None,None,None]
                  ,['reachcode'                   ,'TEXT'  ,'Reach Code'                    ,14  ,None,None]
                  ,['reachsmdate'                 ,'DATE'  ,'Reach SMDate'                  ,None,None,None]
                  ,['reachresolution'             ,'LONG'  ,'Reach Resolution'              ,None,None,None]
                  ,['feature_permanent_identifier','TEXT'  ,'Feature Permanent Identifier'  ,40  ,None,None]
                  ,['featureclassref'             ,'LONG'  ,'Feature Class Reference'       ,None,None,None]
                  ,['source_originator'           ,'TEXT'  ,'Source Originator'             ,130 ,None,None]
                  ,['source_featureid'            ,'TEXT'  ,'Source Feature ID'             ,100 ,None,None]
                  ,['source_featureid2'           ,'TEXT'  ,'Source Feature ID 2'           ,100 ,None,None]
                  ,['source_datadesc'             ,'TEXT'  ,'Source Data Description'       ,100 ,None,None]
                  ,['source_series'               ,'TEXT'  ,'Source Series'                 ,100 ,None,None]
                  ,['source_subdivision'          ,'TEXT'  ,'Source Subdivision'            ,100 ,None,None]
                  ,['source_joinkey'              ,'TEXT'  ,'Source JoinKey'                ,40  ,None,None]
                  ,['start_date'                  ,'DATE'  ,'Start Date'                    ,None,None,None]
                  ,['end_date'                    ,'DATE'  ,'End Date'                      ,None,None,None]
                  ,['featuredetailurl'            ,'TEXT'  ,'Feature Detail URL'            ,255 ,None,None]
                  ,['fmeasure'                    ,'DOUBLE','From Measure'                  ,None,None,None]
                  ,['tmeasure'                    ,'DOUBLE','To Measure'                    ,None,None,None]
                  ,['eventoffset'                 ,'DOUBLE','Event Offset'                  ,None,None,None]
                  ,['event_lengthkm'              ,'DOUBLE','Event Length (Km)'             ,None,None,None]
                  ,['geogstate'                   ,'TEXT'  ,'Event Geographic State'        ,2   ,None,None]
                  ,['network_distancekm'          ,'DOUBLE','Network Distance (Km)'         ,None,None,None]
                  ,['network_flowtimeday'         ,'DOUBLE','Network Flowtime (Day)'        ,None,None,None]
                ]
            );

         #------------------------------------------------------------------------
         scratch_full_reached_p = arcpy.CreateUniqueName(
             base_name  = "ResultReachedPointLinkedData"
            ,workspace  = g_workspace
         );
         arcpy.management.CreateFeatureclass(
             out_path          = os.path.dirname(scratch_full_reached_p)
            ,out_name          = os.path.basename(scratch_full_reached_p)
            ,geometry_type     = "POINT"
            ,has_m             = "DISABLED"
            ,has_z             = "DISABLED"
            ,spatial_reference = arcpy.SpatialReference(3857)
            ,out_alias         = "Result Reached Point Linked Data"
            ,oid_type          = "32_BIT"
         );
         arcpy.management.AddFields(
             in_table          = scratch_full_reached_p
            ,field_description = [
                ['eventtype'                   ,'LONG'  ,'Event Type Program Code'       ,None,None,None]
               ,['program_name'                ,'TEXT'  ,'Program Name'                  ,255 ,None,None]
               ,['permanent_identifier'        ,'TEXT'  ,'Permanent Identifier'          ,40  ,None,None]
               ,['permid_joinkey'              ,'TEXT'  ,'Permanent Identifier JoinKey'  ,40  ,None,None]
               ,['eventdate'                   ,'DATE'  ,'Event Date'                    ,None,None,None]
               ,['reachcode'                   ,'TEXT'  ,'Reach Code'                    ,14  ,None,None]
               ,['reachsmdate'                 ,'DATE'  ,'Reach SMDate'                  ,None,None,None]
               ,['reachresolution'             ,'LONG'  ,'Reach Resolution'              ,None,None,None]
               ,['feature_permanent_identifier','TEXT'  ,'Feature Permanent Identifier'  ,40  ,None,None]
               ,['featureclassref'             ,'LONG'  ,'Feature Class Reference'       ,None,None,None]
               ,['source_originator'           ,'TEXT'  ,'Source Originator'             ,130 ,None,None]
               ,['source_featureid'            ,'TEXT'  ,'Source Feature ID'             ,100 ,None,None]
               ,['source_featureid2'           ,'TEXT'  ,'Source Feature ID 2'           ,100 ,None,None]
               ,['source_datadesc'             ,'TEXT'  ,'Source Data Description'       ,100 ,None,None]
               ,['source_series'               ,'TEXT'  ,'Source Series'                 ,100 ,None,None]
               ,['source_subdivision'          ,'TEXT'  ,'Source Subdivision'            ,100 ,None,None]
               ,['source_joinkey'              ,'TEXT'  ,'Source JoinKey'                ,40  ,None,None]
               ,['start_date'                  ,'DATE'  ,'Start Date'                    ,None,None,None]
               ,['end_date'                    ,'DATE'  ,'End Date'                      ,None,None,None]
               ,['featuredetailurl'            ,'TEXT'  ,'Feature Detail URL'            ,255 ,None,None]
               ,['measure'                     ,'DOUBLE','Measure'                       ,None,None,None]
               ,['eventoffset'                 ,'DOUBLE','Event Offset'                  ,None,None,None]
               ,['geogstate'                   ,'TEXT'  ,'Event Geographic State'        ,2   ,None,None]
               ,['network_distancekm'          ,'DOUBLE','Network Distance (Km)'         ,None,None,None]
               ,['network_flowtimeday'         ,'DOUBLE','Network Flowtime (Day)'        ,None,None,None]
             ]
         );

         #------------------------------------------------------------------------
         if boo_nav_results:
            
            scratch_full_fl = arcpy.CreateUniqueName(
                base_name  = "ResultStreamsSelected"
               ,workspace  = g_workspace
            );
            arcpy.management.CreateFeatureclass(
                out_path          = os.path.dirname(scratch_full_fl)
               ,out_name          = os.path.basename(scratch_full_fl)
               ,geometry_type     = "POLYLINE"
               ,has_m             = "DISABLED"
               ,has_z             = "DISABLED"
               ,spatial_reference = arcpy.SpatialReference(3857)
               ,out_alias         = "Result Streams Selected"
               ,oid_type          = "32_BIT"
            );
            arcpy.management.AddFields(
                in_table          = scratch_full_fl
               ,field_description = [
                   ['nhdplusid'           ,'DOUBLE','NHDPlusID'                  ,None,None,None]
                  ,['hydroseq'            ,'DOUBLE','HydroSeq'                   ,None,None,None]
                  ,['fmeasure'            ,'DOUBLE','From Measure'               ,None,None,None]
                  ,['tmeasure'            ,'DOUBLE','From Measure'               ,None,None,None]
                  ,['lengthkm'            ,'DOUBLE','Length (Km)'                ,None,None,None]
                  ,['flowtimeday'         ,'DOUBLE','Flowtime (Day)'             ,None,None,None]
                  ,['network_distancekm'  ,'DOUBLE','Network Distance (Km)'      ,None,None,None]
                  ,['network_flowtimeday' ,'DOUBLE','Network Flowtime (Day)'     ,None,None,None]
                  ,['levelpathi'          ,'DOUBLE','Level Path ID'              ,None,None,None]
                  ,['terminalpa'          ,'DOUBLE','Terminal Path ID'           ,None,None,None]
                  ,['uphydroseq'          ,'DOUBLE','Upstream HydroSeq'          ,None,None,None]
                  ,['dnhydroseq'          ,'DOUBLE','Downstream HydroSeq'        ,None,None,None]
                  ,['dnminorhyd'          ,'DOUBLE','Downstream Minor HydroSeq'  ,None,None,None]
                  ,['arbolatesu'          ,'DOUBLE','Arbolate Sum'               ,None,None,None]
                  ,['navtermination_flag' ,'LONG'  ,'Navigation Termination Flag',None,None,None]
                  ,['nav_order'           ,'LONG'  ,'Navigation Ordering Key'    ,None,None,None]
                ]
            );
            
         #------------------------------------------------------------------------
         if boo_attributes and 10028 in ary_eventtypelist:
            
            scratch_frspub_attr = arcpy.CreateUniqueName(
                base_name  = "ResultFRSPUBAttributes"
               ,workspace = g_workspace
            );
            arcpy.management.CreateTable(
                out_path          = os.path.dirname(scratch_frspub_attr)
               ,out_name          = os.path.basename(scratch_frspub_attr)
               ,out_alias         = "Result FRSPUB Attributes"
               ,oid_type          = "32_BIT"
            );
            arcpy.management.AddFields(
                in_table          = scratch_frspub_attr
               ,field_description = [
                   ['source_joinkey'                ,'TEXT'  ,'Source JoinKey'                          ,40  ,None,None]
                  ,['registry_id'                   ,'TEXT'  ,'Registry ID'                             ,50  ,None,None]
                  ,['primary_name'                  ,'TEXT'  ,'Primary Name'                            ,240 ,None,None]
                  ,['city_name'                     ,'TEXT'  ,'City Name'                               ,180 ,None,None]
                  ,['county_name'                   ,'TEXT'  ,'County Name'                             ,105 ,None,None]
                  ,['fips_code'                     ,'TEXT'  ,'FIPS Code'                               ,15  ,None,None]
                  ,['state_code'                    ,'TEXT'  ,'State Code'                              ,15  ,None,None]
                  ,['state_name'                    ,'TEXT'  ,'State Name'                              ,105 ,None,None]
                  ,['country_name'                  ,'TEXT'  ,'Country Name'                            ,132 ,None,None]
                  ,['postal_code'                   ,'TEXT'  ,'Postal Code'                             ,42  ,None,None]
                  ,['tribal_land_code'              ,'TEXT'  ,'Tribal Land Code'                        ,3   ,None,None]
                  ,['tribal_land_name'              ,'TEXT'  ,'Tribal Land Name'                        ,600 ,None,None]
                  ,['us_mexico_border_ind'          ,'TEXT'  ,'US/Mexico Border Indicator'              ,1   ,None,None]
                  ,['pgm_sys_id'                    ,'TEXT'  ,'Program System Identifier'               ,30  ,None,None]
                  ,['pgm_sys_acrnm'                 ,'TEXT'  ,'Program System Acronym'                  ,15  ,None,None]
                  ,['nearest_cip_network_distancekm','DOUBLE','Nearest CIP Network Distance (Km)'       ,None,None,None]
                  ,['nearest_cip_network_flowtimeda','DOUBLE','Nearest CIP Network Flowtime (Day)'      ,None,None,None]
                  ,['nearest_rad_network_distancekm','DOUBLE','Nearest RAD Network Distance (Km)'       ,None,None,None]
                  ,['nearest_rad_network_flowtimeda','DOUBLE','Nearest CIP Network Flowtime (Day)'      ,None,None,None]
                ]
            );
         
         #------------------------------------------------------------------------
         if boo_attributes and 10015 in ary_eventtypelist:
            
            scratch_npdes_attr = arcpy.CreateUniqueName(
                base_name  = "ResultNPDESAttributes"
               ,workspace = g_workspace
            );
            arcpy.management.CreateTable(
                out_path          = os.path.dirname(scratch_npdes_attr)
               ,out_name          = os.path.basename(scratch_npdes_attr)
               ,out_alias         = "Result NPDES Attributes"
               ,oid_type          = "32_BIT"
            );
            arcpy.management.AddFields(
                in_table          = scratch_npdes_attr
               ,field_description = [
                   ['source_joinkey'                ,'TEXT'  ,'Source JoinKey'                          ,40  ,None,None]
                  ,['external_permit_nmbr'          ,'TEXT'  ,'External Permit Number'                  ,9   ,None,None]
                  ,['permit_name'                   ,'TEXT'  ,'Permit Name'                             ,120 ,None,None]
                  ,['registry_id'                   ,'TEXT'  ,'Registry ID'                             ,12  ,None,None]
                  ,['primary_name'                  ,'TEXT'  ,'Primary Name'                            ,150 ,None,None]
                  ,['state_code'                    ,'TEXT'  ,'State Code'                              ,5   ,None,None]
                  ,['agency_type_code'              ,'TEXT'  ,'Agency Type Code'                        ,3   ,None,None]
                  ,['issue_date'                    ,'DATE'  ,'Issue Date'                              ,None,None,None]
                  ,['issuing_agency'                ,'TEXT'  ,'Issuing Agency'                          ,100 ,None,None]
                  ,['original_issue_date'           ,'DATE'  ,'Original Issue Date'                     ,None,None,None]
                  ,['permit_status_code'            ,'TEXT'  ,'Permit Status Code'                      ,3   ,None,None]
                  ,['permit_type_code'              ,'TEXT'  ,'Permit Type Code'                        ,3   ,None,None]
                  ,['retirement_date'               ,'DATE'  ,'Retirement Date'                         ,None,None,None]
                  ,['termination_date'              ,'DATE'  ,'Termination Date'                        ,None,None,None]
                  ,['nearest_cip_network_distancekm','DOUBLE','Nearest CIP Network Distance (Km)'       ,None,None,None]
                  ,['nearest_cip_network_flowtimeda','DOUBLE','Nearest CIP Network Flowtime (Day)'      ,None,None,None]
                  ,['nearest_rad_network_distancekm','DOUBLE','Nearest RAD Network Distance (Km)'       ,None,None,None]
                  ,['nearest_rad_network_flowtimeda','DOUBLE','Nearest CIP Network Flowtime (Day)'      ,None,None,None]
                ]
            );
            
         #------------------------------------------------------------------------
         if boo_attributes and 10032 in ary_eventtypelist:
            
            scratch_wqp_attr = arcpy.CreateUniqueName(
                base_name  = "ResultWQPAttributes"
               ,workspace = g_workspace
            );
            arcpy.management.CreateTable(
                out_path          = os.path.dirname(scratch_wqp_attr)
               ,out_name          = os.path.basename(scratch_wqp_attr)
               ,out_alias         = "Result WQP Attributes"
               ,oid_type          = "32_BIT"
            );
            arcpy.management.AddFields(
                in_table          = scratch_wqp_attr
               ,field_description = [
                   ['source_joinkey'                ,'TEXT'  ,'Source JoinKey'                          ,40  ,None,None]
                  ,['organizationidentifier'        ,'TEXT'  ,'Organization Identifier'                 ,256 ,None,None]
                  ,['organizationformalname'        ,'TEXT'  ,'Organization Formal Name'                ,256 ,None,None]
                  ,['monitoringlocationidentifier'  ,'TEXT'  ,'Monitoring Location Identifier'          ,256 ,None,None]
                  ,['monitoringlocationname'        ,'TEXT'  ,'Monitoring Location Name'                ,768 ,None,None]
                  ,['monitoringlocationtypename'    ,'TEXT'  ,'Monitoring Location Type Name'           ,256 ,None,None]
                  ,['monitoringlocationdescription' ,'TEXT'  ,'Monitoring Location Description'         ,4000,None,None]
                  ,['huceightdigitcode'             ,'TEXT'  ,'HUC Eight Digit Code'                    ,8   ,None,None]
                  ,['drainageareameasure_measureval','DOUBLE','Drainage Area Measure Value'             ,None,None,None]
                  ,['drainageareameasure_measureunt','TEXT'  ,'Drainage Area Measure Unit'              ,16  ,None,None]
                  ,['contributingdrainageareameasva','DOUBLE','Contributing Drainage Area Measure Value',None,None,None]
                  ,['contributingdrainageareameasun','TEXT'  ,'Contributing Drainage Area Measure Unit' ,16  ,None,None]
                  ,['latitudemeasure'               ,'DOUBLE','Latitude'                                ,None,None,None]
                  ,['longitudemeasure'              ,'DOUBLE','Longitude'                               ,None,None,None]
                  ,['sourcemapscalenumeric'         ,'DOUBLE','Source Map Scale Numeric'                ,None,None,None]
                  ,['horizontalaccuracymeasureval'  ,'TEXT'  ,'Horizontal Accuracy Measure Value'       ,64  ,None,None]
                  ,['horizontalaccuracymeasureunit' ,'TEXT'  ,'Horizontal Accuracy Measure Unit'        ,16  ,None,None]
                  ,['horizontalcollectionmethodname','TEXT'  ,'Horizontal Collection Method Name'       ,2000,None,None]
                  ,['horizontalcoordinatereferences','TEXT'  ,'Horizontal Coordinate References'        ,16  ,None,None]
                  ,['verticalmeasure_measurevalue'  ,'TEXT'  ,'Vertical Measure Value'                  ,64  ,None,None]
                  ,['verticalmeasure_measureunit'   ,'TEXT'  ,'Vertical Measure Unit'                   ,16  ,None,None]
                  ,['verticalaccuracymeasurevalue'  ,'TEXT'  ,'Vertical Accuracy Measure Value'         ,64  ,None,None]
                  ,['verticalaccuracymeasureunit'   ,'TEXT'  ,'Vertical Accuracy Measure Unit'          ,16  ,None,None]
                  ,['verticalcollectionmethodname'  ,'TEXT'  ,'Vertical Collection Method Name'         ,2000,None,None]
                  ,['verticalcoordinatereferencesys','TEXT'  ,'Vertical Coordinate Reference System'    ,16  ,None,None]
                  ,['countrycode'                   ,'TEXT'  ,'Country Code'                            ,2   ,None,None]
                  ,['statecode'                     ,'TEXT'  ,'State Code'                              ,2   ,None,None]
                  ,['countycode'                    ,'TEXT'  ,'County Code'                             ,3   ,None,None]
                  ,['aquifername'                   ,'TEXT'  ,'Aquifer Name'                            ,2000,None,None]
                  ,['formationtypetext'             ,'TEXT'  ,'Formation Type Text'                     ,2000,None,None]
                  ,['aquifertypename'               ,'TEXT'  ,'Aquifer Type Name'                       ,2000,None,None]
                  ,['constructiondatetext'          ,'TEXT'  ,'Construction Date'                       ,16  ,None,None]
                  ,['welldepthmeasure_measurevalue' ,'DOUBLE','Well Depth Measure Value'                ,None,None,None]
                  ,['welldepthmeasure_measureunit'  ,'TEXT'  ,'Well Depth Measure Unit'                 ,16  ,None,None]
                  ,['wellholedepthmeasure_measureva','DOUBLE','Well Hole Depth Measure Value'           ,None,None,None]
                  ,['wellholedepthmeasure_measureun','TEXT'  ,'Well Hole Depth Measure Unit'            ,16  ,None,None]
                  ,['providername'                  ,'TEXT'  ,'Provider Name'                           ,16  ,None,None]
                  ,['nearest_cip_network_distancekm','DOUBLE','Nearest CIP Network Distance (Km)'       ,None,None,None]
                  ,['nearest_cip_network_flowtimeda','DOUBLE','Nearest CIP Network Flowtime (Day)'      ,None,None,None]
                  ,['nearest_rad_network_distancekm','DOUBLE','Nearest RAD Network Distance (Km)'       ,None,None,None]
                  ,['nearest_rad_network_flowtimeda','DOUBLE','Nearest CIP Network Flowtime (Day)'      ,None,None,None]
                ]
            );
            
         #------------------------------------------------------------------------
         scratch_full_link = arcpy.CreateUniqueName(
             base_name  = "ResultLinkPath"
            ,workspace  = g_workspace
         );
         arcpy.management.CreateFeatureclass(
             out_path          = os.path.dirname(scratch_full_link)
            ,out_name          = os.path.basename(scratch_full_link)
            ,geometry_type     = "POLYLINE"
            ,has_m             = "DISABLED"
            ,has_z             = "DISABLED"
            ,spatial_reference = arcpy.SpatialReference(3857)
            ,out_alias         = "Result Link Path"
            ,oid_type          = "32_BIT"
         );
         arcpy.management.AddFields(
             in_table          = scratch_full_link
            ,field_description = [
                ['nhdplusid'           ,'DOUBLE','NHDPlusID'                  ,None,None,None]
               ,['measure'             ,'DOUBLE','Measure'                    ,None,None,None]
             ]
         );

      #------------------------------------------------------------------------
      #-- Step 70
      #-- Create the database connection
      #------------------------------------------------------------------------
      if num_return_code == 0:
         
         try:
            sde_conn_path = sde_connection;
            sde_conn = arcpy.ArcSDESQLExecute(sde_conn_path);

         except:         
            arcpy.AddMessage(". Failed to connect to " + str(sde_conn_path) + ".");
            
            try:
               z = os.path.dirname(os.path.realpath(__file__));
               sde_conn_path = os.path.join(z,os.path.basename(sde_connection));
               sde_conn = arcpy.ArcSDESQLExecute(sde_conn_path);

            except:
               try:
                  z = arcpy.env.packageWorkspace;
                  sde_conn_path = os.path.join(z,os.path.basename(sde_connection));
                  sde_conn = arcpy.ArcSDESQLExecute(sde_conn_path);
                  
               except Exception as err:
                  arcpy.AddError(err);
                  raise;

      #------------------------------------------------------------------------
      #-- Step 80
      #-- Generate the transaction id
      #------------------------------------------------------------------------
      if num_return_code == 0:
         
         str_session_id = '{' + str(uuid.uuid4()) + '}';
         
         sql_statement1 = """
            DECLARE
               str_session_id           VARCHAR2(40 Char);
               int_start_nhdplusid      NUMBER(19);
               num_start_measure        NUMBER;
               geom_start_point         MDSYS.SDO_GEOMETRY;
               num_snap_max_km          NUMBER := 15;
               num_fall_max_km          NUMBER := 4;
               int_target_fcode         PLS_INTEGER;
               
               ary_flowlines            nhdplus.raindrop_np21.internal_indexed_flowline_list;
               num_path_distance        NUMBER;
               sdo_path_line            MDSYS.SDO_GEOMETRY;
               sdo_end_point            MDSYS.SDO_GEOMETRY;
               int_raindrop_return_code PLS_INTEGER;
               int_return_code          PLS_INTEGER;
               str_status_message       VARCHAR2(256 Char);
               str_search_type          VARCHAR2(255 Char);
               num_max_distancekm       NUMBER;
               num_max_flowtimeday      NUMBER;
               ary_program_list         MDSYS.SDO_STRING2_ARRAY;
               int_flowline_count       INTEGER;
               str_out_nav_engine       VARCHAR2(255 Char);
               int_catchment_count      INTEGER;
               int_sfid_count           INTEGER;
               int_cip_count            INTEGER;
               int_rad_count            INTEGER;
            BEGIN
               -------------------------------------------------------------------
               str_session_id      := """ + format_string(str_session_id)  + """;
               str_search_type     := """ + format_string(str_search_type) + """;
               num_max_distancekm  := """ + format_number(str_max_distancekm)  + """;
               num_max_flowtimeday := """ + format_number(str_max_flowtimeday) + """;
               ary_program_list    := """ + str_eventtypelist + """;
               geom_start_point     := MDSYS.SDO_CS.MAKE_2D(
                  MDSYS.SDO_GEOMETRY(2001,4269,MDSYS.SDO_POINT_TYPE(""" + str(num_long) + """,""" + str(num_lat) + """,NULL),NULL,NULL)
               ); 
               -------------------------------------------------------------------
               INSERT INTO
               upstream_downstream_v4.tmp_updn_status(
                  objectid
                 ,session_id
                 ,session_datestamp
               ) VALUES (
                  upstream_downstream_v4.tmp_updn_status_seq.NEXTVAL
                 ,str_session_id
                 ,SYSTIMESTAMP
               );
               ----------------------------------------------------------------------
               nhdplus.raindrop_np21.raindrop_index_fallback(
                   p_point                     => geom_start_point
                  ,p_raindrop_fcode_allow      => NULL
                  ,p_raindrop_fcode_deny       => NULL
                  ,p_raindrop_snap_max_dist_km => 2
                  ,p_raindrop_path_max_dist_km => num_snap_max_km
                  ,p_raindrop_limit_innetwork  => 'TRUE'
                  ,p_raindrop_limit_navigable  => 'FALSE'
                  ,p_fallback_fcode_allow      => NULL
                  ,p_fallback_fcode_deny       => NULL
                  ,p_fallback_distance_max_km  => num_fall_max_km
                  ,p_fallback_limit_innetwork  => 'FALSE'
                  ,p_fallback_limit_navigable  => 'TRUE'
                  ,p_return_link_path          => 'TRUE'
                  ,p_output_flowlines          => ary_flowlines 
                  ,p_path_distance             => num_path_distance
                  ,p_end_point                 => sdo_path_line
                  ,p_path_line                 => sdo_end_point
                  ,p_raindrop_return_code      => int_raindrop_return_code
                  ,p_return_code               => int_return_code
                  ,p_status_message            => str_status_message
               );
               IF int_return_code <> 0
               THEN
                  UPDATE upstream_downstream_v4.tmp_updn_status a
                  SET
                   return_code    = int_return_code
                  ,status_message = str_status_message
                  WHERE
                  a.session_id = str_session_id;
                  ------------------------------
                  RETURN;
                  ------------------------------
               END IF;
               ----------------------------------------------------------------------
               INSERT INTO
               nhdplus_indexing.tmp_indexing_path(
                   objectid
                  ,session_id
                  ,pathid
                  ,lengthkm
                  ,shape
               ) VALUES (
                   nhdplus_indexing.tmp_indexing_path_seq.NEXTVAL
                  ,str_session_id
                  ,'START'
                  ,ROUND(num_path_distance,3)
                  ,sdo_path_line
               );
               ----------------------------------------------------------------------
               IF int_raindrop_return_code = -20011
               THEN
                  UPDATE upstream_downstream_v4.tmp_updn_status a
                  SET
                   return_code    = int_raindrop_return_code
                  ,status_message = 'Unable to navigate further as flow from this location ends in a NHDPlus sink.'
                  WHERE
                  a.session_id = str_session_id;
                  ------------------------------
                  RETURN;
                  ------------------------------
               END IF;
               ----------------------------------------------------------------------
               int_start_nhdplusid := ary_flowlines(1).comid;
               num_start_measure   := ary_flowlines(1).snap_measure;
               int_target_fcode    := ary_flowlines(1).fcode;
               ----------------------------------------------------------------------
               IF int_target_fcode IN (56600)
               THEN
                  UPDATE upstream_downstream_v4.tmp_updn_status a
                  SET
                   return_code    = -56600
                  ,status_message = 'Unable to navigate further on the NHDPlus network from a coastal flowline.'
                  WHERE
                  a.session_id = str_session_id;
                  ------------------------------
                  RETURN;
                  ------------------------------
               END IF;
               -------------------------------------------------------------------
               upstream_downstream_v4.updn.updn_main(
                   p_search_type                   => str_search_type
                  ,p_start_nhdplusid               => int_start_nhdplusid
                  ,p_start_permanent_identifier    => NULL
                  ,p_start_hydrosequence           => NULL
                  ,p_start_reachcode               => NULL
                  ,p_start_measure                 => num_start_measure
                  ,p_start_source_featureid        => NULL
                  ,p_start_source_featureid2       => NULL
                  ,p_start_source_originator       => NULL
                  ,p_start_source_series           => NULL
                  ,p_start_start_date              => NULL
                  ,p_start_end_date                => NULL
                  ,p_start_permid_joinkey          => NULL
                  ,p_start_source_joinkey          => NULL
                  ,p_start_cat_joinkey             => NULL
                  ,p_start_linked_data_program     => NULL
                  ,p_start_search_precision        => NULL
                  ,p_start_search_logic            => NULL
                  ,p_stop_nhdplusid                => NULL
                  ,p_stop_permanent_identifier     => NULL
                  ,p_stop_hydrosequence            => NULL
                  ,p_stop_reachcode                => NULL
                  ,p_stop_measure                  => NULL
                  ,p_stop_source_featureid         => NULL
                  ,p_stop_source_featureid2        => NULL
                  ,p_stop_source_originator        => NULL
                  ,p_stop_source_series            => NULL
                  ,p_stop_start_date               => NULL
                  ,p_stop_end_date                 => NULL
                  ,p_stop_permid_joinkey           => NULL
                  ,p_stop_source_joinkey           => NULL
                  ,p_stop_cat_joinkey              => NULL
                  ,p_stop_linked_data_program      => NULL
                  ,p_stop_search_precision         => NULL
                  ,p_stop_search_logic             => NULL
                  ,p_search_max_distancekm         => num_max_distancekm
                  ,p_search_max_flowtimeday        => num_max_flowtimeday
                  ,p_linked_data_program_list      => ary_program_list
                  ,p_search_precision              => 'BEST'
                  ,p_return_network_flowlines      => 'TRUE'
                  ,p_return_catchments             => 'FALSE'
                  ,p_return_linked_data_cip        => 'FALSE'
                  ,p_return_linked_data_source     => 'TRUE'
                  ,p_return_linked_data_rad        => 'TRUE'
                  ,p_return_linked_data_attr       => """ + format_stringboo(boo_attributes) + """
                  ,p_remove_stop_start_sfids       => 'TRUE'
                  ,p_navigation_engine             => """ + format_string(str_navigation_engine) + """
                  ,p_push_source_geometry_as_rad   => 'FALSE'
                  ,out_flowline_count              => int_flowline_count
                  ,out_navigation_engine           => str_out_nav_engine
                  ,out_catchment_count             => int_catchment_count
                  ,out_sfid_count                  => int_sfid_count
                  ,out_cip_count                   => int_cip_count
                  ,out_rad_count                   => int_rad_count
                  ,out_return_code                 => int_return_code
                  ,out_status_message              => str_status_message
                  ,p_sessionid                     => str_session_id
               );
               UPDATE upstream_downstream_v4.tmp_updn_status a
               SET
                return_code    = int_return_code
               ,status_message = str_status_message
               WHERE
               a.session_id = str_session_id;
               -------------------------------------------------------------------
               RETURN;
            END;
         """;
         #arcpy.AddMessage(sql_statement1);

      #------------------------------------------------------------------------
      #-- Step 90
      #-- Execute the Database Service
      #------------------------------------------------------------------------
      if num_return_code == 0:
         
         sde_return = sde_conn.execute(sql_statement1)
         arcpy.AddMessage(". upstream downstream service complete.");

         sql_statement = """
            SELECT
             a.return_code
            ,a.status_message
            FROM
            upstream_downstream_v4.tmp_updn_status a
            WHERE
            a.session_id = """ + format_string(str_session_id) + """
         """;
         
         sde_return = sde_conn.execute(sql_statement);

         if sde_return[0][0] != 0:
            num_return_code = sde_return[0][0];
            str_status_message = sde_return[0][1];
            
         arcpy.AddMessage(". upstream downstream return code " + str(num_return_code) + ".");

      #------------------------------------------------------------------------
      #-- Step 100
      #-- Push out results from the geodatabase
      #------------------------------------------------------------------------
      if num_return_code == 0:
         
         #---------------------------------------------------------------------
         if boo_show_source:
            if 10006 in ary_eventtypelist \
            or 10009 in ary_eventtypelist \
            or 10010 in ary_eventtypelist :
            
               with arcpy.da.InsertCursor(
                   in_table     = scratch_full_source_a
                  ,field_names  = [
                      'eventtype'
                     ,'program_name'
                     ,'permid_joinkey'
                     ,'source_originator'
                     ,'source_featureid'
                     ,'source_featureid2'
                     ,'source_series'
                     ,'source_subdivision'
                     ,'source_joinkey'
                     ,'start_date'
                     ,'end_date'
                     ,'featuredetailurl'
                     ,'areasqkm'
                     ,'nearest_network_distancekm'
                     ,'nearest_network_flowtimeday'
                     ,'SHAPE@'
                   ]
               ) as icursor:
                  
                  with arcpy.da.SearchCursor(
                      in_table     = sde_conn_path + "\\rad_ags.updn_v4_ldsrcareas"
                     ,field_names  = [
                         'eventtype'
                        ,'program_name'
                        ,'permid_joinkey'
                        ,'source_originator'
                        ,'source_featureid'
                        ,'source_featureid2'
                        ,'source_series'
                        ,'source_subdivision'
                        ,'source_joinkey'
                        ,'start_date'
                        ,'end_date'
                        ,'featuredetailurl'
                        ,'areasqkm'
                        ,'nearest_network_distancekm'
                        ,'nearest_network_flowtimeday'
                        ,'SHAPE@'
                      ]
                     ,where_clause = "SESSION_ID = '" + str_session_id + "' "
                  ) as scursor:
               
                     for row in scursor:
                        icursor.insertRow(row);
                        
               arcpy.SetParameterAsText(10,scratch_full_source_a);
               
            else:
               arcpy.SetParameterAsText(10,"");
               
         else:
            arcpy.SetParameterAsText(10,"");
            
      else:
         arcpy.SetParameterAsText(10,"");
         
      #------------------------------------------------------------------------
      if num_return_code == 0:

         #---------------------------------------------------------------------
         if boo_show_source:
            if 10006 in ary_eventtypelist \
            or 10009 in ary_eventtypelist \
            or 10010 in ary_eventtypelist :

               with arcpy.da.InsertCursor(
                   in_table     = scratch_full_source_l
                  ,field_names  = [
                      'eventtype'
                     ,'program_name'
                     ,'permid_joinkey'
                     ,'source_originator'
                     ,'source_featureid'
                     ,'source_featureid2'
                     ,'source_series'
                     ,'source_subdivision'
                     ,'source_joinkey'
                     ,'start_date'
                     ,'end_date'
                     ,'featuredetailurl'
                     ,'lengthkm'
                     ,'nearest_network_distancekm'
                     ,'nearest_network_flowtimeday'
                     ,'SHAPE@'
                   ]
               ) as icursor:
                  
                  with arcpy.da.SearchCursor(
                      in_table     = sde_conn_path + "\\rad_ags.updn_v4_ldsrclines"
                     ,field_names  = [
                         'eventtype'
                        ,'program_name'
                        ,'permid_joinkey'
                        ,'source_originator'
                        ,'source_featureid'
                        ,'source_featureid2'
                        ,'source_series'
                        ,'source_subdivision'
                        ,'source_joinkey'
                        ,'start_date'
                        ,'end_date'
                        ,'featuredetailurl'
                        ,'lengthkm'
                        ,'nearest_network_distancekm'
                        ,'nearest_network_flowtimeday'
                        ,'SHAPE@'
                      ]
                     ,where_clause = "SESSION_ID = '" + str_session_id + "' "
                  ) as scursor:
               
                     for row in scursor:
                        icursor.insertRow(row);
                        
               arcpy.SetParameterAsText(11,scratch_full_source_l);
               
            else:
               arcpy.SetParameterAsText(11,"");
               
         else:
            arcpy.SetParameterAsText(11,"");
            
      else:
         arcpy.SetParameterAsText(11,"");
         
      #------------------------------------------------------------------------
      # source_subdivision is missing from ancient Oracle SDE registered view
      if num_return_code == 0:
         
         if boo_show_source:
            with arcpy.da.InsertCursor(
                in_table     = scratch_full_source_p
               ,field_names  = [
                   'eventtype'
                  ,'program_name'
                  ,'permid_joinkey'
                  ,'source_originator'
                  ,'source_featureid'
                  ,'source_featureid2'
                  ,'source_series'
                  ,'source_joinkey'
                  ,'start_date'
                  ,'end_date'
                  ,'featuredetailurl'
                  ,'nearest_network_distancekm'
                  ,'nearest_network_flowtimeday'
                  ,'SHAPE@'
                ]
            ) as icursor:
               
               with arcpy.da.SearchCursor(
                   in_table     = sde_conn_path + "\\rad_ags.updn_v4_ldsrcpoints"
                  ,field_names  = [
                      'eventtype'
                     ,'program_name'
                     ,'permid_joinkey'
                     ,'source_originator'
                     ,'source_featureid'
                     ,'source_featureid2'
                     ,'source_series'
                     ,'source_joinkey'
                     ,'start_date'
                     ,'end_date'
                     ,'featuredetailurl'
                     ,'nearest_network_distancekm'
                     ,'nearest_network_flowtimeday'
                     ,'SHAPE@'
                   ]
                  ,where_clause = "SESSION_ID = '" + str_session_id + "' "
               ) as scursor:
            
                  for row in scursor:
                     icursor.insertRow(row);
                     
            arcpy.SetParameterAsText(12,scratch_full_source_p);
            
         else:
            arcpy.SetParameterAsText(12,"");
            
      else:
         arcpy.SetParameterAsText(12,"");

      #------------------------------------------------------------------------
      if num_return_code == 0:
         
         #---------------------------------------------------------------------
         if 10006 in ary_eventtypelist \
         or 10009 in ary_eventtypelist \
         or 10010 in ary_eventtypelist :
         
            with arcpy.da.InsertCursor(
                in_table     = scratch_full_reached_a
               ,field_names  = [
                   'eventtype' 
                  ,'program_name'   
                  ,'permanent_identifier'
                  ,'permid_joinkey' 
                  ,'eventdate'      
                  ,'reachcode'      
                  ,'reachsmdate'    
                  ,'reachresolution'
                  ,'feature_permanent_identifier'
                  ,'featureclassref'
                  ,'source_originator'
                  ,'source_featureid'
                  ,'source_featureid2'
                  ,'source_datadesc'
                  ,'source_series'  
                  ,'source_subdivision'
                  ,'source_joinkey' 
                  ,'start_date'     
                  ,'end_date'       
                  ,'featuredetailurl'
                  ,'event_areasqkm' 
                  ,'geogstate'      
                  ,'network_distancekm'
                  ,'network_flowtimeday'
                  ,'SHAPE@'
                ]
            ) as icursor:
               
               with arcpy.da.SearchCursor(
                   in_table     = sde_conn_path + "\\rad_ags.updn_v4_ldradareas"
                  ,field_names  = [
                      'eventtype' 
                     ,'program_name'   
                     ,'permanent_identifier'
                     ,'permid_joinkey' 
                     ,'eventdate'      
                     ,'reachcode'      
                     ,'reachsmdate'    
                     ,'reachresolution'
                     ,'feature_permanent_identifier'
                     ,'featureclassref'
                     ,'source_originator'
                     ,'source_featureid'
                     ,'source_featureid2'
                     ,'source_datadesc'
                     ,'source_series'  
                     ,'source_subdivision'
                     ,'source_joinkey' 
                     ,'start_date'     
                     ,'end_date'       
                     ,'featuredetailurl'
                     ,'event_areasqkm' 
                     ,'geogstate'      
                     ,'network_distancekm'
                     ,'network_flowtimeday'
                     ,'SHAPE@'
                   ]
                  ,where_clause = "SESSION_ID = '" + str_session_id + "' "
               ) as scursor:
            
                  for row in scursor:
                     icursor.insertRow(row);
                     
            arcpy.SetParameterAsText(13,scratch_full_reached_a);
            
         else:
            arcpy.SetParameterAsText(13,"");
            
      else:
         arcpy.SetParameterAsText(13,"");

      #------------------------------------------------------------------------
      if num_return_code == 0:
         
         #---------------------------------------------------------------------
         if 10006 in ary_eventtypelist \
         or 10009 in ary_eventtypelist \
         or 10010 in ary_eventtypelist :
         
            with arcpy.da.InsertCursor(
                in_table     = scratch_full_reached_l
               ,field_names  = [
                   'eventtype' 
                  ,'program_name'   
                  ,'permanent_identifier'
                  ,'permid_joinkey' 
                  ,'eventdate'      
                  ,'reachcode'      
                  ,'reachsmdate'    
                  ,'reachresolution'
                  ,'feature_permanent_identifier'
                  ,'featureclassref'
                  ,'source_originator'
                  ,'source_featureid'
                  ,'source_featureid2'
                  ,'source_datadesc'
                  ,'source_series'  
                  ,'source_subdivision'
                  ,'source_joinkey' 
                  ,'start_date'     
                  ,'end_date'       
                  ,'featuredetailurl'
                  ,'fmeasure'
                  ,'tmeasure'
                  ,'eventoffset'
                  ,'event_lengthkm' 
                  ,'geogstate'      
                  ,'network_distancekm'
                  ,'network_flowtimeday'
                  ,'SHAPE@'
                ]
            ) as icursor:
               
               with arcpy.da.SearchCursor(
                   in_table     = sde_conn_path + "\\rad_ags.updn_v4_ldradlines"
                  ,field_names  = [
                      'eventtype' 
                     ,'program_name'   
                     ,'permanent_identifier'
                     ,'permid_joinkey' 
                     ,'eventdate'      
                     ,'reachcode'      
                     ,'reachsmdate'    
                     ,'reachresolution'
                     ,'feature_permanent_identifier'
                     ,'featureclassref'
                     ,'source_originator'
                     ,'source_featureid'
                     ,'source_featureid2'
                     ,'source_datadesc'
                     ,'source_series'  
                     ,'source_subdivision'
                     ,'source_joinkey' 
                     ,'start_date'     
                     ,'end_date'       
                     ,'featuredetailurl'
                     ,'fmeasure'
                     ,'tmeasure'
                     ,'eventoffset'
                     ,'event_lengthkm'  
                     ,'geogstate'      
                     ,'network_distancekm'
                     ,'network_flowtimeday'
                     ,'SHAPE@'
                   ]
                  ,where_clause = "SESSION_ID = '" + str_session_id + "' "
               ) as scursor:
            
                  for row in scursor:
                     icursor.insertRow(row);
                     
            arcpy.SetParameterAsText(14,scratch_full_reached_l);
            
         else:
            arcpy.SetParameterAsText(14,"");
            
      else:
         arcpy.SetParameterAsText(14,"");
         
      #------------------------------------------------------------------------
      if num_return_code == 0:
         
         with arcpy.da.InsertCursor(
             in_table     = scratch_full_reached_p
            ,field_names  = [
                'eventtype' 
               ,'program_name'   
               ,'permanent_identifier'
               ,'permid_joinkey' 
               ,'eventdate'      
               ,'reachcode'      
               ,'reachsmdate'    
               ,'reachresolution'
               ,'feature_permanent_identifier'
               ,'featureclassref'
               ,'source_originator'
               ,'source_featureid'
               ,'source_featureid2'
               ,'source_datadesc'
               ,'source_series'  
               ,'source_subdivision'
               ,'source_joinkey' 
               ,'start_date'     
               ,'end_date'       
               ,'featuredetailurl'
               ,'measure'
               ,'eventoffset'
               ,'geogstate'      
               ,'network_distancekm'
               ,'network_flowtimeday'
               ,'SHAPE@'
             ]
         ) as icursor:
            
            with arcpy.da.SearchCursor(
                in_table     = sde_conn_path + "\\rad_ags.updn_v4_ldradpoints"
               ,field_names  = [
                   'eventtype' 
                  ,'program_name'   
                  ,'permanent_identifier'
                  ,'permid_joinkey' 
                  ,'eventdate'      
                  ,'reachcode'      
                  ,'reachsmdate'    
                  ,'reachresolution'
                  ,'feature_permanent_identifier'
                  ,'featureclassref'
                  ,'source_originator'
                  ,'source_featureid'
                  ,'source_featureid2'
                  ,'source_datadesc'
                  ,'source_series'  
                  ,'source_subdivision'
                  ,'source_joinkey' 
                  ,'start_date'     
                  ,'end_date'       
                  ,'featuredetailurl'
                  ,'measure'
                  ,'eventoffset'
                  ,'geogstate'      
                  ,'network_distancekm'
                  ,'network_flowtimeday'
                  ,'SHAPE@'
                ]
               ,where_clause = "SESSION_ID = '" + str_session_id + "' "
            ) as scursor:
         
               for row in scursor:
                  icursor.insertRow(row);
                  
         arcpy.SetParameterAsText(15,scratch_full_reached_p);
         
      else:
         arcpy.SetParameterAsText(15,"");

      #------------------------------------------------------------------------
      if num_return_code == 0:
                  
         if boo_nav_results:
         
            ######################################################################
            if str_navigation_engine == 'V1':
               
               with arcpy.da.InsertCursor(
                   in_table     = scratch_full_fl
                  ,field_names  = [
                      'nhdplusid'
                     ,'hydroseq'
                     ,'fmeasure'
                     ,'tmeasure'
                     ,'lengthkm'
                     ,'flowtimeday'
                     ,'network_distancekm'
                     ,'network_flowtimeday'
                     ,'levelpathi'
                     ,'terminalpa'
                     ,'uphydroseq'
                     ,'dnhydroseq'
                     ,'navtermination_flag'
                     ,'SHAPE@' 
                   ]
               ) as icursor:
                  
                  with arcpy.da.SearchCursor(
                      in_table     = sde_conn_path + "\\rad_ags.navigation_v1_results"
                     ,field_names  = [
                         'nhdplusid'
                        ,'hydrosequence'
                        ,'fmeasure'
                        ,'tmeasure'
                        ,'lengthkm'
                        ,'flowtimeday'
                        ,'network_distancekm'
                        ,'network_flowtimeday'
                        ,'levelpathid'
                        ,'terminalpathid'
                        ,'uphydrosequence'
                        ,'downhydrosequence'
                        ,'navtermination_flag'
                        ,'SHAPE@'  
                      ]
                     ,where_clause = "SESSION_ID = '" + str_session_id + "' "
                  ) as scursor:
               
                     for row in scursor:
                        icursor.insertRow(row);
                        
            ######################################################################
            elif str_navigation_engine == 'V2':
               
               with arcpy.da.InsertCursor(
                   in_table     = scratch_full_fl
                  ,field_names  = [
                      'nhdplusid'
                     ,'hydroseq'
                     ,'fmeasure'
                     ,'tmeasure'
                     ,'lengthkm'
                     ,'flowtimeday'
                     ,'network_distancekm'
                     ,'network_flowtimeday'
                     ,'levelpathi'
                     ,'terminalpa'
                     ,'uphydroseq'
                     ,'dnhydroseq'
                     ,'navtermination_flag'
                     ,'SHAPE@' 
                   ]
               ) as icursor:
                  
                  with arcpy.da.SearchCursor(
                      in_table     = sde_conn_path + "\\rad_ags.navigation_v2_results"
                     ,field_names  = [
                         'nhdplusid'
                        ,'hydrosequence'
                        ,'fmeasure'
                        ,'tmeasure'
                        ,'lengthkm'
                        ,'flowtimeday'
                        ,'network_distancekm'
                        ,'network_flowtimeday'
                        ,'levelpathid'
                        ,'terminalpathid'
                        ,'uphydrosequence'
                        ,'downhydrosequence'
                        ,'navtermination_flag'
                        ,'SHAPE@'  
                      ]
                     ,where_clause = "SESSION_ID = '" + str_session_id + "' "
                  ) as scursor:
               
                     for row in scursor:
                        icursor.insertRow(row);

            ######################################################################
            elif str_navigation_engine == 'V3':
               
               with arcpy.da.InsertCursor(
                   in_table     = scratch_full_fl
                  ,field_names  = [
                      'nhdplusid'
                     ,'hydroseq'
                     ,'fmeasure'
                     ,'tmeasure'
                     ,'lengthkm'
                     ,'flowtimeday'
                     ,'network_distancekm'
                     ,'network_flowtimeday'
                     ,'levelpathi'
                     ,'terminalpa'
                     ,'uphydroseq'
                     ,'dnhydroseq'
                     ,'navtermination_flag'
                     ,'SHAPE@' 
                   ]
               ) as icursor:
                  
                  with arcpy.da.SearchCursor(
                      in_table     = sde_conn_path + "\\rad_ags.navigation_v3_results"
                     ,field_names  = [
                         'nhdplusid'
                        ,'hydrosequence'
                        ,'fmeasure'
                        ,'tmeasure'
                        ,'lengthkm'
                        ,'flowtimeday'
                        ,'network_distancekm'
                        ,'network_flowtimeday'
                        ,'levelpathid'
                        ,'terminalpathid'
                        ,'uphydrosequence'
                        ,'downhydrosequence'
                        ,'navtermination_flag'
                        ,'SHAPE@'  
                      ]
                     ,where_clause = "SESSION_ID = '" + str_session_id + "' "
                  ) as scursor:
               
                     for row in scursor:
                        icursor.insertRow(row);
                        
            else:
               raise Exception("err");
                     
            arcpy.SetParameterAsText(16,scratch_full_fl);
            
         else:
            arcpy.SetParameterAsText(16,"");
            
      else:
         arcpy.SetParameterAsText(16,"");
         
      #------------------------------------------------------------------------   
      if num_return_code == 0:
         
         if boo_attributes and 10028 in ary_eventtypelist:
         
            with arcpy.da.InsertCursor(
                in_table     = scratch_frspub_attr
               ,field_names  = [
                   'source_joinkey'
                  ,'registry_id'
                  ,'primary_name'
                  ,'city_name'
                  ,'county_name'
                  ,'fips_code'
                  ,'state_code'
                  ,'state_name'
                  ,'country_name'
                  ,'postal_code'
                  ,'tribal_land_code'
                  ,'tribal_land_name'
                  ,'us_mexico_border_ind'
                  ,'pgm_sys_id'
                  ,'pgm_sys_acrnm'
                  ,'nearest_cip_network_distancekm'
                  ,'nearest_cip_network_flowtimeda'
                  ,'nearest_rad_network_distancekm'
                  ,'nearest_rad_network_flowtimeda'
                ]
            ) as icursor:
               
               with arcpy.da.SearchCursor(
                   in_table     = sde_conn_path + "\\rad_ags.updn_v4_ldattrfrspub"
                  ,field_names  = [
                      'source_joinkey'
                     ,'registry_id'
                     ,'primary_name'
                     ,'city_name'
                     ,'county_name'
                     ,'fips_code'
                     ,'state_code'
                     ,'state_name'
                     ,'country_name'
                     ,'postal_code'
                     ,'tribal_land_code'
                     ,'tribal_land_name'
                     ,'us_mexico_border_ind'
                     ,'pgm_sys_id'
                     ,'pgm_sys_acrnm'
                     ,'nearest_cip_network_distancekm'
                     ,'nearest_cip_network_flowtimeda'
                     ,'nearest_rad_network_distancekm'
                     ,'nearest_rad_network_flowtimeda'
                   ]
                  ,where_clause = "SESSION_ID = '" + str_session_id + "' "
               ) as scursor:
            
                  for row in scursor:
                     icursor.insertRow(row);
                     
            arcpy.SetParameterAsText(17,scratch_frspub_attr);
            
         else:
            arcpy.SetParameterAsText(17,"");
            
      else:
         arcpy.SetParameterAsText(17,"");
         
      #------------------------------------------------------------------------   
      if num_return_code == 0:
         
         if boo_attributes and 10015 in ary_eventtypelist:
         
            with arcpy.da.InsertCursor(
                in_table     = scratch_npdes_attr
               ,field_names  = [
                   'source_joinkey'
                  ,'external_permit_nmbr'
                  ,'permit_name'
                  ,'registry_id'
                  ,'primary_name'
                  ,'state_code'
                  ,'agency_type_code'
                  ,'issue_date'
                  ,'issuing_agency'
                  ,'original_issue_date'
                  ,'permit_status_code'
                  ,'permit_type_code'
                  ,'retirement_date'
                  ,'termination_date'
                  ,'nearest_cip_network_distancekm'
                  ,'nearest_cip_network_flowtimeda'
                  ,'nearest_rad_network_distancekm'
                  ,'nearest_rad_network_flowtimeda'
                ]
            ) as icursor:
               
               with arcpy.da.SearchCursor(
                   in_table     = sde_conn_path + "\\rad_ags.updn_v4_ldattrnpdes"
                  ,field_names  = [
                      'source_joinkey'
                     ,'external_permit_nmbr'
                     ,'permit_name'
                     ,'registry_id'
                     ,'primary_name'
                     ,'state_code'
                     ,'agency_type_code'
                     ,'issue_date'
                     ,'issuing_agency'
                     ,'original_issue_date'
                     ,'permit_status_code'
                     ,'permit_type_code'
                     ,'retirement_date'
                     ,'termination_date'
                     ,'nearest_cip_network_distancekm'
                     ,'nearest_cip_network_flowtimeda'
                     ,'nearest_rad_network_distancekm'
                     ,'nearest_rad_network_flowtimeda'
                   ]
                  ,where_clause = "SESSION_ID = '" + str_session_id + "' "
               ) as scursor:
            
                  for row in scursor:
                     icursor.insertRow(row);
                     
            arcpy.SetParameterAsText(18,scratch_npdes_attr);
            
         else:
            arcpy.SetParameterAsText(18,"");
            
      else:
         arcpy.SetParameterAsText(18,"");
         
      #------------------------------------------------------------------------   
      if num_return_code == 0:
         
         if boo_attributes and 10032 in ary_eventtypelist:
         
            with arcpy.da.InsertCursor(
                in_table     = scratch_wqp_attr
               ,field_names  = [
                   'source_joinkey'
                  ,'organizationidentifier'
                  ,'organizationformalname'
                  ,'monitoringlocationidentifier'
                  ,'monitoringlocationname'
                  ,'monitoringlocationtypename'
                  ,'monitoringlocationdescription'
                  ,'huceightdigitcode'
                  ,'drainageareameasure_measureval'
                  ,'drainageareameasure_measureunt'
                  ,'contributingdrainageareameasva'
                  ,'contributingdrainageareameasun'
                  ,'latitudemeasure'
                  ,'longitudemeasure'
                  ,'sourcemapscalenumeric'
                  ,'horizontalaccuracymeasureval'
                  ,'horizontalaccuracymeasureunit'
                  ,'horizontalcollectionmethodname'
                  ,'horizontalcoordinatereferences'
                  ,'verticalmeasure_measurevalue'
                  ,'verticalmeasure_measureunit'
                  ,'verticalaccuracymeasurevalue'
                  ,'verticalaccuracymeasureunit'
                  ,'verticalcollectionmethodname'
                  ,'verticalcoordinatereferencesys'
                  ,'countrycode'
                  ,'statecode'
                  ,'countycode'
                  ,'aquifername'
                  ,'formationtypetext'
                  ,'aquifertypename'
                  ,'constructiondatetext'
                  ,'welldepthmeasure_measurevalue'
                  ,'welldepthmeasure_measureunit'
                  ,'wellholedepthmeasure_measureva'
                  ,'wellholedepthmeasure_measureun'
                  ,'providername'
                  ,'nearest_cip_network_distancekm'
                  ,'nearest_cip_network_flowtimeda'
                  ,'nearest_rad_network_distancekm'
                  ,'nearest_rad_network_flowtimeda'
                ]
            ) as icursor:
               
               with arcpy.da.SearchCursor(
                   in_table     = sde_conn_path + "\\rad_ags.updn_v4_ldattrwqp"
                  ,field_names  = [
                      'source_joinkey'
                     ,'organizationidentifier'
                     ,'organizationformalname'
                     ,'monitoringlocationidentifier'
                     ,'monitoringlocationname'
                     ,'monitoringlocationtypename'
                     ,'monitoringlocationdescription'
                     ,'huceightdigitcode'
                     ,'drainageareameasure_measureval'
                     ,'drainageareameasure_measureunt'
                     ,'contributingdrainageareameasva'
                     ,'contributingdrainageareameasun'
                     ,'latitudemeasure'
                     ,'longitudemeasure'
                     ,'sourcemapscalenumeric'
                     ,'horizontalaccuracymeasureval'
                     ,'horizontalaccuracymeasureunit'
                     ,'horizontalcollectionmethodname'
                     ,'horizontalcoordinatereferences'
                     ,'verticalmeasure_measurevalue'
                     ,'verticalmeasure_measureunit'
                     ,'verticalaccuracymeasurevalue'
                     ,'verticalaccuracymeasureunit'
                     ,'verticalcollectionmethodname'
                     ,'verticalcoordinatereferencesys'
                     ,'countrycode'
                     ,'statecode'
                     ,'countycode'
                     ,'aquifername'
                     ,'formationtypetext'
                     ,'aquifertypename'
                     ,'constructiondatetext'
                     ,'welldepthmeasure_measurevalue'
                     ,'welldepthmeasure_measureunit'
                     ,'wellholedepthmeasure_measureva'
                     ,'wellholedepthmeasure_measureun'
                     ,'providername'
                     ,'nearest_cip_network_distancekm'
                     ,'nearest_cip_network_flowtimeda'
                     ,'nearest_rad_network_distancekm'
                     ,'nearest_rad_network_flowtimeda'
                   ]
                  ,where_clause = "SESSION_ID = '" + str_session_id + "' "
               ) as scursor:
            
                  for row in scursor:
                     icursor.insertRow(row);
                     
            arcpy.SetParameterAsText(19,scratch_wqp_attr);
            
         else:
            arcpy.SetParameterAsText(19,"");
            
      else:
         arcpy.SetParameterAsText(19,"");
            
      #------------------------------------------------------------------------   
      if num_return_code == 0:
            
         with arcpy.da.InsertCursor(
             in_table     = scratch_full_link
            ,field_names  = [
                'SHAPE@'
             ]
         ) as icursor:
            
            with arcpy.da.SearchCursor(
                in_table     = sde_conn_path + "\\rad_ags.indexing_v2_indexingpath"
               ,field_names  = [
                   'SHAPE@'
                ]
               ,where_clause = "SESSION_ID = '" + str_session_id + "' "
            ) as scursor:
         
               for row in scursor:
                  icursor.insertRow(row);
                  
         arcpy.SetParameterAsText(20,scratch_full_link);
         
      else:
         arcpy.SetParameterAsText(20,"");

      #------------------------------------------------------------------------
      #-- Step 110
      #-- Cough out results
      #------------------------------------------------------------------------
      if num_return_code == 0:
         str_status_message = "Upstream/Downstream v4 Search completed.";

      if str_status_message is None:
         str_status_message = "";

      arcpy.SetParameterAsText(21,str_status_message);

###############################################################################
def format_stringboo(val):

   if val is None:
      return "NULL";

   elif val is True:
      return "'TRUE'";
   
   elif val is False:
      return "'FALSE'";
   
   
###############################################################################
def format_string(val):

   if val is None:
      return "NULL";

   val = val.replace("'","''");

   return "'" + val + "'";

###############################################################################
def format_number(val):

   if val is None:
      return "NULL";

   return str(val);
   
   