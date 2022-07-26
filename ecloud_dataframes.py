import numpy as np
import pandas as pd

import LHCMeasurementTools.TimberManager as tm
import LHCMeasurementTools.TimestampHelpers as TH
import LHCMeasurementTools.LHC_BCT as BCT
import LHCMeasurementTools.LHC_Heatloads as HL
import LHCMeasurementTools.LHC_Energy as Energy
from LHCMeasurementTools.LHC_Fills import Fills_Info
from LHCMeasurementTools.LHC_Fill_LDB_Query import load_fill_dict_from_json
from data_folders import data_folder_list


class EcloudDataframes(object):
    def __init__(self):
        self.dict_fill_bmodes = self.get_fill_bmodes()
        self.fill_dict = {}

    def get_fill_dataframes(self, filln):
        self.update_fill_data(filln)
        t_start = self.dict_fill_bmodes[filln]['t_startfill']
        timestamp = t_start * 3600.
        self.get_basic_data(timestamp)
         
    def get_basic_data(self, timestamp):
        df_row = {}
        BCT1 = BCT.BCT(self.fill_dict, beam=1)
        BCT2 = BCT.BCT(self.fill_dict, beam=2)
        print(BCT1.nearest_older_sample(timestamp))
        print(BCT2.nearest_older_sample(timestamp))
        

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
        data_folder_fill = self.dict_fill_bmodes[filln]['data_folder']
        self.fill_dict.update(tm.CalsVariables_from_h5(data_folder_fill
            +'/fill_basic_data_h5s/basic_data_fill_%d.h5'%filln,
            ))
        self.fill_dict.update(tm.CalsVariables_from_h5(data_folder_fill
            +'/fill_bunchbybunch_data_h5s/bunchbybunch_data_fill_%d.h5'%filln))
        self.fill_dict.update(tm.CalsVariables_from_h5(data_folder_fill +
            '/fill_heatload_data_h5s/heatloads_fill_%d.h5'%filln))

       
