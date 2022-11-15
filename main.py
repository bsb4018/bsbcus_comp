
import os,sys
import argparse
from finpred.logger import logger
from finpred.exception import CustomerException
from finpred.configuration.pipeline.training_config import FinanceConfig
from finpred.pipeline.training import TrainingPipeline
from finpred.constant.environment.variable_key import AWS_ACCESS_KEY_ID_ENV_KEY,AWS_SECRET_ACCESS_KEY_ENV_KEY
#from dotenv import load_dotenv
#load_dotenv()
access_key_id = os.getenv(AWS_ACCESS_KEY_ID_ENV_KEY, )
secret_access_key = os.getenv(AWS_SECRET_ACCESS_KEY_ENV_KEY, )


def start_training(start=False):
    try:
        if not start:
            return None
        print("Training Running")
        TrainingPipeline(FinanceConfig()).start()
        
    except Exception as e:
        raise CustomerException(e, sys)

def start_prediction(start=False):
    try:
        pass
    except Exception as e:
        raise CustomerException(e, sys)


def main(training_status, prediction_status):
    try:
        start_training(start=training_status)
        start_prediction(start=prediction_status)
    except Exception as e:
        raise CustomerException(e, sys)

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--t", default=0, type=int, help="If provided true training will be done else not")
        parser.add_argument("--p", default=0, type=int, help="If provided prediction will be done else not")
        
        args = parser.parse_args()

        main(training_status=args.t, prediction_status=args.p)
    except Exception as e:
        print(e)
        logger.exception(CustomerException(e, sys))
