import os
import shutil

src_dir = "/eos/cms/store/group/tsg/STEAM/savarghe/HLTpbFiles/2025"
dest_dir = "/eos/cms/store/group/tsg/STEAM/savarghe/HLTpbFiles/2024_25"

# Ensure destination exists
os.makedirs(dest_dir, exist_ok=True)

# Get all ROOT files in source directory
for filename in os.listdir(src_dir):
    if not filename.startswith("DQM_V0001_HLTpb_") or not filename.endswith(".root"):
        continue

    src_file = os.path.join(src_dir, filename)
    dest_file = os.path.join(dest_dir, filename)

    if not os.path.exists(dest_file):
        print(f"Copying {filename}")
        shutil.copy2(src_file, dest_file)
    else:
        continue
    #     print(f"Already exists: {filename}")
