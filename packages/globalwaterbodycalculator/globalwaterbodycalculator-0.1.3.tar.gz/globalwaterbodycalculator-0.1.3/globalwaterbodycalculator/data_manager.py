import urllib.request
import zipfile
from pathlib import Path
import gdown

DATA_DIR = Path("~/.globalwaterbodycalculator").expanduser()
EQUATION_FILE_ID = "1As-Mh967HDok2CcKJ7SshxOsHH7jNOe0"

EQUATION_CSV = DATA_DIR / "all_equations.csv"

def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def ensure_equation_csv():
    ensure_data_dir()
    if not EQUATION_CSV.exists():
        url = f"https://drive.google.com/uc?id={EQUATION_FILE_ID}"
        gdown.download(url, str(EQUATION_CSV), quiet=False)
    return EQUATION_CSV
