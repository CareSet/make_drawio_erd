# make_drawio_erd/parsers/__init__.py

from .base_parser import BaseParser
from .metadata_csv_parser import MetaDataCSVParser
from .csv_data_parser import CSVDataParser
from .mysql_schema_parser import MySQLSchemaParser  # Include the new parser

