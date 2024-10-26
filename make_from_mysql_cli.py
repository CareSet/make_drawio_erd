#!/usr/bin/env python3

import argparse
import sys
import logging
from make_drawio_erd.parsers.mysql_schema_parser import MySQLSchemaParser
from make_drawio_erd.erd_drawio import ERDGenerator

def main():
    parser = argparse.ArgumentParser(description='Generate draw.io ERD diagram from a MySQL database schema.')
    parser.add_argument('output_drawio', help='Path to the output draw.io diagram file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Increase output verbosity')
    parser.add_argument('--database-matching', help='Unix-style glob pattern to match database names')
    parser.add_argument('--table-matching', help='Unix-style glob pattern to match table names')

    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)
    logger = logging.getLogger(__name__)

    try:
        logger.info('Parsing the MySQL database schema...')
        # Parse the schema using MySQLSchemaParser
        parser_instance = MySQLSchemaParser()
        df = parser_instance.parse()

        # Apply database matching if provided
        if args.database_matching:
            logger.info(f"Filtering databases using pattern: {args.database_matching}")
            df = filter_databases_by_pattern(df, args.database_matching)

        # Apply table matching if provided
        if args.table_matching:
            logger.info(f"Filtering tables using pattern: {args.table_matching}")
            df = filter_tables_by_pattern(df, args.table_matching)

        logger.info('Generating the ERD diagram...')
        # Generate the ERD diagram using ERDGenerator
        erd_generator = ERDGenerator(df)
        drawio_xml = erd_generator.generate_drawio_xml()

        logger.info('Saving the ERD diagram to the output file...')
        # Save the XML to a file
        with open(args.output_drawio, 'w', encoding='utf-8') as f:
            f.write(drawio_xml)

        print(f"ERD diagram has been generated and saved to {args.output_drawio}")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)

def filter_databases_by_pattern(df, pattern):
    import fnmatch

    matched_databases = df['Database'].apply(lambda x: fnmatch.fnmatch(x, pattern))
    filtered_df = df[matched_databases].copy()

    if filtered_df.empty:
        raise ValueError(f"No databases match the pattern '{pattern}'.")

    return filtered_df

def filter_tables_by_pattern(df, pattern):
    import fnmatch

    matched_tables = df['Table'].apply(lambda x: fnmatch.fnmatch(x, pattern))
    filtered_df = df[matched_tables].copy()

    if filtered_df.empty:
        raise ValueError(f"No tables match the pattern '{pattern}'.")

    return filtered_df

if __name__ == "__main__":
    main()