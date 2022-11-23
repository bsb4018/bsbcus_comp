import sys
from finpred.components.training.data_transformation import DataTransformation
from finpred.components.training.data_validation import DataValidation
from finpred.components.training.model_trainer import ModelTrainer
from finpred.exception import CustomerException
from finpred.logger import logger
from finpred.configuration.pipeline.training_config import FinanceConfig
from finpred.components.training.data_ingestion import DataIngestion
from finpred.entity.artifact_entity import DataIngestionArtifact, DataTransformationArtifact, DataValidationArtifact, ModelTrainerArtifact

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

    def start_data_validation(self, data_ingestion_artifact: DataIngestionArtifact) -> DataValidationArtifact:
        try:
            data_validation_config = self.finance_config.get_data_validation_config()
            data_validation = DataValidation(data_ingestion_artifact=data_ingestion_artifact,
                                             data_validation_config=data_validation_config)

            data_validation_artifact = data_validation.initiate_data_validation()
            return data_validation_artifact
        except Exception as e:
            raise CustomerException(e, sys)
    
    def start_data_transformation(self, data_validation_artifact: DataValidationArtifact) -> DataTransformationArtifact:
        try:
            data_transformation_config = self.finance_config.get_data_transformation_config()
            data_transformation = DataTransformation(data_validation_artifact=data_validation_artifact,
                                                     data_transformation_config=data_transformation_config

                                                     )
            data_transformation_artifact = data_transformation.initiate_data_transformation()
            return data_transformation_artifact
        except Exception as e:
            raise CustomerException(e, sys)

    def start_model_trainer(self, data_transformation_artifact: DataTransformationArtifact) -> ModelTrainerArtifact:
        try:
            model_trainer = ModelTrainer(data_transformation_artifact=data_transformation_artifact,
                                         model_trainer_config=self.finance_config.get_model_trainer_config()
                                         )
            model_trainer_artifact = model_trainer.initiate_model_training()
            return model_trainer_artifact
        except Exception as e:
            raise CustomerException(e, sys)

    def start(self):
        try:
            logger.info("Entered 'start_pipeline' method of TrainingPipeline class")
            data_ingestion_artifact = self.start_data_ingestion()
            data_validation_artifact = self.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)
            data_transformation_artifact = self.start_data_transformation(
                data_validation_artifact=data_validation_artifact)
            model_trainer_artifact = self.start_model_trainer(data_transformation_artifact=data_transformation_artifact)

        except Exception as e:
            raise CustomerException(e, sys)





















































































































