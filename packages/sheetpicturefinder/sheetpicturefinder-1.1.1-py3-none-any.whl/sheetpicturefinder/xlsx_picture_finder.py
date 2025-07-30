# Filename: sheet-image-finder.py
# Author: Samprit Sarkar
# Created: 2025-07-04

import os
import zipfile
import tempfile
import xml.etree.ElementTree as ET
from PIL import Image
from io import BytesIO
import shutil


class XLSXPictureFinder:
    def __init__(self, xlsx_source):
        # === Configurable Constants ===
        self.NS = {
            'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
            'xdr': 'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing',
            'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
            'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
        }
        self.temp_prefix = "xlsx_images_"
        self.workbook_xml_path = 'xl/workbook.xml'
        self.worksheet_rels_dir = 'xl/worksheets/_rels'
        self.drawings_dir = 'xl/drawings'
        self.drawings_rels_dir = 'xl/drawings/_rels'
        self.media_dir = 'xl/media'

        # === Internal State ===
        self.tmp_dir = tempfile.mkdtemp(prefix=self.temp_prefix)
        self._temp_files = []
        self.image_cell_map = {}  # { sheet_name: { 'H2': 'image1.png' } }

        # === Input Handling ===
        if isinstance(xlsx_source, str):
            self.xlsx_path = xlsx_source
        elif isinstance(xlsx_source, BytesIO):
            temp_fd, temp_path = tempfile.mkstemp(suffix=".xlsx")
            with os.fdopen(temp_fd, 'wb') as f:
                f.write(xlsx_source.read())
            self.xlsx_path = temp_path
            self._temp_files.append(temp_path)
        else:
            raise ValueError("xlsx_source must be a file path or a BytesIO object")

        self._extract_and_parse()

    @staticmethod
    def _col_letter(col_num):
        letters = ''
        while col_num >= 0:
            letters = chr(col_num % 26 + ord('A')) + letters
            col_num = col_num // 26 - 1
        return letters

    def _extract_and_parse(self):
        with zipfile.ZipFile(self.xlsx_path, 'r') as zip_ref:
            zip_ref.extractall(self.tmp_dir)

        # Map sheetX.xml to actual sheet name
        workbook_xml = os.path.join(self.tmp_dir, self.workbook_xml_path)
        wb_tree = ET.parse(workbook_xml)
        wb_root = wb_tree.getroot()

        sheet_name_map = {}
        for idx, sheet in enumerate(wb_root.findall('.//main:sheets/main:sheet', self.NS), start=1):
            sheet_file = f"sheet{idx}"
            sheet_name = sheet.attrib['name']
            sheet_name_map[sheet_file] = sheet_name

        # Map drawing files to sheet names
        drawing_sheet_map = {}
        sheet_rels_path = os.path.join(self.tmp_dir, self.worksheet_rels_dir)
        if not os.path.exists(sheet_rels_path):
            return

        for file in os.listdir(sheet_rels_path):
            if not file.endswith('.rels'):
                continue
            tree = ET.parse(os.path.join(sheet_rels_path, file))
            for rel in tree.getroot():
                if 'drawing' in rel.attrib.get('Type', ''):
                    target = os.path.basename(rel.attrib['Target'])
                    sheet_file = file.replace('.xml.rels', '')
                    sheet_name = sheet_name_map.get(sheet_file)
                    if sheet_name:
                        drawing_sheet_map[target] = sheet_name

        # Parse drawings for cell-image mapping
        for drawing_file, sheet_name in drawing_sheet_map.items():
            drawing_path = os.path.join(self.tmp_dir, self.drawings_dir, drawing_file)
            drawing_rels_path = os.path.join(self.tmp_dir, self.drawings_rels_dir, drawing_file + '.rels')

            if not os.path.exists(drawing_path) or not os.path.exists(drawing_rels_path):
                continue

            # rId → image file
            rid_to_image = {}
            rel_tree = ET.parse(drawing_rels_path)
            for rel in rel_tree.getroot():
                if 'image' in rel.attrib.get('Type', ''):
                    rid = rel.attrib['Id']
                    image_file = os.path.basename(rel.attrib['Target'])
                    rid_to_image[rid] = image_file

            # anchor → cell mapping
            sheet_map = self.image_cell_map.setdefault(sheet_name, {})
            tree = ET.parse(drawing_path)
            anchors = tree.findall('.//xdr:twoCellAnchor', self.NS) or tree.findall('.//xdr:oneCellAnchor', self.NS)

            for anchor in anchors:
                from_ = anchor.find('xdr:from', self.NS)
                if from_ is None:
                    continue
                row = int(from_.find('xdr:row', self.NS).text) + 1
                col = int(from_.find('xdr:col', self.NS).text)
                cell = f"{self._col_letter(col)}{row}"

                blip = anchor.find('.//a:blip', self.NS)
                if blip is not None:
                    rid = blip.attrib.get(f"{{{self.NS['r']}}}embed")
                    image_file = rid_to_image.get(rid)
                    if image_file:
                        sheet_map[cell] = image_file

    def get_image(self, sheet_name, cell_address):
        """Load image from disk only when requested."""
        image_file = self.image_cell_map.get(sheet_name, {}).get(cell_address)
        if image_file:
            image_path = os.path.join(self.tmp_dir, self.media_dir, image_file)
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    return Image.open(BytesIO(f.read()))
        return None

    def list_image_cells(self, sheet_name):
        """Return a list of cell addresses in the given sheet that contain images."""
        return list(self.image_cell_map.get(sheet_name, {}).keys())

    def list_all_sheet_image_cells(self):
        """
        Return a dictionary of {sheet_name: [cell1, cell2, ...]} for all sheets with images.
        """
        return {
            sheet_name: list(cells.keys())
            for sheet_name, cells in self.image_cell_map.items()
            if cells
        }

    def cleanup(self):
        """Delete all temp directories and temp files."""
        shutil.rmtree(self.tmp_dir, ignore_errors=True)
        for path in self._temp_files:
            try:
                os.remove(path)
            except Exception:
                pass