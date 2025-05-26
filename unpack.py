import os
import re
import zipfile
from tqdm import tqdm  # optional progress bar

# Directory containing the ZIP files
zip_dir = "/eos/cms/store/group/comm_dqm/DQMGUI_Backup/data/offline/OnlineData/original/00039xxxx"

# Local output directory for extracted ROOT files
output_dir = "/eos/cms/store/group/tsg/STEAM/savarghe/HLTpbFiles/2025"
os.makedirs(output_dir, exist_ok=True)

# Extract run number from filename
def extract_run_from_name(fname):
    match = re.search(r"R(\d{6,})", fname)
    return int(match.group(1)) if match else None

# Scan all ZIP files
zip_files = sorted(f for f in os.listdir(zip_dir) if f.endswith(".zip"))

# Get list of already extracted files
already_present = set(os.listdir(output_dir))

MIN_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB in bytes

for zipf in tqdm(zip_files, desc="Extracting HLTpb ROOTs >10MB"):
    zip_path = os.path.join(zip_dir, zipf)
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for info in zf.infolist():
                file = info.filename
                if (
                    "DQM_V0001_HLTpb_R" in file and 
                    file.endswith(".root") and 
                    info.file_size > MIN_SIZE_BYTES
                ):
                    run = extract_run_from_name(file)
                    if run and run >= 392000:
                        flat_name = os.path.basename(file)
                        if flat_name in already_present:
                            continue  # Skip if already extracted
                        temp_path = zf.extract(file, path=output_dir)
                        final_path = os.path.join(output_dir, flat_name)
                        os.rename(temp_path, final_path)
                        already_present.add(flat_name)
    except Exception as e:
        print(f"Failed to extract from {zipf}: {e}")
