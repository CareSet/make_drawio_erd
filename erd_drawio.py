# make_drawio_erd/erd_drawio.py

import pandas as pd
import xml.etree.ElementTree as ET
import html

class ERDGenerator:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.df.fillna('', inplace=True)
        self.tables = {}
        self.cells = {}
        self.cell_id = 2  # Starting from 2 because 0 and 1 are reserved in draw.io
        self.mxGraphModel = None
        self.root = None

    def generate_drawio_xml(self) -> str:
        self._initialize_xml()
        self._create_tables()
        xml_str = ET.tostring(self.mxGraphModel, encoding='utf-8', method='xml').decode('utf-8')
        return xml_str

    def _initialize_xml(self):
        self.mxGraphModel = ET.Element('mxGraphModel')
        diagram_attrs = {
            'dx': '1224',
            'dy': '844',
            'grid': '1',
            'gridSize': '10',
            'guides': '1',
            'tooltips': '1',
            'connect': '1',
            'arrows': '1',
            'fold': '1',
            'page': '1',
            'pageScale': '1',
            'pageWidth': '850',
            'pageHeight': '1100',
            'math': '0',
            'shadow': '0'
        }
        for key, value in diagram_attrs.items():
            self.mxGraphModel.set(key, value)
        root = ET.SubElement(self.mxGraphModel, 'root')

        # Add the first two required cells
        ET.SubElement(root, 'mxCell', {'id': '0'})
        ET.SubElement(root, 'mxCell', {'id': '1', 'parent': '0'})

        self.root = root

    def _create_tables(self):
        # Get unique combinations of Catalog, Database, and Table
        tables = self.df[['Catalog', 'Database', 'Table']].drop_duplicates()
        x_offset = 0
        y_offset = 0
        x_step = 200
        y_step = 150
        max_columns = 0

        for idx, table_row in tables.iterrows():
            catalog = table_row['Catalog']
            database = table_row['Database']
            table_name = table_row['Table']
            full_table_name = f"{catalog}.{database}.{table_name}"
            table_id = str(self.cell_id)
            self.cell_id += 1

            # Get columns for the table
            columns_df = self.df[
                (self.df['Catalog'] == catalog) &
                (self.df['Database'] == database) &
                (self.df['Table'] == table_name)
            ].sort_values('Column_Order')

            num_columns = len(columns_df)
            max_columns = max(max_columns, num_columns)

            # Create table cell (swimlane)
            table_cell = ET.SubElement(self.root, 'mxCell', {
                'id': table_id,
                'value': html.escape(full_table_name),
                'style': 'swimlane;fontStyle=1;childLayout=stackLayout;horizontal=1;startSize=30;horizontalStack=0;resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=0;',
                'vertex': '1',
                'parent': '1'
            })
            table_geometry = ET.SubElement(table_cell, 'mxGeometry', {
                'x': str(x_offset),
                'y': str(y_offset),
                'width': '180',
                'height': str(30 + num_columns * 26),  # Adjust height based on number of columns
                'as': 'geometry'
            })

            # Create column cells
            for idx2, row in columns_df.iterrows():
                column_id = str(self.cell_id)
                self.cell_id += 1

                column_name = row['Column']
                data_type = row.get('Type', '')
                column_display = f"{column_name} : {data_type}"

                # Styles: bold for primary key, underline for foreign key
                is_primary_key = int(row.get('Is_Primary_Key', 0)) == 1
                is_foreign_key = int(row.get('Is_Foreign_Key', 0)) == 1

                column_style = 'text;html=1;align=left;spacingLeft=4;'
                if is_primary_key:
                    column_style += 'fontStyle=1;'  # Bold
                if is_foreign_key:
                    column_style += 'textDecoration=underline;'

                column_cell = ET.SubElement(self.root, 'mxCell', {
                    'id': column_id,
                    'value': html.escape(column_display),
                    'style': column_style,
                    'vertex': '1',
                    'parent': table_id
                })
                column_geometry = ET.SubElement(column_cell, 'mxGeometry', {
                    'x': '0',
                    'y': str(30 + idx2 * 26),
                    'width': '180',
                    'height': '26',
                    'as': 'geometry'
                })

            # Update positions for the next table
            x_offset += x_step
            if x_offset > x_step * 3:
                x_offset = 0
                y_offset += y_step
