import os,sys
from finpred.logger import logger
from finpred.exception import CustomerException
from finpred.utils import read_yaml_file, write_yaml_file
from collections import namedtuple

DataIngestionMetadataInfo = namedtuple("DataIngestionMetadataInfo" , ["from_date", "to_date", "data_file_path"])


class DataIngestionMetadata:
    def __init__(self, metadata_file_path):
        self.metadata_file_path = metadata_file_path


    @property
    def is_metadata_file_present(self):
        return os.path.exists(self.metadata_file_path)

    def write_metadata_info(self, from_date: str, to_date: str, data_file_path: str):
        try:
            metadata_info = DataIngestionMetadataInfo(
                from_date = from_date, to_date = to_date, 
                data_file_path = data_file_path
            )
            write_yaml_file(file_path = self.metadata_file_path, 
                    data = metadata_info._asdict())
        except Exception as e:
            raise CustomerException(e, sys)

    def get_metadata_info(self) -> DataIngestionMetadataInfo:
        try:
            if not self.is_metadata_file_present:
                raise Exception("No metadata file present")
            metadata = read_yaml_file(self.metadata_file_path)
            metadata_info = DataIngestionMetadataInfo(**(metadata))
            logger.info(metadata)
            return metadata_info
        except Exception as e:
            raise CustomerException(e, sys)
