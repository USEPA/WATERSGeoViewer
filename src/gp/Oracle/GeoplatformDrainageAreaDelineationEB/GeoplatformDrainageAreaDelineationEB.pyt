import arcpy;
import sys,os,uuid,json;

class Toolbox(object):

   def __init__(self):
      self.label = "Geoplatform Drainage Area Delineation";
      self.alias = "";

      self.tools = [
          DelineateUsingStartingPoint
      ];

class DelineateUsingStartingPoint(object):

   def __init__(self):
      self.label = "Delineate Using Starting Point"
      self.name  = "DelineateUsingStartingPoint"
      self.description = "The EPA Office of Water Watershed Delineation Service provides an areal representation of the " + \
         "navigation process by linking navigated flowlines to associated catchment geographies. " + \
         "For more information see " +  \
         "<a href='https://watersgeo.epa.gov/openapi/waters/#/Delineation/x131' target='_blank'>" + \
         "EPA service documentation</a>.";
      self.canRunInBackground = False;

   def getParameterInfo(self):
      
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
          displayName   = "Show Selected Streams"
         ,name          = "ShowSelectedStreams"
         ,datatype      = "GPBoolean"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );
      param4.value = False;

      param5 = arcpy.Parameter(
          displayName   = "Show Selected Catchments"
         ,name          = "ShowSelectedCatchments"
         ,datatype      = "GPBoolean"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );
      param5.value = False;
      
      param6 = arcpy.Parameter(
          displayName   = "Advanced Configuration"
         ,name          = "AdvancedConfiguration"
         ,datatype      = "String"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = True
      );

      param7 = arcpy.Parameter(
          displayName   = "Result Delineated Area"
         ,name          = "ResultDelineatedArea"
         ,datatype      = ["DEFeatureClass","GPString"]
         ,parameterType = "Derived"
         ,direction     = "Output"
      );

      param8 = arcpy.Parameter(
          displayName   = "Result Streams Selected"
         ,name          = "ResultStreamsSelected"
         ,datatype      = ["DEFeatureClass","GPString"]
         ,parameterType = "Derived"
         ,direction     = "Output"
      );
      
      param9 = arcpy.Parameter(
          displayName   = "Result Catchments Selected"
         ,name          = "ResultCatchmentsSelected"
         ,datatype      = ["DEFeatureClass","GPString"]
         ,parameterType = "Derived"
         ,direction     = "Output"
      );
      
      param10 = arcpy.Parameter(
          displayName   = "Result Link Path"
         ,name          = "ResultLinkPath"
         ,datatype      = ["DEFeatureClass","GPString"]
         ,parameterType = "Derived"
         ,direction     = "Output"
      );
      
      param11 = arcpy.Parameter(
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
      ];

      return params;

   def isLicensed(self):
      return True;

   def updateParameters(self,parameters):
      return True;

   def updateMessages(self,parameters):
      return True;

   def execute(self,parameters,messages):
      
      # The Esri geoprocessing publishing process is mysterious and convoluted whereby the receiving server sniffs the code for data sources 
	   # registered to the server data store.  If a match is made the server copies its own .sde file into the unpacked project directory 
	   # updating pointers as it sees fit.  It is VERY easy to confuse the logic.  If you wish to publish this tool to ArcGIS server, 
	   # I’ve found the best approach is to hard-code your .sde file location here.  Providing it unambiguously upfront seems the best way to 
	   # make the publishing process happy.  If just using the tool locally in ArcGIS Pro desktop, one can ignore this pointer.  The code does  
	   # check for the .sde file here first but will fall back the script location if not found.
      
      sde_connection = r"D:\Public\Data\pdziemie\github\WATERSGeoViewer\src\gp\Oracle\GeoplatformDrainageAreaDelineationEB\ora_rad_ags.sde";
      
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
            return "PP";
         elif val == "":
            return None;
         return val;
   
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
      str_start_geom      = None;
      
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
      if str_search_type is None \
      or str_search_type not in ["UT","UM","DD","DM","PP"]:
         num_return_code = -20;
         str_status_message += "Invalid search type. ";

      if str_start_point_fc is None:
         if str_start_point_fc in [""," "]:
            num_return_code = -20;
            str_status_message += "Start point is required for all search.  ArcGIS Experience Builder widgets often falsely respond as if a start point has been selected.  Try unselecting and reselecting your start point and try again. ";
            
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
      #-- Unpack feature class into GeoJSON
      #------------------------------------------------------------------------
      desc           = arcpy.Describe(str_start_point_fc);
      sr             = desc.spatialReference;
      num_start_srid = sr.factoryCode;
      
      rows = [row for row in arcpy.da.SearchCursor(str_start_point_fc,["SHAPE@"])];
      if rows is None or len(rows) == 0:
         num_return_code = -30;
         str_status_message += "No geometry found in start point feature class. ";

      else:
         geom = rows[-1][0];
         
         if geom.type != "point":
            geom = arcpy.PointGeometry(geom.trueCentroid);
            
         if num_start_srid != 4269:
            geom = geom.projectAs(arcpy.SpatialReference(4269));

         obj_esrijson = json.loads(geom.JSON);
         num_long = obj_esrijson["x"];
         num_lat  = obj_esrijson["y"];
         
         arcpy.AddMessage(". using start location " + str(num_long) + ", " + str(num_lat) + ".");
         
      #------------------------------------------------------------------------
      #-- Step 60
      #-- Create the service scratch space
      #------------------------------------------------------------------------
      scratch_full_delin = arcpy.CreateUniqueName(
          base_name = "ResultDelineatedArea"
         ,workspace = arcpy.env.scratchGDB
      );
      arcpy.management.CreateFeatureclass(
          out_path          = os.path.dirname(scratch_full_delin)
         ,out_name          = os.path.basename(scratch_full_delin)
         ,geometry_type     = "POLYGON"
         ,has_m             = "DISABLED"
         ,has_z             = "DISABLED"
         ,spatial_reference = arcpy.SpatialReference(3857)
         ,out_alias         = "Result Delineated Area"
         ,oid_type          = "32_BIT"
      );
      arcpy.management.AddFields(
          in_table          = scratch_full_delin
         ,field_description = [
             ['nhdplusid'           ,'DOUBLE','NHDPlusID'                  ,None,None,None]
            ,['sourcefc'            ,'TEXT'  ,'SourceFC'                   ,20  ,None,None]
            ,['hydroseq'            ,'DOUBLE','HydroSeq'                   ,None,None,None]
            ,['areasqkm'            ,'DOUBLE','Area (SqKm)'                ,None,None,None]
          ]
      );

      #------------------------------------------------------------------------
      scratch_full_fl = arcpy.CreateUniqueName(
          base_name = "ResultStreamsSelected"
         ,workspace = arcpy.env.scratchGDB
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
      scratch_full_catch = arcpy.CreateUniqueName(
          base_name = "ResultCatchmentsSelected"
         ,workspace = arcpy.env.scratchGDB
      );
      arcpy.management.CreateFeatureclass(
          out_path          = os.path.dirname(scratch_full_catch)
         ,out_name          = os.path.basename(scratch_full_catch)
         ,geometry_type     = "POLYGON"
         ,has_m             = "DISABLED"
         ,has_z             = "DISABLED"
         ,spatial_reference = arcpy.SpatialReference(3857)
         ,out_alias         = "Result Catchments Selected"
         ,oid_type          = "32_BIT"
      );
      arcpy.management.AddFields(
          in_table          = scratch_full_catch
         ,field_description = [
             ['nhdplusid'           ,'DOUBLE','NHDPlusID'                  ,None,None,None]
            ,['sourcefc'            ,'TEXT'  ,'SourceFC'                   ,20  ,None,None]
            ,['hydroseq'            ,'DOUBLE','HydroSeq'                   ,None,None,None]
            ,['areasqkm'            ,'DOUBLE','Area (SqKm)'                ,None,None,None]
          ]
      );
      
      #------------------------------------------------------------------------
      scratch_full_link = arcpy.CreateUniqueName(
          base_name = "ResultLinkPath"
         ,workspace = arcpy.env.scratchGDB
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

      arcpy.AddMessage(". output feature classes created.");

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

         if boo_nav_results:
            str_nav_results = "BOTH";
         else:
            str_nav_results = "FEATURE";
            
         if boo_catch_results:
            str_catch_results = "BOTH";
         else:
            str_catch_results = "TRUE";

         sql_statement1 = """
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
               str_session_id       := """ + format_string(str_session_id)     + """;
               str_aggregation_flag := """  + format_string(str_catch_results) + """;
               geom_start_point     := MDSYS.SDO_CS.MAKE_2D(
                  MDSYS.SDO_GEOMETRY(2001,4269,MDSYS.SDO_POINT_TYPE(""" + str(num_long) + """,""" + str(num_lat) + """,NULL),NULL,NULL)
               ); 
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
                   p_search_type                 => '""" + str_search_type  + """'
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
                  ,p_max_distancekm              => """  + format_number(str_max_distancekm)   + """
                  ,p_max_flowtimeday             => """  + format_number(str_max_flowtimeday)  + """
                  ,p_feature_type                => 'CATCHMENT'
                  ,p_output_flag                 => """ + format_string(str_nav_results) + """
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
         #arcpy.AddMessage(sql_statement1);

      #------------------------------------------------------------------------
      #-- Step 90
      #-- Execute the Database Service
      #------------------------------------------------------------------------
      if num_return_code == 0:
         
         sde_return = sde_conn.execute(sql_statement1)
         arcpy.AddMessage(". delineation service complete.");

         sql_statement = """
            SELECT
             a.return_code
            ,a.status_message
            FROM
            nhdplus_delineation.tmp_delineation_status a
            WHERE
            a.session_id = '""" + str_session_id + """'
         """;
         
         sde_return = sde_conn.execute(sql_statement);

         if sde_return[0][0] != 0:
            num_return_code = sde_return[0][0];
            str_status_message = sde_return[0][1];
            
         arcpy.AddMessage(". delineation return code " + str(num_return_code) + ".");

      #------------------------------------------------------------------------
      #-- Step 100
      #-- Push out results from the geodatabase
      #------------------------------------------------------------------------
      if num_return_code == 0:
         
         with arcpy.da.InsertCursor(
             in_table     = scratch_full_delin
            ,field_names  = [
                'nhdplusid'
               ,'sourcefc'
               ,'hydroseq'
               ,'areasqkm'
               ,'SHAPE@'
             ]
         ) as icursor:
            
            with arcpy.da.SearchCursor(
                in_table     = sde_conn_path + "\\rad_ags.delineation_v3_catchments"
               ,field_names  = [
                   'FEATUREID'
                  ,'SOURCEFC'
                  ,'HYDROSEQ'
                  ,'AREASQKM'
                  ,'SHAPE@'
                ]
               ,where_clause = "SESSION_ID = '" + str_session_id + "' AND SOURCEFC = 'AGGR'"
            ) as scursor:
         
               for row in scursor:
                  icursor.insertRow(row);
                  
         arcpy.SetParameterAsText(7 ,scratch_full_delin);
         
      else:
         arcpy.SetParameterAsText(7 ,"");
                  
      #------------------------------------------------------------------------
      if num_return_code == 0:
         
         if boo_nav_results:
            
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
                     
            arcpy.SetParameterAsText(8 ,scratch_full_fl);
         
         else:
            arcpy.SetParameterAsText(8 ,"");
         
      else:
         arcpy.SetParameterAsText(8 ,"");
         
      #------------------------------------------------------------------------
      if num_return_code == 0:
         
         if boo_catch_results:
            
            with arcpy.da.InsertCursor(
                in_table     = scratch_full_catch
               ,field_names  = [
                   'nhdplusid'
                  ,'sourcefc'
                  ,'hydroseq'
                  ,'areasqkm'
                  ,'SHAPE@'
                ]
            ) as icursor:
               
               with arcpy.da.SearchCursor(
                   in_table     = sde_conn_path + "\\rad_ags.delineation_v3_catchments"
                  ,field_names  = [
                      'FEATUREID'
                     ,'SOURCEFC'
                     ,'HYDROSEQ'
                     ,'AREASQKM'
                     ,'SHAPE@'
                   ]
                  ,where_clause = "SESSION_ID = '" + str_session_id + "' AND SOURCEFC <> 'AGGR'"
               ) as scursor:
            
                  for row in scursor:
                     icursor.insertRow(row);
                     
            arcpy.SetParameterAsText(9 ,scratch_full_catch);
            
         else:
            arcpy.SetParameterAsText(9 ,"");
            
      else:
         arcpy.SetParameterAsText(9 ,"");
         
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
                  
         arcpy.SetParameterAsText(10,scratch_full_link);
         
      else:
         arcpy.SetParameterAsText(10 ,"");

      #------------------------------------------------------------------------
      #-- Step 110
      #-- Cough out results
      #------------------------------------------------------------------------
      if num_return_code == 0:
         str_status_message = "Drainage Area Delineation completed.";

      if str_status_message is None:
         str_status_message = "";

      arcpy.SetParameterAsText(11,str_status_message);

###############################################################################
def format_string(input):

   if input is None:
      return "NULL";

   input = input.replace("'","''");

   return "'" + input + "'";

###############################################################################
def format_number(input):

   if input is None:
      return "NULL";

   return str(input);