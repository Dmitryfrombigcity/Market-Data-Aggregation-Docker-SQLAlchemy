import subprocess
import sys
from pathlib import Path

from src.utils import start_db

with start_db():
    path_to_dash = Path('.') / 'src' / 'dash' / 'dash_plotly.py'
    subprocess.run([
        sys.executable, path_to_dash],
    )
