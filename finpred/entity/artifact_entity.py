from collections import namedtuple

DataIngestionArtifact = namedtuple("DataIngestionArtifact",
                                   ["feature_store_file_path", "metadata_file_path", "download_dir"])