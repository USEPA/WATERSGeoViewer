import arcpy;
import sys,os;
import uuid;
import builtins;

str_navtype_name       = "StreamSelectionType";
str_delin_results_name = "ResultDelineatedArea";
str_nav_results_name   = "ResultStreamsSelected";
str_catch_results_name = "ResultCatchmentsSelected";
str_link_path_name     = "ResultLinkPath";
str_return_streams     = "ShowSelectedStreams";
str_return_catchments  = "ShowSelectedCatchments";

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

   return "MDSYS.SDO_CS.MAKE_2D(MDSYS.SDO_GEOMETRY('" + input + "'," + str(srid) + "))";

def sqlstatement(session_id,search_type,start_wkt_geom,max_distancekm,max_flowtimeday,nav_results,catch_results):

   return """
      DECLARE
         str_session_id           VARCHAR2(40 Char);
         str_aggregation_flag     VARCHAR2(255 Char);
         int_start_comid          NUMBER(19);
         num_start_measure        NUMBER;
         geom_start_point         MDSYS.SDO_GEOMETRY;
         num_snap_max_km          NUMBER := 15;
         num_fall_max_km          NUMBER := 4;
         int_target_fcode         INTEGER;
         
         ary_flowlines            nhdplus.raindrop_np21.internal_indexed_flowline_list;
         num_path_distance        NUMBER;
         sdo_path_line            MDSYS.SDO_GEOMETRY;
         sdo_end_point            MDSYS.SDO_GEOMETRY;
         int_raindrop_return_code PLS_INTEGER;
         int_return_code          PLS_INTEGER;
         str_status_message       VARCHAR2(256 Char);
      
      BEGIN
         ----------------------------------------------------------------------
         str_session_id       := '""" + session_id      + """';
         str_aggregation_flag := """  + catch_results   + """;
         geom_start_point     := """  + start_wkt_geom  + """;
         ----------------------------------------------------------------------
         INSERT INTO
         nhdplus_delineation.tmp_delineation_status(
             objectid
            ,session_id
            ,session_datestamp
            ,feature_type
            ,aggregation_flag
         ) VALUES (
             nhdplus_delineation.tmp_delineation_status_seq.NEXTVAL
            ,str_session_id
            ,SYSTIMESTAMP
            ,NULL
            ,str_aggregation_flag
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
            UPDATE nhdplus_delineation.tmp_delineation_status a
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
         IF int_raindrop_return_code = -20011
         THEN
            INSERT INTO
            nhdplus_indexing.tmp_pt_indexing_status(
                objectid
               ,session_id
               ,session_datestamp
               ,indexing_line_lengthkm
               ,indexing_line
            ) VALUES (
                nhdplus_indexing.tmp_pt_indexing_status_seq.NEXTVAL
               ,str_session_id
               ,SYSTIMESTAMP
               ,ROUND(num_path_distance,3)
               ,sdo_path_line
            );
            ------------------------------
            UPDATE nhdplus_delineation.tmp_delineation_status a
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
         INSERT INTO
         nhdplus_indexing.tmp_pt_indexing_status(
             objectid
            ,session_id
            ,session_datestamp
            ,indexing_line_lengthkm
            ,indexing_line
         ) VALUES (
             nhdplus_indexing.tmp_pt_indexing_status_seq.NEXTVAL
            ,str_session_id
            ,SYSTIMESTAMP
            ,ROUND(num_path_distance,3)
            ,sdo_path_line
         );
         int_start_comid   := ary_flowlines(1).comid;
         num_start_measure := ary_flowlines(1).snap_measure;
         int_target_fcode  := ary_flowlines(1).fcode;
         ----------------------------------------------------------------------
         INSERT INTO
         nhdplus_navigation.tmp_navigation_status(
            objectid
           ,session_id
           ,session_datestamp
         ) VALUES (
            nhdplus_navigation.tmp_navigation_status_seq.NEXTVAL
           ,str_session_id
           ,SYSTIMESTAMP
         );
         ----------------------------------------------------------------------
         IF int_target_fcode IN (56600)
         THEN
            UPDATE nhdplus_delineation.tmp_delineation_status a
            SET
             return_code    = -56600
            ,status_message = 'Unable to navigate further on the NHDPlus network from a coastal flowline.'
            WHERE
            a.session_id = str_session_id;
            ------------------------------
            RETURN;
            ------------------------------
         END IF;
         ----------------------------------------------------------------------
         nhdplus_delineation.delineation.basin_delineator(
             p_search_type                 => '""" + search_type  + """'
            ,p_start_nhdplusid             => int_start_comid
            ,p_start_permanent_identifier  => NULL
            ,p_start_reachcode             => NULL
            ,p_start_hydrosequence         => NULL
            ,p_start_measure               => num_start_measure
            ,p_stop_nhdplusid              => NULL
            ,p_stop_permanent_identifier   => NULL
            ,p_stop_reachcode              => NULL
            ,p_stop_hydrosequence          => NULL
            ,p_stop_measure                => NULL
            ,p_max_distancekm              => """  + max_distancekm   + """
            ,p_max_flowtimeday             => """  + max_flowtimeday  + """
            ,p_feature_type                => 'CATCHMENTSP'
            ,p_output_flag                 => """ + nav_results + """
            ,p_aggregation_flag            => str_aggregation_flag
            ,p_split_initial_catchment     => 'FALSE'
            ,p_fill_drainage_area_holes    => 'TRUE'
            ,p_flowline_lists              => NULL
            ,p_force_nocache               => NULL
            ,out_return_code               => int_return_code
            ,out_status_message            => str_status_message
            ,p_sessionid                   => str_session_id
         );
         ----------------------------------------------------------------------
         UPDATE nhdplus_delineation.tmp_delineation_status a
         SET
          return_code    = int_return_code
         ,status_message = str_status_message
         WHERE
         a.session_id = str_session_id;
         ----------------------------------------------------------------------
         UPDATE nhdplus_delineation.tmp_catchments a
         SET
         areasqkm = ROUND(areasqkm,3)
         WHERE
             a.areasqkm IS NOT NULL
         AND a.session_id = str_session_id;
         -------------------------------------------------------------------
         UPDATE nhdplus_navigation.tmp_navigation_results a
         SET
          lengthkm = ROUND(lengthkm,3)
         ,network_distancekm = ROUND(network_distancekm,3)
         WHERE
             a.lengthkm IS NOT NULL
         AND a.session_id = str_session_id;
         ----------------------------------------------------------------------
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
      rad_ags.delineation_v3_status a
      WHERE
      a.session_id = '""" + session_id + """'
   """;
   
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
   """
   {
       "Index Methodology": "RAINDROP_FALLBACK"
      ,"Split Catchment": True
      ,"Raindrop Snap Max Distance": 2      
   }  
   """
   
   input_point       = None;
   
   #-- DISTANCE
   #-- RAINDROP
   #-- RAINDROP_FALLBACK
   #-- CATCONSTRAINED
   index_methodology = None;
   
   split_catchment   = None;
   
   raindrop_snap_max_dist_km = None;
   raindrop_dist_max_dist_km = None;
   fallback_dist_max_dist_km = None;
   
   fcode_allow     = None;
   fcode_deny      = None;
   limit_innetwork = None;
   limit_navigable = None;
   
   return (
       index_methodology
      ,split_catchment
      ,raindrop_snap_max_dist_km
      ,raindrop_dist_max_dist_km
      ,fallback_dist_max_dist_km
      ,fcode_allow
      ,fcode_deny
      ,limit_innetwork
      ,limit_navigable
   );

class Toolbox(object):

   def __init__(self):
      self.label = "Toolbox";
      self.alias = "";

      # List of tool classes associated with this toolbox
      self.tools = [
          DelineateUsingStartingPoint
      ];

class DelineateUsingStartingPoint(object):

   def __init__(self):
      self.label = "DelineateUsingStartingPoint"
      self.name  = "DelineateUsingStartingPoint"
      self.description = "The EPA Office of Water Watershed Delineation Service provides an areal representation of the " + \
         "navigation process by linking navigated flowlines to associated areal geographies. " + \
         "The service has been optimized to aggregate and return NHDPlus catchments. " + \
         "For more information see " +  \
         "<a href='https://www.epa.gov/waterdata/navigation-delineation-service' target='_blank'>" + \
         "EPA service documentation</a>.";
      self.canRunInBackground = False;

   def getParameterInfo(self):
      param0 = arcpy.Parameter(
          displayName   = str_navtype_name
         ,name          = str_navtype_name
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
          displayName   = str_return_streams
         ,name          = str_return_streams
         ,datatype      = "GPBoolean"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );
      param4.value = False;

      param5 = arcpy.Parameter(
          displayName   = str_return_catchments
         ,name          = str_return_catchments
         ,datatype      = "GPBoolean"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );
      param5.value = False;
      
      param6 = arcpy.Parameter(
          displayName   = "AdvancedConfiguration"
         ,name          = "AdvancedConfiguration"
         ,datatype      = "String"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = True
      );

      param7 = arcpy.Parameter(
          displayName   = str_delin_results_name
         ,name          = str_delin_results_name
         ,datatype      = "DEFeatureClass"
         ,parameterType = "Derived"
         ,direction     = "Output"
      );

      param8 = arcpy.Parameter(
          displayName   = str_nav_results_name
         ,name          = str_nav_results_name
         ,datatype      = "DEFeatureClass"
         ,parameterType = "Derived"
         ,direction     = "Output"
      );
      
      param9 = arcpy.Parameter(
          displayName   = str_catch_results_name
         ,name          = str_catch_results_name
         ,datatype      = "DEFeatureClass"
         ,parameterType = "Derived"
         ,direction     = "Output"
      );
      
      param10 = arcpy.Parameter(
          displayName   = str_link_path_name
         ,name          = str_link_path_name
         ,datatype      = "DEFeatureClass"
         ,parameterType = "Derived"
         ,direction     = "Output"
      );
      
      param11 = arcpy.Parameter(
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
      num_return_code     = 0;
      str_status_message  = "";
      
      str_default_snap    = "RAINDROP";

      str_search_type     = search_type(parameters[0].valueAsText);
      str_start_point_fc  = strip_empty(parameters[1].valueAsText);
      str_max_distancekm  = strip_empty(parameters[2].value);
      str_max_flowtimeday = strip_empty(parameters[3].value);
      boo_nav_results     = get_boo(parameters[4].valueAsText);
      boo_catch_results   = get_boo(parameters[5].valueAsText);
      str_advanced_config = strip_empty(parameters[6].valueAsText);
      
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
      if hasattr(builtins, "dz_deployer") \
      and builtins.dz_deployer is True:
         str_search_type     = "UT";
         str_max_distancekm  = "5";
         str_advanced_config = None;

      #------------------------------------------------------------------------
      #-- Step 40
      #-- Do error checking
      #------------------------------------------------------------------------
      if str_search_type is None or str_search_type not in ["UT","UM","DD","DM","PP"]:
         num_return_code = -20;
         str_status_message += "Invalid search type. ";

      if str_start_point_fc is None:
         num_return_code = -20;
         str_status_message += "Start point is required for all search. ";

      if str_max_distancekm is not None:
         boo_bad = False;
         try:
            num_val = float(str_max_distancekm);
         except ValueError:
            boo_bad = True;

         if boo_bad or num_val < 0:
            num_return_code = -10;
            str_status_message += "Maximum distance must be a numeric value of zero or greater.  Or use keyword \"Complete\" for the complete delineation. ";

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
      #-- Unpack feature class
      #------------------------------------------------------------------------
      str_start_wkt_geom = None;
      num_start_srid     = None;
      (
          num_rc
         ,str_sm
         ,str_start_wkt_geom
         ,num_start_srid
      ) = unpack_fc(
          str_start_point_fc
      );
      
      if num_rc != 0:
         num_return_code = num_rc;
         str_status_message += str_sm + " ";

      #------------------------------------------------------------------------
      #-- Step 60
      #-- Create the service scratch space
      #------------------------------------------------------------------------
      try:
         arcpy.env.overwriteOutput = True;
         
         scratch_full_delin = arcpy.CreateScratchName(
             str_delin_results_name + "1Z"
            ,""
            ,"FeatureClass"
            ,arcpy.env.scratchGDB
         );
         scratch_path_delin,scratch_name_delin = os.path.split(scratch_full_delin);

         scratch_full_fl = arcpy.CreateScratchName(
             str_nav_results_name + "1Z"
            ,""
            ,"FeatureClass"
            ,arcpy.env.scratchGDB
         );
         scratch_path_fl,scratch_name_fl = os.path.split(scratch_full_fl);
         
         scratch_full_catch = arcpy.CreateScratchName(
             str_catch_results_name + "1Z"
            ,""
            ,"FeatureClass"
            ,arcpy.env.scratchGDB
         );
         scratch_path_catch,scratch_name_catch = os.path.split(scratch_full_catch);
         
         scratch_full_link = arcpy.CreateScratchName(
             str_link_path_name + "1Z"
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

         if boo_nav_results:
            str_nav_results = "'BOTH'";
         else:
            str_nav_results = "'FEATURE'";
            
         if boo_catch_results:
            str_catch_results = "'BOTH'";
         else:
            str_catch_results = "'TRUE'";

         sql_statement1 = sqlstatement(
             str_session_id
            ,str_search_type
            ,format_geometry(str_start_wkt_geom,num_start_srid)
            ,format_number(str_max_distancekm)
            ,format_number(str_max_flowtimeday)
            ,str_nav_results
            ,str_catch_results
         );
         #arcpy.AddMessage(sql_statement1);

      #------------------------------------------------------------------------
      #-- Step 90
      #-- Execute the Database Service
      #------------------------------------------------------------------------
      if num_return_code == 0:
         try:
            sde_return = sde_conn.execute(sql_statement1)
            
         except Exception as err:
            arcpy.AddError(err);
            sys.exit(-1);
            
         (num_return_code,str_status_message) = check_results(sde_conn,str_session_id);

      #------------------------------------------------------------------------
      #-- Step 100
      #-- Push out results from the geodatabase
      #------------------------------------------------------------------------
      try:
         arcpy.FeatureClassToFeatureClass_conversion(
             sde_conn_path + "\\rad_ags.delineation_v3_catchments"
            ,arcpy.env.scratchGDB
            ,scratch_name_delin
            ,"SESSION_ID = '" + str_session_id + "' AND SOURCEFC = 'AGGR'"
         );

      except Exception as err:
         arcpy.AddError(err);
         sys.exit(-1);

      if boo_nav_results:
         str_nav_clause = "SESSION_ID = '" + str_session_id + "'";
      else:
         str_nav_clause = "1=2";

      try:
         arcpy.FeatureClassToFeatureClass_conversion(
             sde_conn_path + "\\rad_ags.navigation_v1_results"
            ,arcpy.env.scratchGDB
            ,scratch_name_fl
            ,str_nav_clause
         );

      except Exception as err:
         arcpy.AddError(err);
         sys.exit(-1);
         
      if boo_catch_results:
         str_catch_clause = "SESSION_ID = '" + str_session_id + "' AND SOURCEFC <> 'AGGR'";
      else:
         str_catch_clause = "1=2";
         
      try:
         arcpy.FeatureClassToFeatureClass_conversion(
             sde_conn_path + "\\rad_ags.delineation_v3_catchments"
            ,arcpy.env.scratchGDB
            ,scratch_name_catch
            ,str_catch_clause
         );

      except Exception as err:
         arcpy.AddError(err);
         sys.exit(-1);
         
      try:
         arcpy.FeatureClassToFeatureClass_conversion(
             sde_conn_path + "\\rad_ags.indexing_v2_indexingpath"
            ,arcpy.env.scratchGDB
            ,scratch_name_link
            ,"SESSION_ID = '" + str_session_id + "'"
         );

      except Exception as err:
         arcpy.AddError(err);
         sys.exit(-1);

      #------------------------------------------------------------------------
      #-- Step 110
      #-- Cough out results
      #------------------------------------------------------------------------
      if num_return_code == 0:
         str_status_message = "Drainage Area Delineation completed.";

      if str_status_message is None:
         str_status_message = "";
         
      arcpy.SetParameterAsText(7,scratch_full_delin);
      arcpy.SetParameterAsText(8,scratch_full_fl);
      arcpy.SetParameterAsText(9,scratch_full_catch);
      arcpy.SetParameterAsText(10,scratch_full_link)
      arcpy.SetParameterAsText(11,str_status_message);
