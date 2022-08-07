from ecloud_dataframes import EcloudDataframes, logger
import pickle
import os

filename = "LHC_ecloud_dataframes_2022.pkl"
if os.path.exists(filename):
    ecloud_df = EcloudDataframes(dataframe_pickle=filename)
else:
    ecloud_df = EcloudDataframes(dataframe_pickle=None)

ecloud_df.update()
logger.info("Finished")

