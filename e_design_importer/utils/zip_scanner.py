import os
import zipfile
import tempfile
import shutil
from io import BytesIO
from pathlib import Path
from .scanner import Scanner


class ZipScanner(Scanner):
    def __init__(self, zip_binary_data):
        super().__init__()
        self.temp_dir = None
        self.zip_data = zip_binary_data
    
    def __enter__(self):
        self.temp_dir = tempfile.mkdtemp(prefix='odoo_design_scan_')
        with zipfile.ZipFile(BytesIO(self.zip_data), 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)
        self.root_path = Path(self.temp_dir)
        return self
    
    def scan(self):
        if not self.root_path:
            raise RuntimeError("ZipScanner must be used inside a 'with' statement")
        return super().scan()
    
    def _cleanup(self):
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None
            self.root_path = None