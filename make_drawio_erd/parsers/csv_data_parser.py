# make_drawio_erd/parsers/csv_data_parser.py

import pandas as pd
import os
from .base_parser import BaseParser

class CSVDataParser(BaseParser):
    def __init__(self, file_path: str, sample_size: int = 10000):
        self.file_path = file_path
        self.sample_size = sample_size

    def parse(self) -> pd.DataFrame:
        # Use the base name of the file (including extension) as the table name
        table_name = os.path.basename(self.file_path)
        # Do not remove the extension
        # table_name = os.path.splitext(table_name)[0]

        # Read the first 'sample_size' rows of the CSV file
        df = pd.read_csv(self.file_path, nrows=self.sample_size, dtype=str)
        column_names = df.columns.tolist()

        # Initialize lists to store metadata
        catalogs = []
        databases = []
        tables = []
        columns = []
        types = []
        column_orders = []
        is_primary_keys = []
        is_foreign_keys = []

        # Infer data types for each column
        for idx, col in enumerate(column_names):
            col_data = df[col].dropna()
            inferred_type = 'VARCHAR'  # Default type
            if not col_data.empty:
                if col_data.apply(self.is_integer).all():
                    inferred_type = 'INT'
                elif col_data.apply(self.is_decimal).all():
                    inferred_type = 'DECIMAL'

            # Append metadata for each column
            catalogs.append('')  # Assuming no catalog
            databases.append('')  # Assuming no database
            tables.append(table_name)
            columns.append(col)
            types.append(inferred_type)
            column_orders.append(idx + 1)  # Column order starts from 1
            is_primary_keys.append(0)  # Default to not a primary key
            is_foreign_keys.append(0)  # Default to not a foreign key

        # Construct the DataFrame expected by ERDGenerator
        metadata_df = pd.DataFrame({
            'Catalog': catalogs,
            'Database': databases,
            'Table': tables,
            'Owner': '',  # No owner information
            'Creation_Date': '',  # No creation date information
            'Column': columns,
            'Type': types,
            'Column_Order': column_orders,
            'Source_Table': '',  # No source table information
            'Is_Primary_Key': is_primary_keys,
            'Is_Foreign_Key': is_foreign_keys
        })

        return metadata_df

    @staticmethod
    def is_integer(value):
        try:
            if '.' in value:
                return False
            int(value)
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def is_decimal(value):
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
