from pathlib import Path
from .scanner import Scanner


class FolderScanner(Scanner):
    def __init__(self, root_path):
        super().__init__()
        self.root_path = Path(root_path)
    
    def _cleanup(self):
        pass