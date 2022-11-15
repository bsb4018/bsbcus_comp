import os

PIPELINE_NAME = "consumer-complaint"
PIPELINE_ARTIFACT_DIR = os.path.join(os.getcwd(), "consumer_artifact")

from finpred.constant.training_pipeline_constants.data_ingestion import *
