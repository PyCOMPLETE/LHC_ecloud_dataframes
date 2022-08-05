import numpy as np
import pandas as pd
import sys
import pickle

from collections import UserDict

from LHCMeasurementTools.TimberManager import CalsVariables_from_h5 
import LHCMeasurementTools.TimestampHelpers as TH
import LHCMeasurementTools.LHC_BCT as BCT
import LHCMeasurementTools.LHC_FBCT as FBCT
import LHCMeasurementTools.LHC_Heatloads as HL
import LHCMeasurementTools.LHC_Energy as Energy
import LHCMeasurementTools.LHC_BQM as BQM
import LHCMeasurementTools.LHC_Heatloads as HL
from LHCMeasurementTools.LHC_Fills import Fills_Info
from LHCMeasurementTools.LHC_Fill_LDB_Query import load_fill_dict_from_json
from LHCMeasurementTools.SetOfHomogeneousVariables import SetOfHomogeneousNumericVariables
from data_folders import data_folder_list

from rich.progress import track, Progress
from rich.progress import TextColumn, BarColumn, TimeElapsedColumn, MofNCompleteColumn, TaskProgressColumn, TimeRemainingColumn
from rich.live import Live
from rich.table import Table
from rich.panel import Panel

                                         
from loguru import logger                
logger.remove()                          
logger.add(sys.stdout, colorize=True, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <blue>{level}</blue> | <level>{message}</level>")

class EcloudDataframes(UserDict):
    bunch_intensity_threshold = 0.15e11
    halfcell_length = 53.45

    save = True
    saved_pickle_name = "LHC_ecloud_dataframes_2022.pkl"
    
    bct = {}
    fbct = {}
    bqm_bunchlengths = {}
    blacklist = [7923, 7969, 8033, 8073]

    def __init__(self, dataframe_pickle=None):
        if dataframe_pickle is not None:
            logger.info(f"Loading {dataframe_pickle}")
            self.data = pickle.load(open(dataframe_pickle,'rb'))
        else:
            self.data["stable_beams"] = pd.DataFrame()
        
        self.dict_fill_bmodes = self.get_fill_bmodes()

        #cell by cell heatload variables
        cell_by_cell_lists = [HL.arc_cells_by_sector[key] for key in HL.arc_cells_by_sector.keys()]
        heatload_varlist = [x for xs in cell_by_cell_lists for x in xs]
        # Arc average heatload variables
        self.heatload_varlist = heatload_varlist + HL.heat_loads_plot_sets['AVG_ARC']

        self.fill_dict = {}

	
    def update(self):


        saved_fills = list(self.data["stable_beams"].index)

        fills = list(self.dict_fill_bmodes.keys())
        tag = "stable_beams"
        
        stable_beam_fills = []
        stable_beam_fills_to_process = []
        for fill in fills:
            if fill in self.blacklist: continue
            fill_info = self.dict_fill_bmodes[fill] 
            fill_keys = fill_info.keys()
            if fill_info["flag_complete"] and "t_start_STABLE" in fill_keys:
                stable_beam_fills.append(fill)
                if fill not in saved_fills:
                    stable_beam_fills_to_process.append(fill)

        logger.info(f"{len(self.blacklist)} Blacklisted fills: ")
        self.pretty_print_list(self.blacklist)
        logger.info(f"{len(stable_beam_fills)} fills with stable beams: ")
        self.pretty_print_list(stable_beam_fills)
        logger.info(f"{len(stable_beam_fills_to_process)} of which not in the dataframes: ")
        self.pretty_print_list(stable_beam_fills_to_process)

        for fill in stable_beam_fills_to_process:
            del self.fill_dict ## to delete data from previous fills
            self.fill_dict = {} ## to delete data from previous fills
            fill_info = self.dict_fill_bmodes[fill] 
            logger.info(f"Fill {fill}...")
            df_rows = self.get_fill_dataframe_rows(int(fill))
            self.data[tag] = pd.concat([self.data[tag], df_rows[tag]])
            
            if self.save:
                pickle.dump(self.data, open(self.saved_pickle_name, "wb"))

    def pretty_print_list(self, the_list, chunk_size=10):
        if len(the_list) < chunk_size:
            logger.info(f"{the_list}")
        else:
            for ii in range(0, len(the_list)-chunk_size, chunk_size):
                logger.info(f"{the_list[ii:ii+chunk_size]}")
            logger.info(f"{the_list[ii+chunk_size:]}")

    def get_fill_dataframe_rows(self, fill):
        dataframe_row = {}
        self.update_fill_data(fill)
        tag = "stable_beams"
        dataframe_row[tag] = {}
        t_start = self.dict_fill_bmodes[fill]['t_startfill']
        timestamp = self.dict_fill_bmodes[fill]['t_start_STABLE']
        dataframe_row[tag]["timestamp"] = timestamp
        dataframe_row[tag].update( self.get_beam_data(timestamp) )
        dataframe_row[tag].update( self.get_heatload_data(timestamp) )

        ## from dict to pandas DataFrame
        df_row = dataframe_row[tag]
        df = pd.DataFrame()
        for key in df_row.keys():
            series = pd.Series([df_row[key]], index=[int(fill)])
            df = pd.concat([df, series.rename(key)], axis=1)
        return {tag : df}
         
    def get_beam_data(self, timestamp):
        logger.info("\tExtracting beam data...")
        dataframe_row = {}
        
        for beam in [1,2]:
            ## BCT
            dataframe_row[f"intensity_b{beam}"] = self.bct[beam].nearest_older_sample(timestamp)
        
            ## FBCT bunch intensities
            bunch_intensities = self.fbct[beam].nearest_older_sample(timestamp)
            filled_slots = bunch_intensities > self.bunch_intensity_threshold
            n_bunches = len(bunch_intensities[filled_slots])
  
            dataframe_row[f"n_bunches_b{beam}"] = n_bunches
            dataframe_row[f"bunch_intensity_b{beam}"] = bunch_intensities
            dataframe_row[f"filled_slots_b{beam}"] = filled_slots
            dataframe_row[f"bunch_intensity_b{beam}_mean"] = np.mean(bunch_intensities[filled_slots])
            dataframe_row[f"bunch_intensity_b{beam}_std"] = np.std(bunch_intensities[filled_slots])

            ## BQM bunch lengths
            bunch_lengths = self.bqm_bunchlengths[beam].nearest_older_sample(timestamp)

            dataframe_row[f"bunch_length_b{beam}"] = bunch_lengths
            filled_bunch_lengths = bunch_lengths[filled_slots]
            dataframe_row[f"bunch_length_b{beam}_mean"] = np.mean(filled_bunch_lengths)
            dataframe_row[f"bunch_length_b{beam}_std"] = np.std(filled_bunch_lengths)
            dataframe_row[f"bunch_length_b{beam}_max"] = np.max(filled_bunch_lengths)
            dataframe_row[f"bunch_length_b{beam}_min"] = np.min(filled_bunch_lengths)
            
        return dataframe_row

    def get_heatload_data(self, timestamp):
        logger.info("\tExtracting heat load data...")
        dataframe_row = {}
        
        # Modelled Impedance and Synchrotron Radiation
        impedance_var = self.fill_dict["imp_arc_wm"]
        impedance_var.values = impedance_var.values[0]
        sr_var = self.fill_dict["sr_arc_wm"]
        sr_var.values = sr_var.values[0]
        impedance_hl_per_m = impedance_var.nearest_older_sample(timestamp)
        sr_hl_per_m = sr_var.nearest_older_sample(timestamp)
  
        dataframe_row["impedance_hl_per_m"] = impedance_hl_per_m
        dataframe_row["impedance_hl_halfcell"] = impedance_hl_per_m * self.halfcell_length
        dataframe_row["sr_hl_per_m"] = sr_hl_per_m
        dataframe_row["sr_hl_halfcell"] = sr_hl_per_m * self.halfcell_length
        
        ## Measured heat loads: 1) halfcell by halfcell and 2) averages over halfcells of sectors
        heatloads = SetOfHomogeneousNumericVariables(variable_list=self.heatload_varlist, timber_variables=self.fill_dict)
        for hl_var in heatloads.variable_list:
            timber_var = heatloads.timber_variables[hl_var]
            dataframe_row[hl_var] = timber_var.nearest_older_sample(timestamp)
            
        return dataframe_row

    def get_fill_bmodes(self):
        dict_fill_bmodes = {}
        for df in data_folder_list:
            this_dict_fill_bmodes = load_fill_dict_from_json(
                    df+'/fills_and_bmodes.json')
            for kk in this_dict_fill_bmodes:
                this_dict_fill_bmodes[kk]['data_folder'] = df
            dict_fill_bmodes.update(this_dict_fill_bmodes)
        return dict_fill_bmodes

    def update_fill_data(self, fill):
        logger.info(f"\tLoading data for Fill {fill}...")
        data_folder_fill = self.dict_fill_bmodes[fill]['data_folder']
        self.fill_dict.update(CalsVariables_from_h5(data_folder_fill
            +'/fill_basic_data_h5s/basic_data_fill_%d.h5'%fill))
        self.fill_dict.update(CalsVariables_from_h5(data_folder_fill
            +'/fill_bunchbybunch_data_h5s/bunchbybunch_data_fill_%d.h5'%fill))
        self.fill_dict.update(CalsVariables_from_h5(data_folder_fill +
            '/fill_heatload_data_h5s/heatloads_fill_%d.h5'%fill))
        self.fill_dict.update(CalsVariables_from_h5(data_folder_fill +
            '/heatloads_fill_h5s/imp_and_SR_fill_%d.h5'%fill))
        self.fill_dict.update(CalsVariables_from_h5(data_folder_fill +
            '/fill_cell_by_cell_heatload_data_h5s/cell_by_cell_heatloads_fill_%d.h5'%fill))
        logger.info(f"\tInitializing BCT, FBCT, BQM with LHCMeasurementTools...")
        
        heatloads = SetOfHomogeneousNumericVariables(variable_list=self.heatload_varlist, timber_variables=self.fill_dict)
        for beam in [1,2]:
            self.bct[beam] = BCT.BCT(self.fill_dict, beam=beam)
            self.fbct[beam] = FBCT.FBCT(self.fill_dict, beam=beam)
            self.bqm_bunchlengths[beam] = BQM.blength(self.fill_dict, beam=beam)

        logger.info(f"\tFinished loading.")

       
