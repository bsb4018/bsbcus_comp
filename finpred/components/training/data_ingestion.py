import os, re, sys, time, uuid
from collections import namedtuple
from typing import List
import json
import requests
import pandas as pd
from datetime import datetime
from finpred.exception import CustomerException
from finpred.logger import logger

from finpred.entity.config_entity import DataIngestionConfig
from finpred.configuration.pipeline.training_config import FinanceConfig
from finpred.exception import CustomerException
from finpred.entity.artifact_entity import DataIngestionArtifact
from finpred.entity.metadata_entity import DataIngestionMetadata

from finpred.configuration.spark_manager import spark_session
DownloadUrl = namedtuple("DownloadUrl", ["url", "file_path", "n_retry"])

class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig, n_retry: int = 5):
        try:
            logger.info(f"{'>>' * 20} Starting data ingestion. {'<<' *20}")
            self.data_ingestion_config = data_ingestion_config
            self.failed_download_urls: List[DownloadUrl] =[]
            self.n_retry = n_retry
        except Exception as e:
            raise CustomerException(e, sys)

    def get_required_interval(self):
        try:
            start_date = datetime.strptime(self.data_ingestion_config.from_date, "%Y-%m-%d")
            end_date = datetime.strptime(self.data_ingestion_config.to_date, "%Y-%m-%d")
            n_diff_days = (end_date - start_date).days
            freq = None
            if n_diff_days > 365:
                freq = "Y"
            elif n_diff_days > 30:
                freq = "M"
            elif n_diff_days > 7:
                freq = "W"
            
            logger.debug(f"{n_diff_days} hence freq: {freq}")
            if freq is None:
                intervals = pd.date_range(
                    start = self.data_ingestion_config.from_date,
                    end = self.data_ingestion_config.to_date,
                    periods = 2
                ).astype('str').tolist()

            else:
                intervals = pd.date_range(
                    start = self.data_ingestion_config.from_date,
                    end = self.data_ingestion_config.to_date,
                    freq = freq
                ).astype('str').tolist()

            logger.debug(f"Prepared Interval: {intervals}")
            if self.data_ingestion_config.to_date not in intervals:
                intervals.append(self.data_ingestion_config.to_date)
            return intervals
        except Exception as e:
            raise CustomerException(e,sys)

    def download_data(self, download_url: DownloadUrl):
        try:
            logger.info(f"Starting diwnload operation: {download_url}")
            
            #Creating and preparing the download directory
            download_dir = os.path.dirname(download_url.file_path)
            os.makedirs(download_dir, exist_ok = True)

            #download the data
            data = requests.get(download_url.url, params={'User-agent': f'your bot {uuid.uuid4()}'})
            try:
                logger.info(f"Started writing downloaded data into json file: {download_url.file_path}")
                
                # Saving downloaded data into hard disk
                with open(download_url.file_path, "w") as file_obj:
                    customer_complaint_data = list(
                        map(lambda x: x["_source"],
                        filter(lambda x: "_source" in x.keys(),
                        json.loads(data.content))))
                    json.dump(customer_complaint_data, file_obj)
                        
                logger.info(f"Downloaded data has been written into file: {download_url.file_path}")
            except Exception as e:
                logger.info("Failed to download, Retry Again")
                if os.path.exists(download_url.file_path):
                    os.remove(download_url.file_path)
                self.retry_download_data(data, download_url = download_url)

        except Exception as e:
            logger.info(e)
            raise CustomerException(e,sys)
    
    def retry_download_data(self, data, download_url: DownloadUrl):
        try:
             # if retry still possible try else return the response
            if download_url.n_retry == 0:
                self.failed_download_urls.append(download_url)
                logger.info(f"Unable to download file {download_url.url}")
                return
            
            # to handle throttling requestion and can be slove if we wait for some second.
            content = data.content.decode("utf-8")
            wait_second = re.findall(r'\d+', content)
            if len(wait_second) > 0:
                time.sleep(int(wait_second[0]) + 2)

            # Writing response to understand why request was failed
            failed_file_path = os.path.join(
                self.data_ingestion_config.failed_dir,
                os.path.basename(download_url.file_path))
            os.makedirs(self.data_ingestion_config.failed_dir, exist_ok=True)
            with open(failed_file_path, 'w') as file_obj:
                file_obj.write(data.content)

            # calling download function again to retry
            download_url = DownloadUrl(download_url.url, file_path=download_url.file_path,
                                       n_retry=download_url.n_retry - 1)
            self.download_data(download_url=download_url)

        except Exception as e:
            raise CustomerException(e,sys)

    def download_files(self, n_day_interval_url: int = None):
        try:
            required_interval = self.get_required_interval()
            logger.info("Started downloading files")
            for index in range(1, len(required_interval)):
                from_date, to_date = required_interval[index - 1], required_interval[index]
                logger.debug(f"Generating data download url between {from_date} and {to_date}")
                datasource_url: str = self.data_ingestion_config.datasource_url
                url = datasource_url.replace("<todate>", to_date).replace("<fromdate>", from_date)
                logger.debug(f"Url: {url}")
                file_name = f"{self.data_ingestion_config.file_name}_{from_date}_{to_date}.json"
                file_path = os.path.join(self.data_ingestion_config.download_dir, file_name)
                download_url = DownloadUrl(url=url, file_path=file_path, n_retry=self.n_retry)
                self.download_data(download_url=download_url)
            logger.info(f"File download completed")
        except Exception as e:
            raise CustomerException(e,sys)

    def convert_files_to_parquet(self) -> str:
        try:
            json_data_dir = self.data_ingestion_config.download_dir
            data_dir = self.data_ingestion_config.feature_store_dir
            os.makedirs(data_dir, exist_ok=True)
            output_file_name = self.data_ingestion_config.file_name
            file_path = os.path.join(data_dir, f"{output_file_name}")
            logger.info(f"Parquet file will be created inside: {file_path}")
            if not os.path.exists(json_data_dir):
                return file_path
            for file_name in os.listdir(json_data_dir):
                json_file_path = os.path.join(json_data_dir, file_name)
                logger.debug(f"Converting {json_file_path} into parquet format at {file_path}")
                df = spark_session.read.json(json_file_path)
                if df.count() > 0:
                    df.write.mode('append').parquet(file_path)
                return file_path
        except Exception as e:
            raise CustomerException(e,sys)

    def write_metadata(self, file_path: str) -> None:
        try:
            logger.info(f"Writing metadata info into metadata file.")
            metadata_info = DataIngestionMetadata(metadata_file_path=self.data_ingestion_config.metadata_file_path)

            metadata_info.write_metadata_info(from_date=self.data_ingestion_config.from_date,
                                              to_date=self.data_ingestion_config.to_date,
                                              data_file_path=file_path
                                              )
            logger.info(f"Metadata has been written.")
        except Exception as e:
            raise CustomerException(e,sys)

    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        try:
            logger.info(f"Started downloading json file")

            #Stop downloading same day data if already downloaded 
            if self.data_ingestion_config.from_date != self.data_ingestion_config.to_date:
                self.download_files()

            if os.path.exists(self.data_ingestion_config.download_dir):
                logger.info(f"Converting and combining downloaded json into parquet file")
                file_path = self.convert_files_to_parquet()
                self.write_metadata(file_path=file_path)

            feature_store_file_path = os.path.join(self.data_ingestion_config.feature_store_dir,
                                                   self.data_ingestion_config.file_name)

            artifact = DataIngestionArtifact(
                feature_store_file_path=feature_store_file_path,
                download_dir=self.data_ingestion_config.download_dir,
                metadata_file_path=self.data_ingestion_config.metadata_file_path,

            )

            logger.info(f"Data ingestion artifact: {artifact}")
            return artifact
        except Exception as e:
            raise CustomerException(e, sys)

def main():
    try:
        config = FinanceConfig()
        data_ingestion_config = config.get_data_ingestion_config()
        data_ingestion = DataIngestion(data_ingestion_config=data_ingestion_config, n_day_interval=6)
        data_ingestion.initiate_data_ingestion()
    except Exception as e:
        raise CustomerException(e, sys)

if __name__ == "__main__":
    try:
        main()

    except Exception as e:
        logger.exception(e)