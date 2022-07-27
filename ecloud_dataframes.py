import numpy as np
import pandas as pd

import LHCMeasurementTools.TimestampHelpers as TH
import LHCMeasurementTools.LHC_BCT as BCT
import LHCMeasurementTools.LHC_FBCT as FBCT
import LHCMeasurementTools.LHC_Heatloads as HL
import LHCMeasurementTools.LHC_Energy as Energy
import LHCMeasurementTools.LHC_BQM as BQM
from LHCMeasurementTools.LHC_Fills import Fills_Info
from LHCMeasurementTools.LHC_Fill_LDB_Query import load_fill_dict_from_json
from data_folders import data_folder_list


class EcloudDataframes(object):
    bunch_intensity_threshold = 0.15e11

    def __init__(self):
        self.dict_fill_bmodes = self.get_fill_bmodes()
        self.fill_dict = {}

    def get_fill_dataframe_rows(self, filln):
        dataframe_rows = {}
        self.update_fill_data(filln)
        tag = "stable_beams"
        dataframe_rows[tag] = {}
        t_start = self.dict_fill_bmodes[filln]['t_startfill']
        timestamp = t_start + 3600. * 3.
        dataframe_rows[tag]["timestamp"] = timestamp
        dataframe_rows[tag].update( self.get_beam_data(timestamp) )
        return dataframe_rows
         
    def get_beam_data(self, timestamp):
        dataframe_row = {}
        
        for beam in [1,2]:
            ## BCT
            bct = BCT.BCT(self.fill_dict, beam=beam)
            dataframe_row[f"intensity_b{beam}"] = bct.nearest_older_sample(timestamp)
        
            ## FBCT bunch intensities
            fbct = FBCT.FBCT(self.fill_dict, beam=beam)
            bunch_intensities = fbct.nearest_older_sample(timestamp)
            filled_slots = bunch_intensities > self.bunch_intensity_threshold
            n_bunches = len(bunch_intensities[filled_slots])
  
            dataframe_row[f"n_bunches_b{beam}"] = n_bunches
            dataframe_row[f"bunch_intensity_b{beam}"] = bunch_intensities
            dataframe_row[f"filled_slots_b{beam}"] = filled_slots
            dataframe_row[f"bunch_intensity_b{beam}_mean"] = np.mean(bunch_intensities[filled_slots])
            dataframe_row[f"bunch_intensity_b{beam}_std"] = np.std(bunch_intensities[filled_slots])

            ## BQM bunch lengths
            bqm_bunchlengths = BQM.blength(self.fill_dict, beam=beam)
            bunch_lengths = bqm_bunchlengths.nearest_older_sample(timestamp)

            dataframe_row[f"bunch_length_b{beam}"] = bunch_lengths
            dataframe_row[f"bunch_length_b{beam}_mean"] = np.mean(bunch_lengths[filled_slots])
            dataframe_row[f"bunch_length_b{beam}_std"] = np.std(bunch_lengths[filled_slots])
            dataframe_row[f"bunch_length_b{beam}_max"] = np.max(bunch_lengths[filled_slots])
            dataframe_row[f"bunch_length_b{beam}_min"] = np.min(bunch_lengths[filled_slots])
            
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

    def update_fill_data(self, filln):
        from LHCMeasurementTools.TimberManager import CalsVariables_from_h5 
        data_folder_fill = self.dict_fill_bmodes[filln]['data_folder']
        self.fill_dict.update(CalsVariables_from_h5(data_folder_fill
            +'/fill_basic_data_h5s/basic_data_fill_%d.h5'%filln))
        self.fill_dict.update(CalsVariables_from_h5(data_folder_fill
            +'/fill_bunchbybunch_data_h5s/bunchbybunch_data_fill_%d.h5'%filln))
        self.fill_dict.update(CalsVariables_from_h5(data_folder_fill +
            '/fill_heatload_data_h5s/heatloads_fill_%d.h5'%filln))

       
