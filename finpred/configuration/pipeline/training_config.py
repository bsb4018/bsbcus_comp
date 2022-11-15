from finpred.logger import logger
from finpred.exception import CustomerException
import os, sys
from datetime import datetime
from finpred.entity.config_entity import TrainingPipelineConfig, DataIngestionConfig
from finpred.constant import TIMESTAMP
from finpred.constant.training_pipeline_constants import *
from finpred.entity.metadata_entity import DataIngestionMetadata

class FinanceConfig:
    def __init__(self, pipeline_name = PIPELINE_NAME, timestamp = TIMESTAMP):
        self.timestamp = timestamp
        self.pipeline_name = pipeline_name
        self.pipeline_config = self.get_pipeline_config()

    def get_pipeline_config(self) -> TrainingPipelineConfig:
        try:
            artifact_dir = PIPELINE_ARTIFACT_DIR
            pipeline_config = TrainingPipelineConfig(pipeline_name=self.pipeline_name,
                                                     artifact_dir=artifact_dir)
            logger.info(f"Pipeline configuration: {pipeline_config}")
            return pipeline_config
        except Exception as e:
            raise CustomerException(e, sys)

    def get_data_ingestion_config(self, from_date=DATA_INGESTION_MIN_START_DATE, to_date=None) -> DataIngestionConfig:
        try:
            min_start_date = datetime.strptime(DATA_INGESTION_MIN_START_DATE, "%Y-%m-%d")
            from_date_obj = datetime.strptime(from_date, "%Y-%m-%d")
            if from_date_obj < min_start_date:
                from_date = DATA_INGESTION_MIN_START_DATE
            if to_date is None:
                to_date = datetime.now().strftime("%Y-%m-%d")

            """
            master directory for data ingestion
            we will store metadata information and ingested file to avoid redundant download
            """

            data_ingestion_master_dir = os.path.join(self.pipeline_config.artifact_dir,
                                                     DATA_INGESTION_DIR)
        
            # time based directory for each run
            data_ingestion_dir = os.path.join(data_ingestion_master_dir,
                                          self.timestamp)
            metadata_file_path = os.path.join(data_ingestion_master_dir, DATA_INGESTION_METADATA_FILE_NAME)

            data_ingestion_metadata = DataIngestionMetadata(metadata_file_path=metadata_file_path)

            if data_ingestion_metadata.is_metadata_file_present:
                metadata_info = data_ingestion_metadata.get_metadata_info()
                from_date = metadata_info.to_date

            data_ingestion_config = DataIngestionConfig(
                from_date=from_date,
                to_date=to_date,
                data_ingestion_dir=data_ingestion_dir,
                download_dir=os.path.join(data_ingestion_dir, DATA_INGESTION_DOWNLOADED_DATA_DIR),
                file_name=DATA_INGESTION_FILE_NAME,
                feature_store_dir=os.path.join(data_ingestion_master_dir, DATA_INGESTION_FEATURE_STORE_DIR),
                failed_dir=os.path.join(data_ingestion_dir, DATA_INGESTION_FAILED_DIR),
                metadata_file_path=metadata_file_path,
                datasource_url=DATA_INGESTION_DATA_SOURCE_URL)

            logger.info(f"Data ingestion config: {data_ingestion_config}")
            return data_ingestion_config
        except Exception as e:
            raise CustomerException(e, sys)