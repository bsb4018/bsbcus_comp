import os

PIPELINE_NAME = "consumer-complaint"
PIPELINE_ARTIFACT_DIR = os.path.join(os.getcwd(), "consumer_artifact")

from finpred.constant.training_pipeline_constants.data_ingestion import *
from finpred.constant.training_pipeline_constants.data_validation import *
from finpred.constant.training_pipeline_constants.data_transformation import *
from finpred.constant.training_pipeline_constants.model_trainer import *
from finpred.constant.training_pipeline_constants.model_evaluation import *
from finpred.constant.training_pipeline_constants.model_pusher import *












