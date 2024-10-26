# make_drawio_erd/cli.py

import argparse
import sys
import logging
from make_drawio_erd.parsers.metadata_csv_parser import MetaDataCSVParser
from make_drawio_erd.erd_drawio import ERDGenerator

def main():
    parser = argparse.ArgumentParser(description='Generate draw.io ERD diagrams from a metadata CSV file.')
    parser.add_argument('input_csv', help='Path to the input metadata CSV file')
    parser.add_argument('output_drawio', help='Path to the output draw.io diagram file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Increase output verbosity')

    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)
    logger = logging.getLogger(__name__)

    try:
        logger.info('Parsing the CSV file...')
        # Parse the CSV file
        csv_parser = MetaDataCSVParser(args.input_csv)
        df = csv_parser.parse()

        logger.info('Generating the ERD diagram...')
        # Generate the ERD diagram
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
