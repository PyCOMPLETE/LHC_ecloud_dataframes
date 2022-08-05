from ecloud_dataframes import EcloudDataframes, logger
import pickle


ecloud_df = EcloudDataframes(dataframe_pickle="LHC_ecloud_dataframes_2022.pkl")
ecloud_df.update()
logger.info("Finished")

