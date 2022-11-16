import sys
from finpred.exception import CustomerException
from finpred.logger import logger
from finpred.configuration.pipeline.training_config import FinanceConfig
from finpred.components.training.data_ingestion import DataIngestion
from finpred.entity.artifact_entity import DataIngestionArtifact


class TrainingPipeline:
    def __init__(self, finance_config: FinanceConfig):
        self.finance_config = finance_config

    def start_data_ingestion(self) -> DataIngestionArtifact:
        try:
            logger.info("Entered 'start_data_ingestion' method of TrainingPipeline class")

            data_ingestion_config = self.finance_config.get_data_ingestion_config()
            data_ingestion = DataIngestion(data_ingestion_config = data_ingestion_config)
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()

            logger.info("Exiting 'start_data_ingestion' method of TrainingPipeline class")
            return data_ingestion_artifact
        except Exception as e:
            raise CustomerException(e,sys)

    def start(self):
        try:
            logger.info("Entered 'start_pipeline' method of TrainingPipeline class")
            data_ingestion_artifact = self.start_data_ingestion()
            
        except Exception as e:
            raise CustomerException(e, sys)





















































































































