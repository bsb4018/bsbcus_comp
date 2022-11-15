import os,sys
from finpred.logger import logger
from finpred.exception import CustomerException
from finpred.utils import read_yaml_file, write_yaml_file
from collections import namedtuple

DataIngestionMetadataInfo = namedtuple("DataIngestionMetadataInfo" , ["from_date", "to_date", "data_file_path"])


class DataIngestionMetadata:
    def __init__(self, metadata_file_path):
        self.metadata_file_path = metadata_file_path

    def write_metadata_info(self, from_date: str, to_date: str, data_file_path: str):
        try:
            pass
        except Exception as e:
            raise CustomerException(e, sys)

    def get_metadata_info(self) -> DataIngestionMetadataInfo:
        try:
            pass
        except Exception as e:
            raise CustomerException(e, sys)
