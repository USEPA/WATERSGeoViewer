import arcpy
import sys,os
import uuid

str_searchtype       = "StreamSelectionType";
str_source_area_fc   = "ResultSourceAreaLinkedData";
str_source_line_fc   = "ResultSourceLinearLinkedData";
str_source_point_fc  = "ResultSourcePointLinkedData";
str_reached_area_fc  = "ResultReachedAreaLinkedData";
str_reached_line_fc  = "ResultReachedLinearLinkedData";
str_reached_point_fc = "ResultReachedPointLinkedData";
str_nav_results_name = "ResultStreamsSelected";
str_link_path_name   = "ResultLinkPath";
str_programlist_name = "SearchForTheseLinkedData";
str_program_default  = "Assessment, Total Maximum Daily Load Tracking and Implementation System (ATTAINS)";
  
def search_type(input):

   if input == "Upstream with Tributaries":
      return "UT";

   elif input == "Upstream Main Path Only":
      return "UM";

   elif input == "Downstream with Divergences":
      return "DD";

   elif input == "Downstream Main Path Only":
      return "DM";
      
   elif input == "Point to Point":
      return "PP";

   elif input == "":
      return None;

   return input;

def strip_empty(input):

   if input == "":
      return None;

   return input;

def to_eventtype(input):

   tmp = input;

   if tmp == "":
      return "NULL";

   elif tmp is not None:
      tmp = tmp.replace('\'','');
      ary_tmp = [];
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

   return tmp;

def get_boo(input):

   if str(input) in ["true","TRUE","Y"]:
      return True;

   else:
      return False;

def navtype_list():

   return [
       "Upstream with Tributaries"
      ,"Upstream Main Path Only"
      ,"Downstream with Divergences"
      ,"Downstream Main Path Only"
      ,"Point to Point"
   ];
   
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
      
   elif input == "Nonpoint Source Projects":
      return 10011;
      
   return input;

def eventtype_list():

   return [
       "Assessment, Total Maximum Daily Load Tracking and Implementation System (ATTAINS)"
      ,"Clean Watersheds Needs Survey"
      ,"Fish Consumption Advisories"
      ,"Fish Tissue Data"
      ,"Facilities that Discharge to Water"
      ,"Facility Registry Service"
      ,"Water Quality Portal Monitoring Data"
      ,"Nonpoint Source Projects"
   ];

def unpack_fc(input):

   desc               = arcpy.Describe(input);
   sr                 = desc.spatialReference;
   num_start_srid     = sr.factoryCode;
   str_status_message = "";
   num_return_code    = 0;

   rows = [row for row in arcpy.da.SearchCursor(input,["SHAPE@"])];
   if rows is None or len(rows) == 0:
      num_return_code = -30;
      str_status_message += "No points found in start point feature class. ";

   else:
      geom = rows[-1][0];

      if geom.type != "point":
         geom = arcpy.PointGeometry(geom.trueCentroid);

      str_start_wkt_geom = geom.WKT;
      
      if num_start_srid == 4269:
         num_start_srid = 8265;

   return (num_return_code,str_status_message,str_start_wkt_geom,num_start_srid);

def format_string(input):

   if input is None:
      return "NULL";

   input = input.replace("'","''");

   return "'" + input + "'";

def format_number(input):

   if input is None:
      return "NULL";

   return str(input);

def format_geometry(input,srid):

   if input is None:
      return "NULL";

   if srid is None:
      srid = 0;

   return "MDSYS.SDO_GEOMETRY('" + input + "'," + str(srid) + ")";

def sqlstatement(session_id,search_type,start_wkt_geom,max_distancekm,max_flowtimeday,programlist,navigation_engine):

   return """
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
         str_search_type          VARCHAR2(2 Char);
         num_max_distancekm       NUMBER;
         num_max_flowtimeday      NUMBER;
         ary_program_list         MDSYS.SDO_STRING2_ARRAY;
      BEGIN
         -------------------------------------------------------------------
         str_session_id      := '""" + session_id      + """';
         geom_start_point    := """  + start_wkt_geom  + """;
         str_search_type     := '""" + search_type     + """';
         num_max_distancekm  := """  + max_distancekm  + """;
         num_max_flowtimeday := """  + max_flowtimeday + """;
         ary_program_list    := """  + programlist     + """;
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
            ,p_return_linked_data_attr       => 'TRUE'
            ,p_navigation_engine             => '""" + navigation_engine + """'
            ,p_push_source_gemetry_as_rad    => NULL
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

def check_results(sde_conn,session_id):

   return_code = 0;
   status_message = "";

   sql_statement = """
      SELECT
       a.return_code
      ,a.status_message
      FROM
      upstream_downstream_v4.tmp_updn_status a
      WHERE
      a.session_id = '""" + session_id + """'
   """

   try:
      sde_return = sde_conn.execute(sql_statement)

   except Exception as err:
      arcpy.AddError(err);
      sys.exit(-1);

   if sde_return[0][0] != 0:
      return_code = sde_return[0][0];
      status_message = sde_return[0][1];

   return (return_code,status_message);
   
def advancedConfig(json_input):
   
   #-- DISTANCE
   #-- RAINDROP
   #-- RAINDROP_FALLBACK
   #-- CATCONSTRAINED
   index_methodology = "RAINDROP_FALLBACK";
   
class Toolbox(object):

   def __init__(self):
   
      self.label = "Toolbox";
      self.alias = "";

      self.tools = [
          SearchUsingStartingPoint
      ];

class SearchUsingStartingPoint(object):

   def __init__(self):
      
      self.label = "SearchUsingStartingPoint"
      self.name  = "SearchUsingStartingPoint"
      self.description = "The Upstream/Downstream Search V4 service is designed to provide standard traversal and linked data discovery functions upon the NHDPlus stream network.  " + \
         "For more information see " +  \
         "<a href='https://watersgeo.epa.gov/openapi/waters/?sfilter=Discovery' target='_blank'>" + \
         "EPA service documentation</a>.";
      self.canRunInBackground = False;

   def getParameterInfo(self):
      
      param0 = arcpy.Parameter(
          displayName   = str_searchtype
         ,name          = str_searchtype
         ,datatype      = "String"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );
      param0.value = "Upstream with Tributaries";
      param0.filter.type = "ValueList";
      param0.filter.list = navtype_list();

      param1 = arcpy.Parameter(
          displayName   = "StartingPoint"
         ,name          = "StartingPoint"
         ,datatype      = "GPFeatureRecordSetLayer"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = True
      );
      param1.filter.list = ['Point'];

      param2 = arcpy.Parameter(
          displayName   = "MaxDistanceKm"
         ,name          = "MaxDistanceKm"
         ,datatype      = "String"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = True
      );
      
      param3 = arcpy.Parameter(
          displayName   = "MaxFlowtimeDay"
         ,name          = "MaxFlowtimeDay"
         ,datatype      = "String"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = True
      );

      param4 = arcpy.Parameter(
          displayName   = str_programlist_name
         ,name          = str_programlist_name
         ,datatype      = "String"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,multiValue    = True
         ,enabled       = True
      );
      param4.value       = str_program_default;
      param4.filter.type = "ValueList";
      param4.filter.list = eventtype_list();
      
      param5 = arcpy.Parameter(
          displayName   = "AdvancedConfiguration"
         ,name          = "AdvancedConfiguration"
         ,datatype      = "String"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = True
      );

      param6 = arcpy.Parameter(
          displayName   = str_source_point_fc
         ,name          = str_source_point_fc
         ,datatype      = "DEFeatureClass"
         ,parameterType = "Derived"
         ,direction     = "Output"
      );
      param6.schema.featureTypeRule  = "AsSpecified";
      param6.schema.featureType      = "Simple";
      param6.schema.geometryTypeRule = "AsSpecified";
      param6.schema.geometryType     = "Point";
      param6.schema.fieldsRule       = "AllNoFIDs";
      
      param7 = arcpy.Parameter(
          displayName   = str_source_line_fc
         ,name          = str_source_line_fc
         ,datatype      = "DEFeatureClass"
         ,parameterType = "Derived"
         ,direction     = "Output"
      );
      param7.schema.featureTypeRule  = "AsSpecified";
      param7.schema.featureType      = "Simple";
      param7.schema.geometryTypeRule = "AsSpecified";
      param7.schema.geometryType     = "Polyline";
      param7.schema.fieldsRule       = "AllNoFIDs";

      param8 = arcpy.Parameter(
          displayName   = str_source_area_fc
         ,name          = str_source_area_fc
         ,datatype      = "DEFeatureClass"
         ,parameterType = "Derived"
         ,direction     = "Output"
      );
      param8.schema.featureTypeRule  = "AsSpecified";
      param8.schema.featureType      = "Simple";
      param8.schema.geometryTypeRule = "AsSpecified";
      param8.schema.geometryType     = "Polygon";
      param8.schema.fieldsRule       = "AllNoFIDs";
      
      param9 = arcpy.Parameter(
          displayName   = str_reached_point_fc
         ,name          = str_reached_point_fc
         ,datatype      = "DEFeatureClass"
         ,parameterType = "Derived"
         ,direction     = "Output"
      );
      param9.schema.featureTypeRule  = "AsSpecified";
      param9.schema.featureType      = "Simple";
      param9.schema.geometryTypeRule = "AsSpecified";
      param9.schema.geometryType     = "Point";
      param9.schema.fieldsRule       = "AllNoFIDs";
      
      param10 = arcpy.Parameter(
          displayName   = str_reached_line_fc
         ,name          = str_reached_line_fc
         ,datatype      = "DEFeatureClass"
         ,parameterType = "Derived"
         ,direction     = "Output"
      );
      param10.schema.featureTypeRule  = "AsSpecified";
      param10.schema.featureType      = "Simple";
      param10.schema.geometryTypeRule = "AsSpecified";
      param10.schema.geometryType     = "Polyline";
      param10.schema.fieldsRule       = "AllNoFIDs";

      param11 = arcpy.Parameter(
          displayName   = str_reached_area_fc
         ,name          = str_reached_area_fc
         ,datatype      = "DEFeatureClass"
         ,parameterType = "Derived"
         ,direction     = "Output"
      );
      param11.schema.featureTypeRule  = "AsSpecified";
      param11.schema.featureType      = "Simple";
      param11.schema.geometryTypeRule = "AsSpecified";
      param11.schema.geometryType     = "Polygon";
      param11.schema.fieldsRule       = "AllNoFIDs";

      param12 = arcpy.Parameter(
          displayName   = str_nav_results_name
         ,name          = str_nav_results_name
         ,datatype      = "DEFeatureClass"
         ,parameterType = "Derived"
         ,direction     = "Output"
      );
      param12.schema.featureTypeRule  = "AsSpecified";
      param12.schema.featureType      = "Simple";
      param12.schema.geometryTypeRule = "AsSpecified";
      param12.schema.geometryType     = "Polyline";
      param12.schema.fieldsRule       = "AllNoFIDs";
      
      param13 = arcpy.Parameter(
          displayName   = str_link_path_name
         ,name          = str_link_path_name
         ,datatype      = "DEFeatureClass"
         ,parameterType = "Derived"
         ,direction     = "Output"
      );
      
      param14 = arcpy.Parameter(
          displayName   = "StatusMessage"
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
      ];

      return params

   def isLicensed(self):
      
      return True;

   def updateParameters(self, parameters):
      
      return True;

   def updateMessages(self, parameters):
      
      return True;

   def execute(self, parameters, messages):
      
      #------------------------------------------------------------------------
      #-- Step 10
      #-- Load variables from form parameters
      #------------------------------------------------------------------------
      num_return_code      = 0;
      str_status_message   = "";

      str_search_type     = search_type(parameters[0].valueAsText);
      str_start_point_fc  = strip_empty(parameters[1].valueAsText);
      str_max_distancekm  = strip_empty(parameters[2].value);
      str_max_flowtimeday = strip_empty(parameters[3].value);
      str_eventtypelist   = to_eventtype(parameters[4].valueAsText);
      str_advanced_config = strip_empty(parameters[5].valueAsText);
      
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
      #-- Sniff for deployment scenario
      #------------------------------------------------------------------------
      if hasattr(__builtin__, "dz_deployer") \
      and __builtin__.dz_deployer is True:
         str_search_type    = "UT";
         str_max_distancekm = "5";
         str_eventtypelist  = "MDSYS.SDO_NUMBER_ARRAY(10011,10032)";
         str_navigation_engine = 'V2';

      #------------------------------------------------------------------------
      #-- Step 40
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
      #-- Step 50
      #-- Unpack feature class
      #------------------------------------------------------------------------
      str_start_wkt_geom = None;
      num_start_srid     = None;
      (
          num_return_code
         ,str_status_message
         ,str_start_wkt_geom
         ,num_start_srid
      ) = unpack_fc(
         str_start_point_fc
      );
       
      #------------------------------------------------------------------------
      #-- Step 60
      #-- Create the service scratch space
      #------------------------------------------------------------------------
      try:
         arcpy.env.overwriteOutput = True;
      
         scratch_full_source_a = arcpy.CreateScratchName(
             str_source_area_fc
            ,""
            ,"FeatureClass"
            ,arcpy.env.scratchGDB
         );
         scratch_path_source_a,scratch_name_source_a = os.path.split(scratch_full_source_a);

         scratch_full_source_l = arcpy.CreateScratchName(
             str_source_line_fc
            ,""
            ,"FeatureClass"
            ,arcpy.env.scratchGDB
         );
         scratch_path_source_l,scratch_name_source_l = os.path.split(scratch_full_source_l);

         scratch_full_source_p = arcpy.CreateScratchName(
             str_source_point_fc
            ,""
            ,"FeatureClass"
            ,arcpy.env.scratchGDB
         );
         scratch_path_source_p,scratch_name_source_p = os.path.split(scratch_full_source_p);
         
         scratch_full_reached_a = arcpy.CreateScratchName(
             str_reached_area_fc
            ,""
            ,"FeatureClass"
            ,arcpy.env.scratchGDB
         );
         scratch_path_reached_a,scratch_name_reached_a = os.path.split(scratch_full_reached_a);

         scratch_full_reached_l = arcpy.CreateScratchName(
             str_reached_line_fc
            ,""
            ,"FeatureClass"
            ,arcpy.env.scratchGDB
         );
         scratch_path_reached_l,scratch_name_reached_l = os.path.split(scratch_full_reached_l);

         scratch_full_reached_p = arcpy.CreateScratchName(
             str_reached_point_fc
            ,""
            ,"FeatureClass"
            ,arcpy.env.scratchGDB
         );
         scratch_path_reached_p,scratch_name_reached_p = os.path.split(scratch_full_reached_p);

         scratch_full_nav = arcpy.CreateScratchName(
             str_nav_results_name
            ,""
            ,"FeatureClass"
            ,arcpy.env.scratchGDB
         );
         scratch_path_nav,scratch_name_nav = os.path.split(scratch_full_nav);
         
         scratch_full_link = arcpy.CreateScratchName(
             str_link_path_name
            ,""
            ,"FeatureClass"
            ,arcpy.env.scratchGDB
         );
         scratch_path_link,scratch_name_link = os.path.split(scratch_full_link);

      except Exception as err:
         arcpy.AddError(err);

      #------------------------------------------------------------------------
      #-- Step 70
      #-- Create the database connection
      #------------------------------------------------------------------------
      if num_return_code == 0:
         try:
            sde_conn_path = arcpy.env.packageWorkspace + "\\ora_rad_ags.sde"
            sde_conn = arcpy.ArcSDESQLExecute(sde_conn_path);

         except:
            try:
               sde_conn_path = sys.path[0] + "\\ora_rad_ags.sde"
               sde_conn = arcpy.ArcSDESQLExecute(sde_conn_path);

            except Exception as err:
               arcpy.AddError(err);

      #------------------------------------------------------------------------
      #-- Step 80
      #-- Generate the transaction id
      #------------------------------------------------------------------------
      if num_return_code == 0:
         str_session_id = '{' + str(uuid.uuid4()) + '}';
         
         sql_statement1 = sqlstatement(
             str_session_id
            ,str_search_type
            ,format_geometry(str_start_wkt_geom,num_start_srid)
            ,format_number(str_max_distancekm)
            ,format_number(str_max_flowtimeday)
            ,str_eventtypelist
            ,str_navigation_engine
         );
         arcpy.AddMessage(sql_statement1);

      #------------------------------------------------------------------------
      #-- Step 90
      #-- Execute the Database Service
      #------------------------------------------------------------------------
      if num_return_code == 0:
         try:
            sde_return = sde_conn.execute(sql_statement1)

         except Exception as err:
            arcpy.AddError("Database Level Error");
            sys.exit(-1);

         (num_return_code,str_status_message) = check_results(sde_conn,str_session_id);

      #------------------------------------------------------------------------
      #-- Step 100
      #-- Push out results from the geodatabase
      #------------------------------------------------------------------------
      arcpy.env.transferDomains = True;
         
      try:
         arcpy.FeatureClassToFeatureClass_conversion(
             sde_conn_path + "\\rad_ags.updn_v4_ldsrcpoints"
            ,arcpy.env.scratchGDB
            ,scratch_name_source_p
            ,"session_id = '" + str_session_id + "'"
         );

         arcpy.FeatureClassToFeatureClass_conversion(
             sde_conn_path + "\\rad_ags.updn_v4_ldsrclines"
            ,arcpy.env.scratchGDB
            ,scratch_name_source_l
            ,"session_id = '" + str_session_id + "'"
         );

         arcpy.FeatureClassToFeatureClass_conversion(
             sde_conn_path + "\\rad_ags.updn_v4_ldsrcareas"
            ,arcpy.env.scratchGDB
            ,scratch_name_source_a
            ,"session_id = '" + str_session_id + "'"
         );
         
         arcpy.FeatureClassToFeatureClass_conversion(
             sde_conn_path + "\\rad_ags.updn_v4_ldradpoints"
            ,arcpy.env.scratchGDB
            ,scratch_name_reached_p
            ,"session_id = '" + str_session_id + "'"
         );

         arcpy.FeatureClassToFeatureClass_conversion(
             sde_conn_path + "\\rad_ags.updn_v4_ldradlines"
            ,arcpy.env.scratchGDB
            ,scratch_name_reached_l
            ,"session_id = '" + str_session_id + "'"
         );

         arcpy.FeatureClassToFeatureClass_conversion(
             sde_conn_path + "\\rad_ags.updn_v4_ldradareas"
            ,arcpy.env.scratchGDB
            ,scratch_name_reached_a
            ,"session_id = '" + str_session_id + "'"
         );
         
      except Exception as err:
         arcpy.AddError(err);
         sys.exit(-1);
      
      try:
      
         if str_navigation_engine == 'V1':
         
            arcpy.FeatureClassToFeatureClass_conversion(
                sde_conn_path + "\\rad_ags.navigation_v1_results"
               ,arcpy.env.scratchGDB
               ,scratch_name_nav
               ,"session_id = '" + str_session_id + "'"
            );
            
         elif str_navigation_engine == 'V2':
         
            arcpy.FeatureClassToFeatureClass_conversion(
                sde_conn_path + "\\rad_ags.navigation_v2_results"
               ,arcpy.env.scratchGDB
               ,scratch_name_nav
               ,"session_id = '" + str_session_id + "'"
            );
            
         elif str_navigation_engine == 'V3':
         
            arcpy.FeatureClassToFeatureClass_conversion(
                sde_conn_path + "\\rad_ags.navigation_v3_results"
               ,arcpy.env.scratchGDB
               ,scratch_name_nav
               ,"session_id = '" + str_session_id + "'"
            );
            
         else:
            raise Exception('err');
         
      except Exception as err:
         arcpy.AddError(err);
         sys.exit(-1);
         
      try:
         arcpy.FeatureClassToFeatureClass_conversion(
             sde_conn_path + "\\rad_ags.indexing_v2_indexingpath"
            ,arcpy.env.scratchGDB
            ,scratch_name_link
            ,"SESSION_ID = '" + str_session_id + "' AND PATHID = 'START'"
         );

      except Exception as err:
         arcpy.AddError(err);
         sys.exit(-1);

      #------------------------------------------------------------------------
      #-- Step 110
      #-- Cough out results
      #------------------------------------------------------------------------
      if num_return_code == 0:
         str_status_message = "Upstream/Downstream v4 Search completed.";

      if str_status_message is None:
         str_status_message = "";
         
      arcpy.SetParameterAsText(6 ,scratch_full_source_p);
      arcpy.SetParameterAsText(7 ,scratch_full_source_l);
      arcpy.SetParameterAsText(8 ,scratch_full_source_a);
      arcpy.SetParameterAsText(9 ,scratch_full_reached_p);
      arcpy.SetParameterAsText(10,scratch_full_reached_l);
      arcpy.SetParameterAsText(11,scratch_full_reached_a);
      arcpy.SetParameterAsText(12,scratch_full_nav);
      arcpy.SetParameterAsText(13,scratch_full_link);
      arcpy.SetParameterAsText(14,str_status_message);

