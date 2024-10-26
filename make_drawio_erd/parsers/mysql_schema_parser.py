# make_drawio_erd/parsers/mysql_schema_parser.py

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from dotenv import load_dotenv
import os
from .base_parser import BaseParser

class MySQLSchemaParser(BaseParser):
    def __init__(self):
        self.engine = self._create_engine()

    def _create_engine(self) -> Engine:
        # Load environment variables from .env file
        load_dotenv()

        # Get MySQL connection details from environment variables
        mysql_host = os.getenv('MYSQL_HOST', 'localhost')
        mysql_port = os.getenv('MYSQL_PORT', '3306')
        mysql_user = os.getenv('MYSQL_USER')
        mysql_password = os.getenv('MYSQL_PASSWORD')

        if not all([mysql_user, mysql_password]):
            raise ValueError("MySQL credentials are not fully set in the .env file.")

        # Create the SQLAlchemy engine without specifying a default database
        connection_string = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/"
        engine = create_engine(connection_string)
        return engine

    def parse(self) -> pd.DataFrame:
        # Query to get column information from all databases except system databases
        query = """
        SELECT
            C.TABLE_SCHEMA AS `Database`,
            C.TABLE_NAME AS `Table`,
            C.COLUMN_NAME AS `Column`,
            C.DATA_TYPE AS `Type`,
            C.ORDINAL_POSITION AS `Column_Order`,
            CASE WHEN KCU.CONSTRAINT_NAME = 'PRIMARY' THEN 1 ELSE 0 END AS `Is_Primary_Key`,
            CASE WHEN KCU.REFERENCED_TABLE_NAME IS NOT NULL THEN 1 ELSE 0 END AS `Is_Foreign_Key`
        FROM
            information_schema.COLUMNS C
            LEFT JOIN information_schema.KEY_COLUMN_USAGE KCU
                ON C.TABLE_SCHEMA = KCU.TABLE_SCHEMA
                AND C.TABLE_NAME = KCU.TABLE_NAME
                AND C.COLUMN_NAME = KCU.COLUMN_NAME
        WHERE
            C.TABLE_SCHEMA NOT IN ('information_schema', 'mysql', 'performance_schema', 'sys')
        ORDER BY
            C.TABLE_SCHEMA, C.TABLE_NAME, C.ORDINAL_POSITION;
        """

        df = pd.read_sql(query, self.engine)

        # Construct the DataFrame expected by ERDGenerator
        metadata_df = pd.DataFrame({
            'Catalog': '',  # MySQL does not use catalogs
            'Database': df['Database'],
            'Table': df['Table'],
            'Owner': '',  # Owner information not available
            'Creation_Date': '',  # Creation date not available
            'Column': df['Column'],
            'Type': df['Type'],
            'Column_Order': df['Column_Order'],
            'Source_Table': '',  # No source table information
            'Is_Primary_Key': df['Is_Primary_Key'],
            'Is_Foreign_Key': df['Is_Foreign_Key']
        })

        return metadata_df
